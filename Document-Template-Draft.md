# T2 Tri-Core v2.0 — Dynamic Master Template
# Incident Response & Reporting Policy (มาตรา 58)
# ================================================================
# Version: 2.0 (Dynamic Template)
# Syntax: Jinja2 ({{VARIABLE|default('fallback')}})
# Smart Link Source: T1 → T2 via t2_integrator.py
# ================================================================

# ============================================================================
# 📄 หน้าปกเอกสาร (Cover Page)
# ============================================================================

| รายการ | รายละเอียด |
|--------|-------------|
| **ชื่อองค์กร/ลูกค้า** | {{CLIENT_NAME|default('[ชื่อองค์กรของท่าน]')}} |
| **ชื่อเอกสาร** | นโยบายการรักษาความมั่นคงปลอดภัยไซเบอร์ด้านการแจ้งเหตุและการตอบสนองต่อเหตุการณ์ |
| **เวอร์ชัน** | {{DOC_VERSION|default('1.0')}} |
| **วันที่มีผลบังคับ** | {{EFFECTIVE_DATE|default('[วันที่ประกาศใช้]')}} |
| **ภาค Sector** | {{SECTOR_NAME|default('[ภาคพลังงาน/การผลิต/ขนส่ง/น้ำประปา/อื่นๆ]')}} |
| **ระดับความลับ** | ภายใน — จำกัดการเผยแพร่ |
| **รหัสเอกสาร** | {{DOC_ID|default('POL-OT-IR-[XXX]')}} |
| **Sync ID (Smart Link)** | {{SYNC_ID|default('[ระบบจะกำหนดอัตโนมัติ]')}} |

---

# ============================================================================
# 📋 ข้อมูล Smart Link Context (T1 → T2 Injection Summary)
# ============================================================================
# ส่วนนี้สรุปข้อมูลที่ได้รับจาก T1 Threat Intelligence ผ่าน Smart Link
# หากเห็น Sync ID = [ระบบจะกำหนดอัตโนมัติ] แสดงว่ายังไม่ได้ inject ข้อมูลจริง
# ============================================================================

## 🔗 Smart Link Context (T1 → T2)

| Field | Value | Source |
|-------|-------|--------|
| **Threat Name** | {{THREAT_NAME|default('[ไม่ระบุภัยคุกคาม]')}} | T1 Radar |
| **Threat Category** | {{THREAT_CATEGORY|default('[ไม่ระบุประเภท]')}} | T1 Radar |
| **Severity Level** | {{TIER_COLOR|default('🟡')}} **{{SEVERITY_LEVEL|default('MEDIUM')}}** | T1 Radar |
| **Attack Vector** | {{ATTACK_VECTOR|default('[ไม่ระบุ]')}} | T1 Radar |
| **TTPs (MITRE)** | {{TTP_IDS|default('[ไม่ระบุ]')}} | T1 Radar |
| **Affected Asset** | **{{AFFECTED_ASSET|default('[ระบุอุปกรณ์วิกฤต]')}}** | T1 Asset Analysis |
| **Asset Vendor** | {{ASSET_VENDOR|default('[ไม่ระบุยี่ห้อ]')}} | T1 Asset Analysis |
| **Asset Model** | {{ASSET_MODEL|default('[ไม่ระบุรุ่น]')}} | T1 Asset Analysis |
| **Asset Type** | {{ASSET_TYPE|default('[ไม่ระบุประเภท]')}} | T1 Asset Analysis |
| **Zone** | {{ZONE_NAME|default('[ไม่ระบุโซน]')}} | T1 Asset Analysis |
| **Criticality** | {{CRITICALITY|default('MEDIUM')}} | T1 Asset Analysis |
| **Max CVEs** | {{MAX_VULN_COUNT|default('0')}} | T1 Asset Analysis |
| **Firmware** | {{FIRMWARE|default('[ไม่ระบุ]')}} | T1 Asset Analysis |
| **Current Security Level** | SL-{{SL_CURRENT|default('0')}} | T1 SL Assessment |
| **Target Security Level** | SL-{{SL_TARGET|default('0')}} | T1 SL Assessment |
| **SL Gap** | {{SL_GAP|default('0')}} | T1 SL Assessment |
| **Risk Score** | **{{RISK_SCORE|default('[ไม่ระบุ]')}}** | T1 Risk Engine |
| **Likelihood** | {{LIKELIHOOD|default('0')}}/10 | T1 Risk Engine |
| **Impact Level** | {{IMPACT_LEVEL|default('0')}}/10 | T1 Risk Engine |
| **Recommended Tier** | {{TIER_COLOR|default('🟡')}} **{{TIER_NAME|default('Standard')}}** — {{PRICE_RANGE|default('[ราคาตาม Tier]')}} | T2 Tier Selector |
| **Reporting Deadline** | ⚠️ {{VERIFIED_REPORTING_DEADLINE|default('72 ชั่วโมง (Core 6 Verified)')}} | Core 6 Verbatim |
| **Wisdom Pattern** | {{WISDOM_PATTERN_ID|default('[ไม่ระบุ]')}} | T1 Wisdom DB |
| **Wisdom Procedure** | {{WISDOM_STEPS|default('[ขั้นตอนจาก T1 Wisdom]')}} | T1 Wisdom DB |

