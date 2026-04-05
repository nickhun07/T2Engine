#!/bin/bash
# ============================================================
# T2 Tri-Core v2.1 — Full Deploy to NAS
# Run ONCE on NAS via SSH
# ============================================================
set -e

echo "=========================================="
echo "T2 Tri-Core v2.1 — Full Deploy"
echo "=========================================="

WORK_DIR="/opt/t2-deploy"
REPO_URL="https://github.com/nickhun07/T2Engine.git"
ACSSA_DIR="/opt/t2-acssa-engine"  # หรือ path ที่ t2-acssa-engine อยู่จริง

# ============================================================
# STEP 1: Find ACSSA source directory
# ============================================================
echo "[1/6] Finding t2-acssa-engine source..."
if [ -d "$ACSSA_DIR" ]; then
    echo "  Found: $ACSSA_DIR"
elif [ -d "/root/t2-acssa-engine" ]; then
    ACSSA_DIR="/root/t2-acssa-engine"
    echo "  Found: $ACSSA_DIR"
elif [ -d "/home/nicksor0s/t2-acssa-engine" ]; then
    ACSSA_DIR="/home/nicksor0s/t2-acssa-engine"
    echo "  Found: $ACSSA_DIR"
else
    echo "  ERROR: t2-acssa-engine not found!"
    echo "  Running: find / -name 'main.py' -path '*/t2*' 2>/dev/null"
    find / -name "main.py" 2>/dev/null | grep -i acssa | head -5
    exit 1
fi

# ============================================================
# STEP 2: Clone GitHub repo to NAS
# ============================================================
echo "[2/6] Cloning T2Engine repo..."
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"
rm -rf T2Engine 2>/dev/null
git clone "$REPO_URL" T2Engine
echo "  Cloned: $WORK_DIR/T2Engine"
ls -la "$WORK_DIR/T2Engine/"

# ============================================================
# STEP 3: Merge T2 files into ACSSA source
# ============================================================
echo "[3/6] Merging T2 files into ACSSA source..."
T2_FILES="$WORK_DIR/T2Engine"

# Copy core files
cp "$T2_FILES/t2_integrator.py" "$ACSSA_DIR/"
cp "$T2_FILES/t2_webapp_v1.py" "$ACSSA_DIR/"
cp "$T2_FILES/Document-Template-Draft.md" "$ACSSA_DIR/"

echo "  Copied: t2_integrator.py, t2_webapp_v1.py, Document-Template-Draft.md"

# ============================================================
# STEP 4: Add new endpoints to main.py
# ============================================================
echo "[4/6] Adding T2 endpoints to main.py..."

# Check if main.py exists
if [ ! -f "$ACSSA_DIR/main.py" ]; then
    echo "  ERROR: main.py not found at $ACSSA_DIR/main.py"
    ls "$ACSSA_DIR/"
    exit 1
fi

# Create backup
cp "$ACSSA_DIR/main.py" "$ACSSA_DIR/main.py.backup.$(date +%Y%m%d%H%M%S)"

# Append T2 endpoints to main.py
cat >> "$ACSSA_DIR/main.py" << 'T2_EOF'

# ============================================================
# T2 Tri-Core v2.1 — New Endpoints
# ============================================================
from t2_integrator import T1TOSmartLink
from datetime import datetime

T2_VERSION = "2.1"

