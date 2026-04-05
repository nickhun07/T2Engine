# core6-regulator — ฐานข้อมูลกฎหมายและข้อบังคับสำหรับ T1 RAG

## โครงสร้างโฟลเดอร์

```
core6-regulator/
├── thai-cyber/         ← พ.ร.บ. ไซเบอร์ + NCSA
├── energy/             ← กฟผ., กฟน., กฟภ. + IEC 62443
├── nerc-cip/           ← NERC CIP (US Energy)
├── nis2/               ← NIS2 Directive (EU)
├── iso27001/           ← ISO 27001:2022
├── pdpa/               ← พ.ร.บ.คุ้มครองข้อมูลส่วนบุคคล
└── nist/              ← NIST CSF, 800-82, 800-53
```

## วิธีเพิ่มเอกสาร

1. **สร้างไฟล์** `.md` หรือ `.txt` ใน folder ที่เหมาะสม
2. **ตั้งชื่อให้สื่อ** เช่น `ncsa-cii-notification-procedure.md`
3. **รัน indexer:**

```bash
cd /root/.openclaw/workspace/t1-tricore/group2-indexers/rag-sync
python3 rag-regulator-indexer.py
```

## รูปแบบเอกสารที่ดี

```markdown
## มาตรา 58 — การแจ้งเหตุ (พ.ร.บ.ไซเบอร์ พ.ศ. 2562)

### ข้อกำหนดหลัก
- หน่วยงาน CII ต้องแจ้งเหตุภายใน 72 ชั่วโมง
- ช่องทาง: NCSA Portal (https://ncsa.go.th)
- ข้อมูลที่ต้องแจ้ง: ลักษณะเหตุ ผลกระทบ มาตรการ

### บทลงโทษ
- ปรับสูงสุด 1,000,000 บาท
- NCSA เปิดเผยชื่อต่อสาธารณะ

### เอกสารอ้างอิง
- พ.ร.บ.การรักษาความมั่นคงปลอดภัยไซเบอร์ พ.ศ. 2562
- ประกาศ NCSA เรื่อง หลักเกณฑ์การแจ้งเหตุ
```

## เอกสารที่ต้องการ (Priority Order)

### 🔴 P1 — Thai Cyber Law (เพิ่มก่อน)
- [ ] พ.ร.บ.การรักษาความมั่นคงปลอดภัยไซเบอร์ พ.ศ. 2562 (ฉบับเต็ม)
- [ ] NCSA CII Notification Procedure
- [ ] NCSA Minimum Cybersecurity Standards (Jan 2025)
- [ ] ประกาศ NCSA เรื่อง มาตรการรักษาความมั่นคงปลอดภัย (2025)

### 🟠 P2 — Energy Sector
- [ ] กฟผ. OT Security Requirements
- [ ] IEC 62443-2-1 (Security Program)
- [ ] IEC 62443-3-3 (System Security)
- [ ] NERC CIP-003 through CIP-014

### 🟡 P3 — EU/International
- [ ] NIS2 Directive (2022)
- [ ] ISO 27001:2022 Annex A
- [ ] NIST CSF 2.0
- [ ] NIST 800-82 Rev.3 (OT Security)

### 🟢 P4 — Data Protection
- [ ] PDPA (พ.ร.บ.คุ้มครองข้อมูลส่วนบุคคล)
- [ ] ISO 27701 (Privacy Extension)

---

**หลังเพิ่มไฟล์ → รัน `python3 rag-regulator-indexer.py` ที่ OpenClaw**