---

# ============================================================================
# 📌 Executive Summary
# ============================================================================

## บทสรุปผู้บริหาร (Executive Summary)

**เอกสารฉบับนี้จัดทำขึ้นเพื่อตอบสนองต่อภัยคุกคามทางไซเบอร์ที่ตรวจพบในระบบ OT/ICS ขององค์กร**

### สรุปสถานการณ์

ตรวจพบภัยคุกคามประเภท **{{THREAT_CATEGORY|default('[ประเภทภัยคุกคาม]')}}** นามว่า **"{{THREAT_NAME|default('[ชื่อภัยคุกคาม]')}}"** ซึ่งมีระดับความรุนแรง {{TIER_COLOR|default('🟡')}} **{{SEVERITY_LEVEL|default('MEDIUM')}}** ภัยคุกคามนี้ใช้รูปแบบการโจมตีผ่าน **{{ATTACK_VECTOR|default('[รูปแบบการโจมตี]')}}** โดยมีเป้าหมายที่ระบบ {{SECTOR_NAME|default('[ภาค Sector]')}}

ระบบที่ได้รับผลกระทบ ได้แก่ **{{AFFECTED_ASSET|default('[ระบุอุปกรณ์วิกฤต]')}}** ({{ASSET_TYPE|default('อุปกรณ์ OT/ICS')}}) ยี่ห้อ **{{ASSET_VENDOR|default('[ไม่ระบุ]')}}** รุ่น {{ASSET_MODEL|default('[ไม่ระบุ]')}} ตั้งอยู่ในโซน **{{ZONE_NAME|default('[โซน]')}}** ซึ่งถูกจัดระดับความสำคัญเป็น **{{CRITICALITY|default('MEDIUM')}}** Critical

### การประเมินความเสี่ยง

จากการวิเคราะห์พบว่าระบบมี Security Level ปัจจุบันที่ **SL-{{SL_CURRENT|default('0')}}** และควรยกระดับเป็น **SL-{{SL_TARGET|default('0')}}** เพื่อรับมือกับภัยคุกคามนี้ (Gap: **{{SL_GAP|default('0')}}** ระดับ) คะแนนความเสี่ยงรวมอยู่ที่ **{{RISK_SCORE|default('[คะแนน]')}}** (Likelihood {{LIKELIHOOD|default('0')}}/10 × Impact {{IMPACT_LEVEL|default('0')}}/10)

### มาตรการเร่งด่วน

องค์กรต้องดำเนินการตามขั้นตอนที่ {{WISDOM_PATTERN_ID|default('[ระบุ Pattern]')}} ซึ่งประกอบด้วย:

> {{WISDOM_STEPS|default('[ขั้นตอนจาก Wisdom Database จะแสดงที่นี่]')}}

### ข้อบังคับทางกฎหมาย

**⚠️ หน้าที่ตามกฎหมาย:** ตาม{{LEGAL_AUTHORITY_REFERENCE|default('พระราชบัญญัติการรักษาความมั่นคงปลอดภัยไซเบอร์ พ.ศ. 2562 มาตรา 58')}} องค์กรที่เป็น CII ต้องแจ้งเหตุต่อ NCSA ภายใน **{{VERIFIED_REPORTING_DEADLINE|default('72 ชั่วโมง')}}** นับแต่ทราบเหตุ มิฉะนั้นอาจถูกลงโทษ {{LEGAL_PENALTY_DESC|default('ปรับสูงสุด 1,000,000 บาท + เปิดเผยชื่อ')}}

### ข้อเสนอแนะตาม Pricing Tier