@app.get("/api/v1/t2/status")
async def t2_status():
    """T2 Tri-Core status endpoint"""
    return {
        "status": "ready",
        "version": T2_VERSION,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/t2/generate")
async def t2_generate(request: dict):
    """
    Generate T2 policy document from T1 threat intelligence.
    Body: {
        "client_name": str,
        "sector": str,
        "tier": str (B/S/P/E),
        "threat_name": str (optional),
        "threat_type": str (optional)
    }
    """
    try:
        link = T1TOSmartLink()
        
        # Build T1-like data structure
        t1_data = {
            "threat_summary": {
                "name": request.get("threat_name", "Volt Typhoon"),
                "type": request.get("threat_type", "APT"),
                "severity": request.get("severity", "CRITICAL"),
                "attack_vector": request.get("attack_vector", "LotL"),
                "ttp_ids": request.get("ttp_ids", ["T1070"])
            },
            "asset_analysis": [{
                "name": request.get("asset_name", "Rockwell ControlLogix"),
                "vendor": request.get("asset_vendor", "Rockwell"),
                "type": request.get("asset_type", "PLC"),
                "criticality": request.get("criticality", "CRITICAL"),
                "max_vuln": request.get("max_vuln", 7),
                "zone": request.get("zone", "L2 Process Control")
            }],
            "sl_assessment": {
                "current_sl": request.get("current_sl", 1),
                "target_sl": request.get("target_sl", 4),
                "gap": request.get("sl_gap", 3)
            },
            "wisdom_matches": [{
                "pattern_id": request.get("wisdom_pattern", "W-041-03"),
                "steps": request.get("wisdom_steps", ["Detect anomalous traffic"])
            }],
            "risk_score": {
                "overall": request.get("risk_score", 94),
                "likelihood": request.get("likelihood", 8),
                "impact": request.get("impact", 10)
            },
            "client_name": request.get("client_name", "Test Corp"),
            "sector_name": request.get("sector", "Energy")
        }
        
        link.parse_t1_from_dict(t1_data)
        
        # Tier mapping
        tier_map = {"B": "Base", "S": "Standard", "P": "Pro", "E": "Enterprise"}
        tier_code = request.get("tier", "E")
        tier_name = tier_map.get(tier_code, "Enterprise")
        
        # Run integration
        output_path = f"/tmp/t2_output_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
        result = link.run_full_pipeline(
            t1_json_path=None,
            template_path=f"{ACSSA_DIR}/Document-Template-Draft.md",
            output_path=output_path
        )
        
        return {
            "success": True,
            "sync_id": result.sync_id,
            "tier": tier_name,
            "tier_code": tier_code,
            "placeholders_filled": result.placeholders_filled,
            "warnings": result.warnings,
            "markdown_length": len(result.filled_document),
            "output_file": output_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

T2_EOF

echo "  ✅ Appended T2 endpoints to main.py"

# ============================================================
# STEP 5: Install dependencies in container
# ============================================================
echo "[5/6] Checking Python dependencies..."
# Check if jinja2, weasyprint, markdown available in container
docker exec t2-acssa-api python3 -c "import jinja2, markdown; print('Deps OK')" 2>/dev/null || \
docker exec t2-acssa-api pip install jinja2 markdown --quiet 2>/dev/null

# ============================================================
# STEP 6: Rebuild and restart
# ============================================================
echo "[6/6] Rebuilding Docker image..."
cd "$ACSSA_DIR"

# Check if Dockerfile exists
if [ -f "Dockerfile" ]; then
    echo "  Building: docker build -t t2-acssa-engine:latest ."
    docker build -t t2-acssa-engine:latest . 2>&1 | tail -5
else
    echo "  WARNING: No Dockerfile found at $ACSSA_DIR"
    echo "  Files in ACSSA_DIR:"
    ls -la "$ACSSA_DIR/"
fi

# Restart container
echo "  Restarting container..."
docker-compose down 2>/dev/null || docker stop t2-acssa-api
docker-compose up -d 2>/dev/null || docker run -d --name t2-acssa-api \
    -p 8000:8000 \
    -v "$ACSSA_DIR:/app" \
    t2-acssa-engine:latest

# Wait and check health
sleep 5
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null | grep -c "ok" || echo 0)
if [ "$HEALTH" -gt 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Deploy SUCCESS!"
    echo "=========================================="
    echo "T2 API: http://$(hostname -I | awk '{print $1}'):8000/api/v1/t2/status"
    echo "T2 Generate: POST /api/v1/t2/generate"
else
    echo ""
    echo "=========================================="
    echo "⚠️ Container may need manual restart"
    echo "=========================================="
    docker logs t2-acssa-api --tail 20
fi

echo ""
echo "Files deployed:"
ls -la "$ACSSA_DIR/" | grep t2_
