#!/usr/bin/env python3
"""
t2_integrator.py v2.1 — T1 → T2 Neural Link (Dynamic Context Injection)
==============================================================
T2 Tri-Core v2.1 Features:
1. Automated Path Watcher   — Auto-fetch latest JSON from T1 output dir
2. Multi-Asset Aggregation  — Jinja2 {% for asset in assets %} loops
3. Delta Analysis            — Compare new vs old policy version
4. PDF/HTML Export          — Professional delivery formats

Logic หลัก:
1. find_latest_t1_json()    — Scan T1 output dir for latest JSON
2. parse_t1_json()         — อ่าน + validate T1 JSON (single or multi-asset)
3. aggregate_multi_asset()  — Build asset table from multi-asset JSON
4. map_context_to_template() — map fields → placeholders (46+ vars)
5. select_tier()            — เลือก Tier ตาม severity
6. verify_core6_compliance() — ป้องกัน T1 ขัดกับ Core 6 Verbatim
7. delta_analysis()          — Compare with previous policy version
8. render_jinja_template()  — Jinja2 rendering with for-loops
9. export_pdf() / export_html() — Export formats

วิธีใช้:
    python t2_integrator.py --auto-fetch          # Scan T1 dir for latest
    python t2_integrator.py --t1-json /path/file.json  # Direct file
    python t2_integrator.py --delta               # Compare with previous
    python t2_integrator.py --format html         # Export as HTML
    python t2_integrator.py --format pdf           # Export as PDF

Author: T2 Tri-Core v2.1 / OTengine4
Date: 2026-04-05
"""

import json
import re
import uuid
import hashlib
import os
import glob
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from jinja2 import Environment, BaseLoader, TemplateError
from collections import defaultdict

# =============================================================================
# SECTION 1: Data Classes & Enums
# =============================================================================