ตามการประเมินความรุนแรงของภัยคุกคาม ข้อเสนอแนะสำหรับองค์กรคือ **{{TIER_NAME|default('[Tier]')}}** ซึ่งมีราคา {{PRICE_RANGE|default('[ช่วงราคา]')}} พร้อมด้วย {{RECOMMENDED_PROCEDURES|default('[ขั้นตอนที่แนะนำ]')}}

---

# ============================================================================
# 📦 Multi-Asset Inventory Table (Dynamic Loop — รองรับหลายอุปกรณ์)
# ============================================================================

{% if assets and asset_count > 0 %}
## 📋 รายการอุปกรณ์ที่ได้รับผลกระทบ ({{ asset_count }} รายการ)

> **🔍 Delta Alert:** {% if has_multiple_vendors %}พบอุปกรณ์หลายยี่ห้อในรายงานเดียว — ต้องประสานงานหลาย vendor{% else %}อุปกรณ์ทั้งหมดมาจาก {{ unique_vendors[0] if unique_vendors else '—' }}{% endif %}

| # | ชื่ออุปกรณ์ | ยี่ห้อ | ประเภท | โซน | ความสำคัญ | Max CVEs | Firmware | Protocol |
|---|------------|--------|---------|------|-----------|---------|---------|---------|
{% for asset in assets %}
| {{ loop.index }} | **{{ asset.name }}** | {{ asset.vendor }} | {{ asset.type }} | {{ asset.zone }} | {{ asset.criticality }} | {{ asset.max_vuln }} | {{ asset.firmware }} | {{ asset.protocols|join(', ') if asset.protocols else '—' }} |
{% endfor %}

### สรุปภาพรวมอุปกรณ์
- **จำนวนอุปกรณ์:** {{ asset_count }} ชิ้น
- **ยี่ห้อที่พบ:** {{ unique_vendors|join(', ') if unique_vendors else '—' }}
- **โซนที่ได้รับผลกระทบ:** {{ unique_zones|join(', ') if unique_zones else '—' }}
- **จำนวน vulnerabilities ทั้งหมด:** {{ total_vulnerabilities }}
- **ระดับความสำคัญสูงสุด:** {{ highest_criticality }}
{% else %}
> ⚠️ ไม่พบข้อมูลอุปกรณ์ — กรุณาตรวจสอบ T1 JSON output
{% endif %}

# ============================================================================
# ส่วนที่ 1: ข้อมูลเอกสารและการอนุมัติ
# ============================================================================

## 1.1 ประวัติการแก้ไขเอกสาร

| เวอร์ชัน | วันที่ | ผู้แก้ไข | รายละเอียดการแก้ไข |
|-----------|--------|----------|----------------------|
| 1.0 | [วันที่] | [ผู้จัดทำ] | ฉบับแรก — สร้างจาก T2 Tri-Core v2.0 Smart Link |

## 1.2 การอนุมัติเอกสาร

| ตำแหน่ง | ชื่อ-นามสกุล | ลายมือชื่อ | วันที่ |
|---------|-------------|-----------|--------|
| ผู้อนุมัตินโยบาย | | | |
| ผู้จัดทำนโยบาย | | | |
| ผู้ตรวจสอบ (CISO) | | | |

## 1.3 ข้อมูลเอกสาร (Document Metadata)

| Field | Value |
|-------|-------|
| Document ID | {{DOC_ID|default('POL-OT-IR-[XXX]')}} |
| Version | {{DOC_VERSION|default('1.0')}} |
| Effective Date | {{EFFECTIVE_DATE|default('[วันที่]')}} |
| Next Review | {{NEXT_REVIEW|default('[วันที่ทบทวน]')}} |
| Threat Level | {{TIER_COLOR|default('🟡')}} {{SEVERITY_LEVEL|default('MEDIUM')}} |
| Pricing Tier | {{TIER_COLOR|default('🟡')}} {{TIER_NAME|default('[Tier]')}} — {{PRICE_RANGE|default('[ราคา]')}} |
| Classification | ภายใน — จำกัดการเผยแพร่ |
| Smart Link Sync ID | {{SYNC_ID|default('[รอการ Sync]')}} |
| Generated By | T2 Tri-Core v2.0 (OTengine4) |

---

# ============================================================================
# ส่วนที่ 2: ขอบเขตและวัตถุประสงค์
# ============================================================================

## 2.1 ขอบเขต

นโยบายฉบับนี้ครอบคลุม:

