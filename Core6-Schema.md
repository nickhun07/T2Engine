# T2 Tri-Core v2.0 — Core 6 (Regulator KB) Schema

## Source
From: Nik (User Message - Step 2)
Date: 2026-04-04

## JSON Schema — Atomic Requirements
```json
{
  "req_id": "TH-NCSA-BASE-01",
  "source_metadata": {
    "law_name": "ประกาศคณะกรรมการ กปช. เรื่อง มาตรฐานขั้นต่ำฯ",
    "section": "หมวด 2 การป้องกัน (Protection)",
    "article_no": "ข้อ 7 (1)",
    "enforcement_date": "2024-01-01",
    "jurisdiction": "Thailand"
  },
  "requirement_details": {
    "verbatim_text": "หน่วยงาน CII ต้องจัดให้มีมาตรการบริหารจัดการสิทธิ์และการเข้าถึง (Identity and Access Management)...",
    "keywords": ["Access Control", "IAM", "Authentication", "CII"],
    "penalty_context": "ฝ่าฝืนมาตรา 54 แห่ง พ.ร.บ. ไซเบอร์ (โทปรับไม่เกิน 200,000 บาท)"
  },
  "mapping_hints": {
    "suggested_iec_62443_reference": ["3-3 FR 1", "2-1 SP.05"],
    "maturity_level": "Foundational"
  }
}
```

## 3 ชั้นป้องกันการปนมาตรา (Anti-Mix-up)
1. **req_id Hard Constraint** — Filter by req_id prefix ก่อน search
2. **Vector Space Segmentation** — แยก index ตาม law_name
3. **Double-Check Validator** — ตรวจ req_id vs article_no ก่อน output

## Verbatim Rule
- verbatim_text → ห้าม AI แก้ ห้าม paraphrase
- keywords/summary → สร้างสำหรับ Vector Search (ภาษาอังกฤษ-ไทย ต่างกัน)

## Penalty Context
ใช้สร้าง "Urgency" ในเล่ม ฿395K → เขียนคำโปรยได้ "ขลัง"

## Maturity Tagging
- Foundational = บังคับทุกคน → เล่ม Base
- Advanced = แนะนำถ้าพร้อม → เล่ม Enterprise

## Action: Build Core 6 Sample Dataset
สร้าง 3-5 requirements จาก ประกาศ NCSA มาตรฐานขั้นต่ำ ตาม Schema ข้างบน