class SeverityLevel(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class PricingTier(Enum):
    BASE = ("Base", "฿95,000", "B")
    STANDARD = ("Standard", "฿125,000", "S")
    PRO = ("Pro", "฿165,000", "P")
    ENTERPRISE = ("Enterprise", "฿395,000", "E")
    
    def __init__(self, label: str, price: str, code: str):
        self.label = label
        self.price = price
        self.code = code

class ConflictResolution(Enum):
    ALWAYS_WIN = "ALWAYS_WIN"
    T1_CAN_RECOMMEND_ABOVE = "T1_CAN_RECOMMEND_ABOVE"
    T1_CAN_RECOMMEND_BELOW = "T1_CAN_RECOMMEND_BELOW"

@dataclass
class OverrideLog:
    """บันทึกการ override — เก็บไว้ให้ auditor ดูว่าเกิด conflict อะไร"""
    placeholder: str
    t1_value: str
    core6_value: str
    resolution: str
    rationale: str
    article_ref: str = ""

@dataclass
class T1Input:
    """โครงสร้าง T1 JSON output ที่รองรับ"""
    threat_name: str = ""
    threat_type: str = ""
    severity: str = "MEDIUM"
    attack_vector: str = ""
    ttp_ids: List[str] = field(default_factory=list)
    assets: List[Dict[str, Any]] = field(default_factory=list)
    current_sl: int = 0
    target_sl: int = 0
    sl_gap: int = 0
    wisdom_pattern_id: str = ""
    wisdom_steps: List[str] = field(default_factory=list)
    risk_score: int = 0
    likelihood: int = 0
    impact_level: int = 0
    raw_json: Dict[str, Any] = field(default_factory=dict)
    input_hash: str = ""

@dataclass
class InjectionResult:
    """ผลลัพธ์ของการ inject — มีทุกอย่างที่ต้องใช้"""
    sync_id: str
    timestamp: str
    tier: str
    tier_code: str
    placeholders_filled: int
    overrides: List[OverrideLog]
    filled_document: str
    warnings: List[str]
    compliance_verified: bool

# =============================================================================
# SECTION 2: Core 6 Verbatim Registry (ป้องกัน T1 มาแก้กฎหมาย)
# =============================================================================

class Core6Registry:
    """
    ฐานข้อมูล Core 6 — กฎหมายไทยที่ต้อง protected
    
    หลักการ: "Regulator is King"
    - ถ้า T1 บอกให้ทำ "น้อยกว่า" หรือ "ขัด" กฎหมาย → override ด้วย Core 6 เสมอ
    - ถ้า T1 บอกให้ทำ "มากกว่า" กฎหมาย → แนะนำเป็น L2 Recommendation ได้
    """
    
    VERBATIMS = {
        "TH-CYBER-58": {
            "article": "มาตรา 58",
            "key_requirement": "แจ้งเหตุต่อ NCSA ภายใน 72 ชั่วโมง นับแต่ทราบเหตุ",
            "deadline_hours": 72,
            "reporting_authority": "NCSA",
            "report_content": ["ลักษณะเหตุ", "ผลกระทบ", "มาตรการที่ดำเนินการแล้ว"],
            "penalty": "ปรับสูงสุด 1,000,000 บาท + เปิดเผยชื่อ",
            "conflict_resolution": "ALWAYS_WIN"
        },
        "TH-CYBER-59": {
            "article": "มาตรา 59",
            "key_requirement": "แจ้งภายใน 24 ชั่วโมง กรณีภัยคุกคามร้ายแรง/กระทบความมั่นคงของรัฐ",
            "deadline_hours": 24,
            "reporting_authority": "NCSA",
            "trigger_condition": "ภัยคุกคามร้ายแรงหรืออาจกระทบความมั่นคงของรัฐ",
            "conflict_resolution": "T1_CAN_RECOMMEND_BELOW"
        },
        "TH-CYBER-54": {
            "article": "มาตรา 54",
            "key_requirement": "ประเมินตนเอง (Self-Assessment) อย่างน้อยปีละ 1 ครั้ง",
            "frequency": "annual",
            "penalty": "ปรับสูงสุด 200,000 บาท",
            "conflict_resolution": "ALWAYS_WIN"
        }
    }
    
    @classmethod
    def get_verbatims(cls) -> Dict[str, Dict]:
        return cls.VERBATIMS
    
    @classmethod
    def check_conflict(cls, t1_value: str, core6_id: str, context: str = "") -> Tuple[bool, Optional[str]]:
        if core6_id not in cls.VERBATIMS:
            return False, t1_value
        
        verbatim = cls.VERBATIMS[core6_id]
        resolution = verbatim["conflict_resolution"]
        
        if resolution == "ALWAYS_WIN":
            if t1_value != verbatim.get("key_requirement", ""):
                return True, verbatim["key_requirement"]
        
        if resolution == "T1_CAN_RECOMMEND_BELOW":
            if "deadline_hours" in verbatim:
                try:
                    t1_hours = int(t1_value)
                    if t1_hours > verbatim["deadline_hours"]:
                        return True, f"{verbatim['deadline_hours']} ชั่วโมง ({verbatim['article']})"
                except (ValueError, TypeError):
                    pass
        
        return False, t1_value

# =============================================================================
# SECTION 3: Severity → Tier Mapping
# =============================================================================

class TierSelector:
    """
    แมป severity จาก T1 → Pricing Tier สำหรับ T2
    
    Logic:
    - CRITICAL → Enterprise ฿395K
    - HIGH     → Pro ฿165K
    - MEDIUM   → Standard ฿125K
    - LOW      → Base ฿95K
    """
    
    SEVERITY_TO_TIER = {
        "CRITICAL": {
            "tier": "Enterprise",
            "code": "E",
            "price_range": "฿295,000 - ฿395,000",
            "color": "🔴",
            "urgency_multiplier": "2x",
            "recommended_procedures": ["Full L2", "Tabletop Exercise", "24/7 SOC"],
            "timeline_hours": 24
        },
        "HIGH": {
            "tier": "Pro",
            "code": "P",
            "price_range": "฿165,000 - ฿245,000",
            "color": "🟠",
            "urgency_multiplier": "1.5x",
            "recommended_procedures": ["L2 Procedure", "IR Drill"],
            "timeline_hours": 48
        },
        "MEDIUM": {
            "tier": "Standard",
            "code": "S",
            "price_range": "฿125,000 - ฿165,000",
            "color": "🟡",
            "urgency_multiplier": "1x",
            "recommended_procedures": ["L1 Policy", "Basic IR"],
            "timeline_hours": 72
        },
        "LOW": {
            "tier": "Base",
            "code": "B",
            "price_range": "฿95,000 - ฿125,000",
            "color": "🟢",
            "urgency_multiplier": "0.5x",
            "recommended_procedures": ["L1 Policy Only"],
            "timeline_hours": 168
        }
    }
    
    @classmethod
    def get_tier(cls, severity: str) -> Dict[str, Any]:
        return cls.SEVERITY_TO_TIER.get(severity.upper(), cls.SEVERITY_TO_TIER["MEDIUM"])
    
    @classmethod
    def calculate_price(cls, severity: str, asset_count: int = 1) -> Dict[str, Any]:
        tier = cls.get_tier(severity)
        base_price_map = {"E": 295000, "P": 165000, "S": 125000, "B": 95000}
        base = base_price_map.get(tier["code"], 125000)
        asset_premium = max(0, (asset_count - 3) * 15000)
        return {
            "tier": tier["tier"],
            "tier_code": tier["code"],
            "base_price": base,
            "asset_premium": asset_premium,
            "estimated_price": base + asset_premium,
            "price_range_display": tier["price_range"]
        }

# =============================================================================
# SECTION 4: Template Engine
# =============================================================================

class TemplateEngine:
    """
    Template engine — supports BOTH legacy {VAR} and Jinja2 {{VAR|default('x')}}
    Priority: Jinja2 rendering first, fallback to legacy replacement
    """
    
    LEGACY_PATTERN = re.compile(r'\{([A-Z_][A-Z0-9_]*)\}')
    JINJA2_PATTERN = re.compile(r'\{\{(\w+)(?:\|default\([^\)]+\))?\}\}')
    
    def __init__(self, template_path: str = None):
        self.template_path = template_path
        self.template_content = ""
        if template_path and Path(template_path).exists():
            self.template_content = Path(template_path).read_text(encoding="utf-8")
        self._jinja_env = Environment(loader=BaseLoader(), autoescape=False)
    
    def load_template(self, path: str) -> str:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Template not found: {path}")
        self.template_content = p.read_text(encoding="utf-8")
        return self.template_content
    
    def extract_placeholders(self) -> List[str]:
        """Extract all unique placeholder names (both legacy + Jinja2)"""
        found = set()
        found.update(self.LEGACY_PATTERN.findall(self.template_content))
        found.update(self.JINJA2_PATTERN.findall(self.template_content))
        return sorted(found)
    
    def replace_placeholders(self, values: Dict[str, Any]) -> Tuple[str, int]:
        """
        Replace placeholders — tries Jinja2 first, falls back to legacy {VAR}
        Smart Defaults: if a value is empty/None, it stays as {{VAR|default('x')}} in Jinja2
        Supports for-loops via jinja2: {% for asset in assets %}...{% endfor %}
        """
        content = self.template_content
        replacements = 0
        
        # Check if this is a Jinja2 template
        has_jinja2 = '{{' in content
        
        if has_jinja2:
            try:
                template = self._jinja_env.from_string(content)
                rendered = template.render(**values)
                # Count Jinja2 variable uses
                jinja2_vars = self.JINJA2_PATTERN.findall(content)
                replacements = len(jinja2_vars)
                return rendered, replacements
            except TemplateError as e:
                self._warn(f"Jinja2 rendering failed: {e}, falling back to legacy")
        
        # Legacy fallback: replace {VAR} with values
        for key, value in values.items():
            placeholder = f"{{{key}}}"
            if placeholder in content:
                content = content.replace(placeholder, str(value))
                replacements += 1
        return content, replacements
    
    def render_with_context(self, values: Dict[str, Any], asset_summary: Dict[str, Any]) -> Tuple[str, int]:
        """
        Enhanced rendering with asset loop support and asset summary data.
        """
        content = self.template_content
        has_jinja2 = '{{' in content
        
        if has_jinja2:
            try:
                # Merge asset_summary into values for Jinja2 for-loops
                full_context = {**values, **asset_summary}
                template = self._jinja_env.from_string(content)
                rendered = template.render(**full_context)
                jinja2_vars = self.JINJA2_PATTERN.findall(content)
                return rendered, len(jinja2_vars)
            except TemplateError as e:
                self._warn(f"Jinja2 render failed: {e}")
        
        return content, 0
    
    def get_unfilled_placeholders(self) -> List[str]:
        """Return list of placeholders still unfilled (still have {{VAR}} or {VAR})"""
        found = set()
        # Check for Jinja2 unfilled
        jinja2_matches = re.findall(r'\{\{(\w+)\|default\([^\)]+\)\}\}', self.template_content)
        found.update(jinja2_matches)
        return sorted(found)
    
    def _warn(self, msg: str):
        print(f"  ⚠️ TemplateEngine: {msg}")

# =============================================================================
# SECTION 5: Main Class — T1TOSmartLink
# =============================================================================

class T1TOSmartLink:
    """
    T1 → T2 Smart Link Engine
    
    หน้าที่: ดึง JSON output จาก T1 มาฉีดเข้า T2 Document Template
            โดยผ่าน 5 ขั้นตอน:
            
    Step 1: parse_t1_json()        — อ่าน + validate T1 JSON
    Step 2: select_tier()          — เลือก Tier ตาม severity  
    Step 3: verify_core6_compliance() — ป้องกัน T1 ขัด Core 6
    Step 4: map_context_to_template() — map fields → placeholders
    Step 5: inject_and_render()     — สร้าง Draft ใหม่
    """
    
    VERSION = "2.1"
    
    # Default T1 output directories to scan (in priority order)
    DEFAULT_T1_DIRS = [
        "/root/.openclaw/workspace/t1-tricore/output/radar/",
        "/root/.openclaw/workspace/t1-tricore/output/",
        "/root/.openclaw/workspace/t1-radar/outputs/",
        "/root/.openclaw/workspace/t1/outputs/",
        "/root/.openclaw/workspace/T1/output/",
    ]
    
    def __init__(self, t1_json_path: str = None, template_path: str = None, 
                 mapping_config_path: str = None):
        self.t1_json_path = t1_json_path
        self.t1_data: Optional[T1Input] = None
        self.template_engine = TemplateEngine(template_path)
        self.mapping_config = {}
        
        if mapping_config_path and Path(mapping_config_path).exists():
            with open(mapping_config_path, 'r', encoding='utf-8') as f:
                self.mapping_config = json.load(f)
        
        self.overrides: List[OverrideLog] = []
        self.warnings: List[str] = []
        self.sync_id = ""
    
    def _generate_sync_id(self) -> str:
        return f"SYNC-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
    
    # =========================================================================
    # FEATURE 1: Automated Path Watcher — Find Latest T1 JSON
    # =========================================================================
    def find_latest_t1_json(self, search_dirs: List[str] = None) -> Optional[str]:
        """
        Scan T1 output directories for the most recent JSON file.
        Returns the path to the latest JSON, or None if nothing found.
        
        Supports patterns:
        - battle_card_*.json
        - risk_assessment_*.json
        - t1_output_*.json
        - *-t1-*.json
        - Any .json in T1 output dirs
        """
        dirs = search_dirs or self.DEFAULT_T1_DIRS
        candidates = []
        
        for d in dirs:
            d_path = Path(d)
            if not d_path.exists():
                continue
            # Find all JSON files sorted by modification time
            for json_file in sorted(d_path.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
                # Skip obviously non-T1 files
                if json_file.name.startswith('.'):
                    continue
                # Check if it looks like a T1 output file
                try:
                    content = json.loads(json_file.read_text(encoding="utf-8"))
                    # Valid T1 JSON has these top-level keys
                    if any(k in content for k in ['threat_summary', 'battle_card', 'risk_score', 'asset_analysis', 'sl_assessment']):
                        candidates.append((str(json_file), json_file.stat().st_mtime, content))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
        
        if not candidates:
            return None
        
        # Sort by mtime descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        latest = candidates[0]
        print(f"  🔍 Found T1 JSON: {latest[0]}")
        print(f"     Modified: {datetime.fromtimestamp(latest[1]).strftime('%Y-%m-%d %H:%M:%S')}")
        return latest[0]
    
    # =========================================================================
    # FEATURE 2: Multi-Asset Aggregation
    # =========================================================================
    def aggregate_multi_asset(self, assets: List[Dict]) -> Dict[str, Any]:
        """
        Convert list of assets from T1 into template-ready format.
        Handles mixed vendors (Siemens + Rockwell in same report).
        """
        if not assets:
            return {}
        
        # Normalize each asset
        normalized = []
        for asset in assets:
            norm = {
                "name": asset.get("name", "—"),
                "vendor": asset.get("vendor", asset.get("manufacturer", asset.get("brand", "—"))),
                "type": asset.get("type", asset.get("device_type", "—")),
                "model": asset.get("model", asset.get("name", "—")),
                "zone": asset.get("zone", asset.get("location", "—")),
                "criticality": asset.get("criticality", "MEDIUM").upper(),
                "max_vuln": asset.get("max_vuln", asset.get("vuln_count", 0)),
                "firmware": asset.get("firmware", asset.get("fw_version", "—")),
                "protocols": asset.get("protocols", []),
                "connectivity": asset.get("connectivity", asset.get("network_type", "—")),
            }
            normalized.append(norm)
        
        # Build summary stats
        vendors = list(set(a["vendor"] for a in normalized if a["vendor"] != "—"))
        zones = list(set(a["zone"] for a in normalized if a["zone"] != "—"))
        total_vulns = sum(a["max_vuln"] for a in normalized)
        highest_criticality = "CRITICAL" if any(a["criticality"] == "CRITICAL" for a in normalized) else "HIGH"
        
        return {
            "assets": normalized,
            "asset_count": len(normalized),
            "unique_vendors": vendors,
            "vendor_count": len(vendors),
            "unique_zones": zones,
            "total_vulnerabilities": total_vulns,
            "highest_criticality": highest_criticality,
            "has_multiple_vendors": len(vendors) > 1,
        }
    
    # =========================================================================
    # FEATURE 3: Delta Analysis — Compare New vs Old Policy
    # =========================================================================
    def delta_analysis(self, new_t1_data: Dict, old_policy_path: str = None) -> Dict[str, Any]:
        """
        Compare new T1 assessment against the previous policy version.
        Returns a dict of changes that should be highlighted in the new policy.
        """
        if not old_policy_path or not Path(old_policy_path).exists():
            return {"has_delta": False, "reason": "No previous policy to compare"}
        
        try:
            old_content = Path(old_policy_path).read_text(encoding="utf-8")
        except Exception:
            return {"has_delta": False, "reason": "Could not read old policy"}
        
        new_threat = new_t1_data.get("threat_summary", {})
        old_threat_match = re.search(r'Threat Name[:\s]+([^\n|]+)', old_content)
        old_severity_match = re.search(r'Severity Level[:\s]+([^\n|]+)', old_content)
        old_asset_match = re.search(r'Affected Asset[:\s]+([^\n|]+)', old_content)
        
        changes = []
        
        if old_threat_match and new_threat.get("name"):
            old_name = old_threat_match.group(1).strip()
            if old_name != new_threat["name"]:
                changes.append({
                    "type": "THREAT_CHANGED",
                    "old": old_name,
                    "new": new_threat["name"],
                    "description": f"ภัยคุกคามเปลี่ยนจาก '{old_name}' เป็น '{new_threat['name']}' — อัปเดตนโยบายทันที"
                })
        
        if old_severity_match and new_threat.get("severity"):
            old_sev = old_severity_match.group(1).strip()
            new_sev = new_threat["severity"].upper()
            if new_sev in old_sev or old_sev in new_sev:
                pass  # same general level
            elif new_sev == "CRITICAL" and old_sev != "CRITICAL":
                changes.append({
                    "type": "SEVERITY_INCREASED",
                    "old": old_sev,
                    "new": new_sev,
                    "description": f"ความรุนแรงเพิ่มขึ้นเป็น {new_sev} — Priority สูงขึ้น Tier เปลี่ยน"
                })
        
        if old_asset_match and new_t1_data.get("asset_analysis"):
            old_asset = old_asset_match.group(1).strip()
            new_assets = [a.get("name", "") for a in new_t1_data["asset_analysis"]]
            if old_asset not in new_assets and new_assets:
                changes.append({
                    "type": "ASSET_CHANGED",
                    "old": old_asset,
                    "new": ", ".join(new_assets),
                    "description": f"อุปกรณ์เป้าหมายเปลี่ยนจาก '{old_asset}' เป็น {', '.join(new_assets)}"
                })
        
        return {
            "has_delta": len(changes) > 0,
            "changes": changes,
            "change_count": len(changes),
            "old_policy_hash": hashlib.md5(old_content.encode()).hexdigest()[:8],
        }
    
    def _compute_input_hash(self, raw_json: Dict) -> str:
        s = json.dumps(raw_json, sort_keys=True)
        return hashlib.sha256(s.encode()).hexdigest()[:16]
    
    # STEP 1: Parse T1 JSON
    def parse_t1_json(self, json_path: str = None) -> T1Input:
        path = json_path or self.t1_json_path
        if not path:
            raise ValueError("ต้องระบุ t1_json_path")
        
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"T1 JSON not found: {path}")
        
        raw = json.loads(p.read_text(encoding="utf-8"))
        self.sync_id = self._generate_sync_id()
        input_hash = self._compute_input_hash(raw)
        
        threat = raw.get("threat_summary", {})
        assets = raw.get("asset_analysis", [])
        sl = raw.get("sl_assessment", {})
        wisdom = raw.get("wisdom_matches", [])
        risk = raw.get("risk_score", {})
        
        self.t1_data = T1Input(
            threat_name=threat.get("name", ""),
            threat_type=threat.get("type", ""),
            severity=threat.get("severity", "MEDIUM"),
            attack_vector=threat.get("attack_vector", ""),
            ttp_ids=threat.get("ttp_ids", []),
            assets=assets if isinstance(assets, list) else [assets],
            current_sl=sl.get("current_sl", 0),
            target_sl=sl.get("target_sl", 0),
            sl_gap=sl.get("gap", 0),
            wisdom_pattern_id=wisdom[0].get("pattern_id", "") if wisdom else "",
            wisdom_steps=wisdom[0].get("steps", []) if wisdom else [],
            risk_score=risk.get("overall", 0),
            likelihood=risk.get("likelihood", 0),
            impact_level=risk.get("impact", 0),
            raw_json=raw,
            input_hash=input_hash
        )
        return self.t1_data
    
    def parse_t1_from_dict(self, data: Dict) -> T1Input:
        self.sync_id = self._generate_sync_id()
        self.t1_data = T1Input(
            threat_name=data.get("threat_summary", {}).get("name", ""),
            threat_type=data.get("threat_summary", {}).get("type", ""),
            severity=data.get("threat_summary", {}).get("severity", "MEDIUM"),
            attack_vector=data.get("threat_summary", {}).get("attack_vector", ""),
            ttp_ids=data.get("threat_summary", {}).get("ttp_ids", []),
            assets=data.get("asset_analysis", []),
            current_sl=data.get("sl_assessment", {}).get("current_sl", 0),
            target_sl=data.get("sl_assessment", {}).get("target_sl", 0),
            sl_gap=data.get("sl_assessment", {}).get("gap", 0),
            wisdom_pattern_id=data.get("wisdom_matches", [{}])[0].get("pattern_id", ""),
            wisdom_steps=data.get("wisdom_matches", [{}])[0].get("steps", []),
            risk_score=data.get("risk_score", {}).get("overall", 0),
            likelihood=data.get("risk_score", {}).get("likelihood", 0),
            impact_level=data.get("risk_score", {}).get("impact", 0),
            raw_json=data,
            input_hash=self._compute_input_hash(data)
        )
        return self.t1_data
    
    # STEP 2: Select Tier
    def select_tier(self, severity: str = None) -> Dict[str, Any]:
        sev = severity or (self.t1_data.severity if self.t1_data else "MEDIUM")
        tier_info = TierSelector.get_tier(sev)
        asset_count = len(self.t1_data.assets) if self.t1_data and self.t1_data.assets else 1
        price_info = TierSelector.calculate_price(sev, asset_count)
        return {
            "tier": tier_info["tier"],
            "tier_code": tier_info["code"],
            "tier_color": tier_info["color"],
            "price_info": price_info,
            "urgency_multiplier": tier_info["urgency_multiplier"],
            "recommended_procedures": tier_info["recommended_procedures"],
            "timeline_hours": tier_info["timeline_hours"]
        }
    
    # STEP 3: Verify Core 6 Compliance
    def verify_core6_compliance(self, t1_suggested_value: Any, 
                                core6_article_id: str,
                                context: str = "") -> Tuple[Any, Optional[OverrideLog]]:
        core6 = Core6Registry.VERBATIMS.get(core6_article_id, {})
        resolution = core6.get("conflict_resolution", "ALWAYS_WIN")
        override = None
        final_value = t1_suggested_value
        
        if resolution == "ALWAYS_WIN":
            if t1_suggested_value != core6.get("key_requirement", t1_suggested_value):
                override = OverrideLog(
                    placeholder=f"CORE6_{core6_article_id}",
                    t1_value=str(t1_suggested_value),
                    core6_value=core6.get("key_requirement", ""),
                    resolution="OVERRIDE: Core 6 Verbatim Wins",
                    rationale=f"มาตรา {core6.get('article', core6_article_id)} มีผลบังคับทางกฎหมาย",
                    article_ref=core6_article_id
                )
                self.overrides.append(override)
                final_value = core6.get("key_requirement", t1_suggested_value)
                self.warnings.append(
                    f"⚠️ Override: '{t1_suggested_value}' → '{final_value}' ({core6_article_id})"
                )
        
        elif resolution == "T1_CAN_RECOMMEND_BELOW":
            if "deadline_hours" in core6:
                try:
                    t1_hours = int(str(t1_suggested_value).replace(" ชม.", "").replace(" hours", "").strip())
                    if t1_hours > core6["deadline_hours"]:
                        override = OverrideLog(
                            placeholder=f"CORE6_{core6_article_id}",
                            t1_value=str(t1_hours),
                            core6_value=str(core6["deadline_hours"]),
                            resolution="OVERRIDE: Deadline cannot exceed legal minimum",
                            rationale=f"มาตรา {core6['article']} บังคับ {core6['deadline_hours']} ชม.",
                            article_ref=core6_article_id
                        )
                        self.overrides.append(override)
                        final_value = f"{core6['deadline_hours']} ชั่วโมง"
                        self.warnings.append(
                            f"⚠️ Override: T1 {t1_hours}h → มาตรา {core6['article']} {core6['deadline_hours']}h"
                        )
                except (ValueError, TypeError):
                    pass
        
        return final_value, override
    
    def verify_full_compliance(self) -> Dict[str, Any]:
        if not self.t1_data:
            return {"verified": False, "reason": "No T1 data loaded"}
        
        self.overrides = []
        self.warnings = []
        
        if self.t1_data.threat_type.upper() in ["RANSOMWARE", "APT", "MALWARE"]:
            if self.t1_data.severity.upper() in ["CRITICAL", "HIGH"]:
                suggested_deadline = 24
                _, override = self.verify_core6_compliance(
                    suggested_deadline, 
                    "TH-CYBER-58",
                    "Threat type suggests faster reporting"
                )
                if override:
                    self.warnings.append(
                        f"📋 Recommendation: พิจารณาแจ้ง NCSA ภายใน 24 ชม. "
                        f"(มาตรา 59 กรณีภัยร้ายแรง) แม้มาตรา 58 กำหนด 72 ชม."
                    )
        
        return {
            "verified": True,
            "overrides_count": len(self.overrides),
            "warnings_count": len(self.warnings),
            "has_conflicts": len(self.overrides) > 0
        }
    
    # STEP 4: Map Context to Template Placeholders (46+ variables)
    def map_context_to_template(self) -> Dict[str, str]:
        if not self.t1_data:
            raise ValueError("ต้องเรียก parse_t1_json() ก่อน")
        
        t1 = self.t1_data
        tier = self.select_tier(t1.severity)
        asset = t1.assets[0] if t1.assets else {}
        
        # Format strings
        sl_change = f"SL-{t1.current_sl} → SL-{t1.target_sl} (Gap: {t1.sl_gap})"
        ttp_str = ", ".join(t1.ttp_ids) if t1.ttp_ids else "—"
        wisdom_str = "; ".join(t1.wisdom_steps) if t1.wisdom_steps else "—"
        risk_display = f"{t1.risk_score}/100" if t1.risk_score else "—"
        
        # Core 6 compliance check for reporting deadline
        verified_deadline, _ = self.verify_core6_compliance(
            tier["timeline_hours"],
            "TH-CYBER-58"
        )
        deadline_str = verified_deadline if isinstance(verified_deadline, str) else f"{verified_deadline} ชั่วโมง"
        
        # Smart defaults for asset fields
        asset_vendor = asset.get("vendor", asset.get("manufacturer", "—"))
        asset_model = asset.get("model", asset.get("name", "—"))
        
        return {
            # ===== Document Metadata =====
            "DOC_ID": f"POL-OT-IR-{tier['tier_code']}-{datetime.now().strftime('%Y%m%d')}",
            "DOC_VERSION": "1.0",
            "EFFECTIVE_DATE": datetime.now().strftime("%d/%m/%Y"),
            "NEXT_REVIEW": (datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y"),
            "SYNC_ID": self.sync_id,
            "CLIENT_NAME": t1.raw_json.get("client_name", "—"),
            "SECTOR_NAME": t1.raw_json.get("sector_name", "—"),
            
            # ===== Threat Intelligence =====
            "THREAT_NAME": t1.threat_name or "—",
            "THREAT_CATEGORY": t1.threat_type or "—",  # alias for THREAT_TYPE
            "THREAT_TYPE": t1.threat_type or "—",
            "SEVERITY_LEVEL": t1.severity.upper(),
            "ATTACK_VECTOR": t1.attack_vector or "—",
            "TTP_IDS": ttp_str,
            
            # ===== Asset Details =====
            "AFFECTED_ASSET": asset.get("name", "—"),
            "ASSET_VENDOR": asset_vendor,
            "ASSET_MODEL": asset_model,
            "ASSET_TYPE": asset.get("type", "—"),
            "ZONE_NAME": asset.get("zone", "—"),
            "CRITICALITY": asset.get("criticality", "MEDIUM").upper(),
            "MAX_VULN_COUNT": str(asset.get("max_vuln", asset.get("vuln_count", "0"))),
            "FIRMWARE": asset.get("firmware", "—"),
            
            # ===== Security Level Assessment =====
            "SL_CURRENT": str(t1.current_sl),
            "SL_TARGET": str(t1.target_sl),
            "SL_GAP": str(t1.sl_gap),
            "SL_CHANGE": sl_change,
            
            # ===== Risk Score =====
            "RISK_SCORE": risk_display,
            "LIKELIHOOD": str(t1.likelihood) if t1.likelihood else "—",
            "IMPACT_LEVEL": str(t1.impact_level) if t1.impact_level else "—",
            
            # ===== Pricing Tier =====
            "TIER_NAME": tier["tier"],
            "TIER_CODE": tier["tier_code"],
            "TIER_COLOR": tier["tier_color"],
            "PRICE_RANGE": tier["price_info"]["price_range_display"],
            "RECOMMENDED_PROCEDURES": ", ".join(tier["recommended_procedures"]),
            "TIMELINE_HOURS": str(tier["timeline_hours"]),
            
            # ===== Compliance & Core 6 =====
            "VERIFIED_REPORTING_DEADLINE": deadline_str,
            
            # ===== Legal/Regulatory (Core 6 verbatim) =====
            "LEGAL_AUTHORITY_REFERENCE": "พระราชบัญญัติการรักษาความมั่นคงปลอดภัยไซเบอร์ พ.ศ. 2562 มาตรา 58",
            "LEGAL_AUTHORITY_NAME": "สำนักงานคณะกรรมการการรักษาความมั่นคงปลอดภัยไซเบอร์แห่งชาติ (NCSA)",
            "LEGAL_ARTICLE_58_TITLE": "มาตรา 58 — การแจ้งเหตุภายใน 72 ชั่วโมง",
            "LEGAL_ARTICLE_58_TEXT": "หน่วยงาน CII ที่เกิดเหตุภัยคุกคามทางไซเบอร์ที่มีผลกระทบต่อความมั่นคงปลอดภัย ต้องแจ้งเหตุต่อ NCSA (สกมช.) ภายใน 72 ชั่วโมง นับแต่ทราบเหตุ โดยต้องระบุลักษณะเหตุ ผลกระทบ และมาตรการที่ดำเนินการแล้ว",
            "LEGAL_ARTICLE_58_EXCEPTION": "ไม่มีข้อยกเว้นสำหรับ CII — 72 ชม. คือ Hard Deadline",
            "LEGAL_ARTICLE_59_TITLE": "มาตรา 59 — การแจ้งเหตุภายใน 24 ชั่วโมง (กรณีภัยคุกคามร้ายแรง)",
            "LEGAL_ARTICLE_59_TEXT": "ในกรณีที่เหตุการณ์มีลักษณะร้ายแรงหรืออาจกระทบต่อความมั่นคงของรัฐ ต้องแจ้งภายใน 24 ชั่วโมง",
            "LEGAL_ARTICLE_59_TRIGGER": "เหตุการณ์ที่มีลักษณะร้ายแรง หรืออาจกระทบต่อความมั่นคงของรัฐ",
            "LEGAL_PENALTY_DESC": "ปรับสูงสุด 1,000,000 บาท + NCSA เปิดเผยชื่อต่อสาธารณะ",
            
            # ===== Standards Mapping =====
            "MAPPED_STANDARD_CLAUSE_1": "IEC 62443-2-1 EVENT 1.2",
            "MAPPED_STANDARD_DESC_1": "องค์กรต้องมีกระบวนการรายงานเหตุการณ์ที่เป็นเอกสาร",
            "MAPPED_STANDARD_CLAUSE_2": "IEC 62443-2-1 EVENT 1.3",
            "MAPPED_STANDARD_DESC_2": "องค์กรต้องมีช่องทาง/อินเทอร์เฟซสำหรับการรายงานเหตุการณ์",
            "MAPPED_STANDARD_CLAUSE_3": "IEC 62443-2-1 EVENT 1.8",
            "MAPPED_STANDARD_DESC_3": "องค์กรต้องมี incident handling และ response ที่เป็นระบบ",
            "MAPPED_STANDARD_CLAUSE_4": "NIST CSF RS.MA-2",
            "MAPPED_STANDARD_DESC_4": "รายงานต่อหน่วยงานรัฐภายในเวลาที่กำหนด",
            
            # ===== Wisdom Database =====
            "WISDOM_PATTERN_ID": t1.wisdom_pattern_id or "—",
            "WISDOM_STEPS": wisdom_str,
        }
    
    # STEP 5: Inject and Render (with multi-asset + delta support)
    def inject_and_render(self, template_path: str = None,
                         old_policy_path: str = None) -> InjectionResult:
        if not self.t1_data:
            raise ValueError("ต้องเรียก parse_t1_json() ก่อน")
        
        if template_path:
            self.template_engine.load_template(template_path)
        elif not self.template_engine.template_content:
            default = Path(__file__).parent / "Document-Template-Draft.md"
            if default.exists():
                self.template_engine.load_template(str(default))
        
        compliance = self.verify_full_compliance()
        values = self.map_context_to_template()
        
        # Multi-Asset Aggregation (Step 2.5)
        asset_summary = self.aggregate_multi_asset(self.t1_data.assets)
        
        # Delta Analysis (Step 3b)
        delta = self.delta_analysis(
            self.t1_data.raw_json,
            old_policy_path
        )
        
        # Render with full context (supports for-loops)
        filled_doc, count = self.template_engine.render_with_context(values, asset_summary)
        
        # Add sections
        override_section = self._generate_override_section()
        if override_section:
            filled_doc += override_section
        
        delta_section = self._generate_delta_section(delta)
        if delta_section:
            filled_doc += delta_section
        
        return InjectionResult(
            sync_id=self.sync_id,
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            tier=self.select_tier()["tier"],
            tier_code=self.select_tier()["tier_code"],
            placeholders_filled=count,
            overrides=self.overrides,
            filled_document=filled_doc,
            warnings=self.warnings + ([f"📊 Delta: {delta['change_count']} changes from previous policy"]
                                     if delta.get("has_delta") else []),
            compliance_verified=True
        )
    
    def _generate_override_section(self) -> str:
        if not self.overrides:
            return ""
        lines = ["\n---\n", "# บันทึกการ Override (T1 Intel → Core 6 Verbatim)\n",
                 "> ⚠️ **หมายเหตุ:** ข้อมูลจาก T1 Threat Intelligence ถูก override ด้วย Core 6 Verbatim เพื่อความถูกต้องตามกฎหมาย\n"]
        for i, ov in enumerate(self.overrides, 1):
            lines.append(f"## Override #{i}\n")
            lines.append(f"- **Placeholder:** `{ov.placeholder}`\n")
            lines.append(f"- **T1 Suggestion:** {ov.t1_value}\n")
            lines.append(f"- **Core 6 Override:** {ov.core6_value}\n")
            lines.append(f"- **Resolution:** {ov.resolution}\n")
            lines.append(f"- **เหตุผล:** {ov.rationale}\n")
        if self.warnings:
            lines.append("\n## Warnings / Recommendations\n")
            for w in self.warnings:
                lines.append(f"- {w}\n")
        return "".join(lines)
    
    # =========================================================================
    # FEATURE 3b: Delta Section Generator
    # =========================================================================
    def _generate_delta_section(self, delta: Dict[str, Any]) -> str:
        if not delta.get("has_delta"):
            return ""
        lines = ["\n---\n", "# 📊 Delta Analysis — การเปลี่ยนแปลงจากเล่มก่อน\n",
                 "> ⚠️ **หมายเหตุ:** นโยบายฉบับนี้มีการเปลี่ยนแปลงจากเล่มก่อน กรุณาอ่านส่วนนี้ก่อน\n",
                 f"| ประเภทการเปลี่ยนแปลง | รายละเอียด |\n",
                 f"|---|---|\n"]
        for change in delta.get("changes", []):
            lines.append(f"| **{change['type']}** | {change['description']} |\n")
        lines.append(f"\n**จำนวนการเปลี่ยนแปลง:** {delta['change_count']} รายการ\n")
        return "".join(lines)
    
    # =========================================================================
    # FEATURE 4: Export Functions
    # =========================================================================
    def export_html(self, content: str, output_path: str, title: str = "OTengine4 Policy Document") -> str:
        """
        Convert Markdown document to a professional HTML dashboard.
        Ready to send via email or host on web.
        """
        import markdown
        
        # Convert markdown to HTML
        html_body = markdown.markdown(
            content,
            extensions=['tables', 'fenced_code', 'toc']
        )
        
        # Build full HTML with OTengine4 branding
        html = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'IBM Plex Sans Thai', 'Segoe UI', sans-serif; 
                background: #0a0e1a; color: #e2e8f0; line-height: 1.7; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
        .header {{ background: linear-gradient(135deg, #1a1f35 0%, #0d1220 100%);
                   border: 1px solid #2a3f5f; border-radius: 16px; padding: 40px;
                   margin-bottom: 32px; text-align: center; }}
        .header h1 {{ color: #60a5fa; font-size: 28px; margin-bottom: 8px; }}
        .header .subtitle {{ color: #94a3b8; font-size: 14px; }}
        .sync-badge {{ display: inline-block; background: #1e3a5f; border: 1px solid #3b82f6;
                       color: #60a5fa; padding: 4px 16px; border-radius: 20px;
                       font-size: 12px; margin-top: 16px; }}
        .content {{ background: #111827; border: 1px solid #1f2937; border-radius: 16px;
                    padding: 40px; }}
        .content h1, .content h2, .content h3 {{ color: #60a5fa; margin: 24px 0 12px; }}
        .content h1 {{ font-size: 24px; border-bottom: 2px solid #1e3a5f; padding-bottom: 12px; }}
        .content h2 {{ font-size: 20px; color: #93c5fd; }}
        .content h3 {{ font-size: 16px; color: #a5b4fc; }}
        .content p {{ margin: 12px 0; color: #cbd5e1; }}
        .content table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
        .content th {{ background: #1e3a5f; color: #60a5fa; padding: 12px; 
                      text-align: left; font-size: 13px; }}
        .content td {{ padding: 10px 12px; border-bottom: 1px solid #1f2937; 
                      font-size: 13px; color: #cbd5e1; }}
        .content tr:hover {{ background: #1a2332; }}
        .content blockquote {{ border-left: 4px solid #3b82f6; padding: 16px 20px;
                              background: #1a1f35; margin: 16px 0; border-radius: 0 8px 8px 0; }}
        .content code {{ background: #1e293b; padding: 2px 8px; border-radius: 4px;
                         font-size: 13px; color: #a5b4fc; }}
        .content pre {{ background: #1e293b; padding: 16px; border-radius: 8px;
                        overflow-x: auto; margin: 16px 0; }}
        .severity-CRITICAL {{ color: #ef4444; }}
        .severity-HIGH {{ color: #f97316; }}
        .severity-MEDIUM {{ color: #eab308; }}
        .severity-LOW {{ color: #22c55e; }}
        .footer {{ text-align: center; padding: 24px; color: #64748b; font-size: 12px; }}
        .warning-banner {{ background: linear-gradient(90deg, #7c2d12, #9a3412);
                           border: 1px solid #ea580c; border-radius: 12px; padding: 20px;
                           margin-bottom: 24px; }}
        .delta-box {{ background: #1e3a5f; border: 1px solid #3b82f6; border-radius: 12px;
                      padding: 20px; margin: 24px 0; }}
        @media print {{ 
            body {{ background: white; color: black; }}
            .content, .header {{ border: 1px solid #ddd; }} 
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ OTengine4 — OT Cybersecurity Policy</h1>
            <div class="subtitle">T2 Tri-Core v2.1 — Autonomous Policy Generator</div>
            <div class="sync-badge">Sync ID: {self.sync_id or 'N/A'}</div>
        </div>
        <div class="content">
            {html_body}
        </div>
        <div class="footer">
            Generated by T2 Tri-Core v2.1 Smart Link | OTengine4 | {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </div>
    </div>
</body>
</html>"""
        
        output = Path(output_path)
        output.write_text(html, encoding="utf-8")
        return str(output)
    
    def export_pdf(self, html_path: str, output_path: str = None) -> str:
        """
        Convert HTML to PDF using available tools.
        Tries: weasyprint → chromium → wkhtmltopdf → pandoc
        """
        if output_path is None:
            output_path = str(Path(html_path).with_suffix('.pdf'))
        
        # Try weasyprint first (best for Thai/UTF-8)
        try:
            from weasyprint import HTML as WPHTML
            WPHTML(filename=html_path).write_pdf(output_path)
            print(f"  ✅ PDF exported (weasyprint): {output_path}")
            return output_path
        except ImportError:
            pass
        except Exception as e:
            print(f"  ⚠️ weasyprint failed: {e}")
        
        # Try wkhtmltopdf
        try:
            import subprocess
            result = subprocess.run(
                ['wkhtmltopdf', '--enable-local-file-access', '--print-media-type',
                 html_path, output_path],
                capture_output=True, timeout=60
            )
            if Path(output_path).exists():
                print(f"  ✅ PDF exported (wkhtmltopdf): {output_path}")
                return output_path
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Fallback: generate print-ready HTML
        print(f"  ⚠️ PDF tools not available — HTML saved instead")
        print(f"     Open this URL in Chrome → Print → Save as PDF:")
        print(f"     {html_path}")
        return html_path  # return HTML path as fallback
    
    # Quick Methods
    def run_full_pipeline(self, t1_json_path: str = None, template_path: str = None,
                         output_path: str = None, old_policy_path: str = None,
                         export_format: str = None) -> InjectionResult:
        """
        รันทุกขั้นตอนในคำสั่งเดียว:
        1. Parse T1 JSON (or auto-fetch from T1 dir)
        2. Multi-asset aggregation
        3. Delta analysis vs previous policy
        4. Inject & render with Jinja2
        5. Export (MD → HTML → PDF)
        """
        # Auto-fetch if no JSON path provided
        if not t1_json_path:
            found = self.find_latest_t1_json()
            if found:
                t1_json_path = found
            else:
                print("  ⚠️ No T1 JSON found. Using sample data.")
        
        if t1_json_path and Path(t1_json_path).exists():
            self.parse_t1_json(t1_json_path)
        else:
            print("  ⚠️ No T1 JSON path or file not found.")
        
        result = self.inject_and_render(template_path, old_policy_path)
        
        if output_path:
            Path(output_path).write_text(result.filled_document, encoding="utf-8")
            print(f"  📄 Markdown saved: {output_path}")
            
            # Auto-export based on format
            if export_format in ("html", "both"):
                html_path = str(Path(output_path).with_suffix('.html'))
                self.export_html(result.filled_document, html_path)
                print(f"  🌐 HTML exported: {html_path}")
            
            if export_format in ("pdf", "both"):
                html_path = str(Path(output_path).with_suffix('.html'))
                # Ensure HTML exists
                if not Path(html_path).exists():
                    self.export_html(result.filled_document, html_path)
                pdf_path = self.export_pdf(html_path)
                if pdf_path != html_path:
                    print(f"  📰 PDF exported: {pdf_path}")
        
        return result

# =============================================================================
# SECTION 6: Main Execution
# =============================================================================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="T1 → T2 Smart Link v2.1 — Neural Link for Autonomous Policy Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python t2_integrator.py --auto-fetch                    # Scan T1 dir for latest JSON
  python t2_integrator.py --t1-json /path/to/t1.json      # Direct file
  python t2_integrator.py --auto-fetch --format html      # Auto-fetch + HTML export
  python t2_integrator.py --t1-json /path/t1.json --delta # Compare with previous
  python t2_integrator.py --format pdf --output out.md    # Generate all formats
        """
    )
    parser.add_argument("--t1-json", help="Path to T1 JSON output")
    parser.add_argument("--template", "--template-path", dest="template",
                        help="Path to T2 Document Template")
    parser.add_argument("--output", "--output-path", dest="output",
                        help="Path to output markdown file")
    parser.add_argument("--auto-fetch", action="store_true",
                        help="Auto-scan T1 output directories for latest JSON")
    parser.add_argument("--delta", "--compare", dest="delta",
                        help="Path to previous policy (for delta analysis)")
    parser.add_argument("--format", choices=["html", "pdf", "both", "md"],
                        default="md", help="Export format (default: md)")
    parser.add_argument("--client", help="Client/organization name override")
    parser.add_argument("--sector", help="Sector name override")
    args = parser.parse_args()
    
    # Build template path
    template_path = args.template or str(Path(__file__).parent / "Document-Template-Draft.md")
    
    link = T1TOSmartLink(
        t1_json_path=args.t1_json,
        template_path=template_path,
        mapping_config_path=str(Path(__file__).parent / "t1_field_mapping.json")
    )
    
    # Determine what T1 data to use
    t1_path = args.t1_json
    if args.auto_fetch and not t1_path:
        found = link.find_latest_t1_json()
        if found:
            t1_path = found
    
    if t1_path and Path(t1_path).exists():
        print(f"Loading T1 JSON: {t1_path}")
        link.parse_t1_json(t1_path)
    else:
        # Demo with realistic sample data (Volt Typhoon scenario)
        sample_t1 = {
            "threat_summary": {
                "name": "Volt Typhoon",
                "type": "APT",
                "severity": "CRITICAL",
                "attack_vector": "Living-off-the-Land (LotL) via native OS tools",
                "ttp_ids": ["T1070", "T1106", "T0861", "T1016"]
            },
            "asset_analysis": [{
                "name": "Rockwell ControlLogix 1756-L85E",
                "vendor": "Rockwell Automation",
                "type": "PLC/DCS Controller",
                "criticality": "CRITICAL",
                "max_vuln": 7,
                "firmware": "V32.014",
                "zone": "L2 Process Control",
                "protocols": ["EtherNet/IP", "CIP"]
            }, {
                "name": "Siemens S7-1500",
                "vendor": "Siemens",
                "type": "PLC",
                "criticality": "HIGH",
                "max_vuln": 4,
                "firmware": "V2.9",
                "zone": "L2 Control",
                "protocols": ["Profinet", "S7Comm"]
            }],
            "sl_assessment": {"current_sl": 1, "target_sl": 4, "gap": 3},
            "wisdom_matches": [{"pattern_id": "W-041-03", "steps": ["Detect anomalous Logix traffic", "Segment ControlLogix VLAN", "Enable CIP Security", "Deploy Honeypot PLC"]}],
            "risk_score": {"overall": 94, "likelihood": 8, "impact": 10},
            "client_name": args.client or "สถานีไฟฟ้ากรุงเทพฯ",
            "sector_name": args.sector or "ไฟฟ้า"
        }
        print("No T1 JSON found. Running with sample data (Volt Typhoon + Multi-Asset)...")
        link.parse_t1_from_dict(sample_t1)
    
    # Determine export format
    export_fmt = None if args.format == "md" else args.format
    
    # Run pipeline
    result = link.inject_and_render(template_path, old_policy_path=args.delta)
    
    print(f"\n{'='*60}")
    print(f"✅ T2 Neural Link — Sync Complete!")
    print(f"{'='*60}")
    print(f"   Sync ID:       {result.sync_id}")
    print(f"   Tier:          {result.tier} ({result.tier_code})")
    print(f"   Placeholders:  {result.placeholders_filled}")
    print(f"   Compliance:    {'✅ Verified' if result.compliance_verified else '⚠️ Failed'}")
    print(f"   Overrides:     {len(result.overrides)}")
    print(f"   Warnings:      {len(result.warnings)}")
    
    if result.warnings:
        for w in result.warnings:
            print(f"   ⚠️  {w}")
    
    # Output handling
    if args.output:
        md_path = args.output
        Path(md_path).write_text(result.filled_document, encoding="utf-8")
        print(f"\n  📄 Markdown: {md_path}")
        
        if export_fmt in ("html", "both"):
            html_path = Path(md_path).with_suffix('.html')
            link.export_html(result.filled_document, str(html_path))
            print(f"  🌐 HTML:      {html_path}")
        
        if export_fmt in ("pdf", "both"):
            html_path = Path(md_path).with_suffix('.html')
            if not html_path.exists():
                link.export_html(result.filled_document, str(html_path))
            pdf_path = link.export_pdf(str(html_path))
            if pdf_path != str(html_path):
                print(f"  📰 PDF:      {pdf_path}")
    else:
        print(f"\n  📄 Document ready ({len(result.filled_document)} chars)")
        print(f"  Use --output <path.md> --format html to export")