- หน่วยงานที่จัดเป็น "หน่วยงานโครงสร้างพื้นฐานสำคัญทางสารสนเทศ (CII)" ตาม{{LEGAL_AUTHORITY_REFERENCE|default('พระราชบัญญัติการรักษาความมั่นคงปลอดภัยไซเบอร์ พ.ศ. 2562')}}
- ระบบ SCADA/ICS/DCS ทั้งหมดที่อยู่ภายใต้การดูแลขององค์กร โดยเฉพาะระบบ{{AFFECTED_ASSET|default('[อุปกรณ์วิกฤต]')}}ในภาค{{SECTOR_NAME|default('[ภาค Sector]')}}
- กระบวนการทุกขั้นตอนตั้งแต่การตรวจจับเหตุ การแจ้งเหตุ จนถึงการฟื้นฟู
- ผู้ใช้งานทุกระดับ รวมถึงผู้บริหาร วิศวกร และบุคลากรสนับสนุน

{% if THREAT_NAME and THREAT_NAME != '[ชื่อภัยคุกคาม]' %}
- **ภัยคุกคามเฉพาะ:** นโยบายนี้จัดทำขึ้นเพื่อรับมือกับภัยคุกคาม {{THREAT_NAME}} ({{THREAT_CATEGORY|default('ไม่ระบุ')}}) ที่ตรวจพบในระบบ {{AFFECTED_ASSET|default('[ระบุ]')}} ผ่าน{{ATTACK_VECTOR|default('[เวกเตอร์]')}}
{% endif %}

## 2.2 วัตถุประสงค์

1. กำหนดกรอบการตอบสนองต่อเหตุการณ์ไซเบอร์ที่สอดคล้องกับ{{MAPPED_STANDARD_CLAUSE_1|default('มาตรฐาน IEC 62443-2-1 และ NIST CSF')}}
2. บรรลุข้อกำหนดทางกฎหมายว่าด้วยการแจ้งเหตุภายใน {{VERIFIED_REPORTING_DEADLINE|default('72 ชั่วโมง')}} ตาม{{LEGAL_AUTHORITY_REFERENCE|default('มาตรา 58 แห่ง พ.ร.บ.ไซเบอร์')}}
3. ลดผลกระทบจากเหตุการณ์ไซเบอร์ต่อการดำเนินการและชื่อเสียงองค์กร
4. สร้างความเชื่อมั่นให้ผู้มีส่วนได้ส่วนเสียว่าองค์กรมีความพร้อมรับมือภัยคุกคาม{{THREAT_NAME|default('')}} {{THREAT_CATEGORY|default('')}}
5. กำหนดมาตรการรับมือเฉพาะสำหรับระบบ {{AFFECTED_ASSET|default('[อุปกรณ์วิกฤต]')}} ({{ASSET_VENDOR|default('[ยี่ห้อ]')}} {{ASSET_MODEL|default('[รุ่น]')}}) ที่เป็นไปตาม{{MAPPED_STANDARD_CLAUSE_2|default('IEC 62443')}}

---

# ============================================================================
# ส่วนที่ 3: นิยามและคำย่อ
# ============================================================================

## 3.1 นิยามศัพท์

| คำศัพท์ | นิยาม |
|---------|-------|
| **เหตุการณ์ไซเบอร์ (Cyber Incident)** | เหตุการณ์ที่มีผลกระทบต่อความมั่นคงปลอดภัยไซเบอร์ของระบบสารสนเทศ อันได้แก่ การละเมิดความมั่นคงปลอดภัย การล่วงละเมิดนโยบาย หรือกิจกรรมที่ไม่ได้รับอนุญาต |
| **{{THREAT_NAME|default('[ชื่อภัยคุกคาม]')}}** | ภัยคุกคามประเภท{{THREAT_CATEGORY|default('[ประเภท]')}}ที่ใช้{{ATTACK_VECTOR|default('[รูปแบบการโจมตี]')}}เป็นเวกเตอร์หลัก ตาม TTP {{TTP_IDS|default('[MITRE IDs]')}} |
| **{{AFFECTED_ASSET|default('[อุปกรณ์]')}}** | ระบบ{{ASSET_TYPE|default('OT/ICS')}}ยี่ห้อ{{ASSET_VENDOR|default('[ยี่ห้อ]')}}รุ่น{{ASSET_MODEL|default('[รุ่น]')}}ที่ได้รับผลกระทบจาก{{THREAT_NAME|default('ภัยคุกคาม')}} |
| **NCSA** | สำนักงานคณะกรรมการการรักษาความมั่นคงปลอดภัยไซเบอร์แห่งชาติ |
| **Security Level (SL)** | ระดับความปลอดภัยตาม IEC 62443 ({{SL_CURRENT|default('0')}} → {{SL_TARGET|default('0')}}, Gap {{SL_GAP|default('0')}}) |
| **CSIRT** | Computer Security Incident Response Team — ทีมตอบสนองต่อเหตุการณ์ไซเบอร์ขององค์กร |
| **Wisdom Pattern** | {{WISDOM_PATTERN_ID|default('[Pattern ID]')}} — {{WISDOM_STEPS|default('[ขั้นตอน]')}} |

## 3.2 คำย่อ

| คำย่อ | คำเต็ม |
|-------|--------|
| NCSA | สำนักงานคณะกรรมการการรักษาความมั่นคงปลอดภัยไซเบอร์แห่งชาติ |
| CII | หน่วยงานโครงสร้างพื้นฐานสำคัญทางสารสนเทศ |
| SCADA | Supervisory Control and Data Acquisition |
| ICS | Industrial Control System |
| DCS | Distributed Control System |
| PLC | Programmable Logic Controller |
| CISO | Chief Information Security Officer |
| CSIRT | Computer Security Incident Response Team |
| TTP | Tactics, Techniques, and Procedures (MITRE ATT&CK) |

---

# ============================================================================
# ส่วนที่ 4: บทบัญญัติทางกฎหมาย (Core 6 Protected — Verbatim)
# ============================================================================
# ⚠️ กฎหมายในส่วนนี้ได้รับการคุ้มครองโดย Core 6 Verbatim Registry
# ห้ามแก้ไขคำพูด ห้ามให้ AI สรุปหรือเขียนใหม่ ห้ามเปลี่ยนความหมาย
# หาก T1 Intel ขัดกับกฎหมาย → Override ด้วย Core 6 เสมอ
# ============================================================================

## 4.1 {{LEGAL_ARTICLE_58_TITLE|default('มาตรา 58 — การแจ้งเหตุภายใน 72 ชั่วโมง')}}

> **⚖️ ข้อกำหนดทางกฎหมาย — ห้ามแก้ไขคำพูด**
>
> **{{LEGAL_AUTHORITY_REFERENCE|default('พระราชบัญญัติการรักษาความมั่นคงปลอดภัยไซเบอร์ พ.ศ. 2562 — มาตรา 58')}}**
>
> *"{{LEGAL_ARTICLE_58_TEXT|default('หน่วยงาน CII ที่เกิดเหตุภัยคุกคามทางไซเบอร์ที่มีผลกระทบต่อความมั่นคงปลอดภัย ต้องแจ้งเหตุต่อ NCSA (สกมช.) ภายใน 72 ชั่วโมง นับแต่ทราบเหตุ โดยต้องระบุลักษณะเหตุ ผลกระทบ และมาตรการที่ดำเนินการแล้ว')}}*
>
> **📌 บทลงโทษ:** {{LEGAL_PENALTY_DESC|default('ฝ่าฝืนมาตรา 58 — ปรับสูงสุด 1,000,000 บาท + NCSA เปิดเผยชื่อต่อสาธารณะ')}}

## 4.2 {{LEGAL_ARTICLE_59_TITLE|default('มาตรา 59 — การแจ้งเหตุภายใน 24 ชั่วโมง (กรณีภัยคุกคามร้ายแรง)')}}

> **⚖️ ข้อกำหนดทางกฎหมาย — ห้ามแก้ไขคำพูด**
>
> *"{{LEGAL_ARTICLE_59_TEXT|default('ในกรณีที่เหตุการณ์มีลักษณะร้ายแรงหรืออาจกระทบต่อความมั่นคงของรัฐ ต้องแจ้งภายใน 24 ชั่วโมง')}}*

## 4.3 มาตรฐานสากลที่สอดคล้อง (Standards Mapping)

| มาตรฐาน | Clause | คำอธิบาย |
|---------|--------|----------|
| {{MAPPED_STANDARD_CLAUSE_1|default('IEC 62443-2-1 EVENT 1.2')}} | {{MAPPED_STANDARD_DESC_1|default('องค์กรต้องมีกระบวนการรายงานเหตุการณ์ที่เป็นเอกสาร')}} | ข้อกำหนดนี้สอดคล้องกับ{{LEGAL_AUTHORITY_REFERENCE|default('มาตรา 58')}} |
| {{MAPPED_STANDARD_CLAUSE_2|default('IEC 62443-2-1 EVENT 1.3')}} | {{MAPPED_STANDARD_DESC_2|default('องค์กรต้องมีช่องทาง/อินเทอร์เฟซสำหรับการรายงานเหตุการณ์')}} | NCSA Portal เป็นช่องทางที่เป็นไปตามข้อกำหนดนี้ |
| {{MAPPED_STANDARD_CLAUSE_3|default('IEC 62443-2-1 EVENT 1.8')}} | {{MAPPED_STANDARD_DESC_3|default('องค์กรต้องมี incident handling และ response ที่เป็นระบบ')}} | กระบวนการในนโยบายนี้เป็นไปตามข้อกำหนด |
| {{MAPPED_STANDARD_CLAUSE_4|default('NIST CSF RS.MA-2')}} | {{MAPPED_STANDARD_DESC_4|default('รายงานต่อหน่วยงานรัฐภายในเวลาที่กำหนด')}} | รองรับการแจ้งเหตุ{{VERIFIED_REPORTING_DEADLINE|default('72 ชม.')}} |

---

# ============================================================================
# ส่วนที่ 5: Layer 1 — นโยบายระดับผู้บริหาร (L1 Policy)
# ============================================================================

## 5.1 คำแถลงนโยบาย

**[{{CLIENT_NAME|default('[องค์กร]')}}]** ตระหนักว่าการดำเนินงานด้าน{{SECTOR_NAME|default('[ภาคส่วน]')}}ต้องอาศัยระบบ {{ASSET_TYPE|default('SCADA/ICS')}} ที่มีความต่อเนื่องและเชื่อถือได้ องค์กรจึงกำหนดนโยบายว่า:

1. องค์กรจะดำเนินการตอบสนองต่อเหตุการณ์ไซเบอร์อย่างเป็นระบบและมีประสิทธิภาพ เพื่อลดผลกระทบต่อการผลิตและบริการ

2. องค์กรจะปฏิบัติตามข้อกำหนดทางกฎหมายว่าด้วยการแจ้งเหตุต่อ{{LEGAL_AUTHORITY_NAME|default('สำนักงานคณะกรรมการการรักษาความมั่นคงปลอดภัยไซเบอร์แห่งชาติ (NCSA)')}}ภายใน {{VERIFIED_REPORTING_DEADLINE|default('72 ชั่วโมง')}} นับแต่ทราบเหตุ ตาม{{LEGAL_AUTHORITY_REFERENCE|default('มาตรา 58 แห่งพระราชบัญญัติฯ')}}

3. องค์กรจะรักษาความลับ ความถูกต้อง ความพร้อมใช้งาน และความสมบูรณ์ของข้อมูลเหตุการณ์เป็นหลักฐานทางกฎหมาย

4. องค์กรจะทบทวนและปรับปรุงกระบวนการตอบสนองต่อเหตุการณ์อย่างน้อยปีละ 1 ครั้ง หรือเมื่อมีเหตุการณ์สำคัญ

5. องค์กรกำหนดให้ระบบ{{AFFECTED_ASSET|default('[อุปกรณ์วิกฤต]')}}มี Security Level ไม่ต่ำกว่า **SL-{{SL_TARGET|default('0')}}** เพื่อรับมือกับภัยคุกคาม{{THREAT_NAME|default('[ชื่อภัย]')}}

**[ลายมือชื่อผู้บริหารสูงสุด] / [ตำแหน่ง] / [วันที่]**

*[Ref: {{LEGAL_AUTHORITY_REFERENCE|default('NCSA-58')}} / {{MAPPED_STANDARD_CLAUSE_1|default('IEC-EVENT-1.2')}} / {{MAPPED_STANDARD_CLAUSE_4|default('NIST-RS.MA-2')}}]*

---

# ============================================================================
# ส่วนที่ 6: Layer 2 — ขั้นตอนปฏิบัติ (L2 Procedure)
# ============================================================================

## 6.0 Smart Link: T1 Wisdom Injection

> **🔗 ขั้นตอนจาก T1 Wisdom Database ({{WISDOM_PATTERN_ID|default('[Pattern ID]')}})**
>
> จากการวิเคราะห์{{THREAT_NAME|default('[ชื่อภัยคุกคาม]')}}ผ่าน{{ATTACK_VECTOR|default('[เวกเตอร์]')}}ที่โจมตี{{AFFECTED_ASSET|default('[อุปกรณ์]')}} T1 แนะนำขั้นตอนดังนี้:
>
> **{{WISDOM_STEPS|default('[ขั้นตอนจาก Wisdom Database จะแสดงที่นี่]')}}**
>
>