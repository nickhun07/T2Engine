# T2 Tri-Core v2.0 — Core 6 Sample Dataset
## NCSA / พ.ร.บ.ไซเบอร์ Atomic Requirements (3 ข้อ)

> สร้างจากข้อมูลจริง: มาตรฐานการรักษาความมั่นคงปลอดภัยสำหรับเว็บไซต์ พ.ศ. 2568 (NCSA), มาตรา 45-58 พ.ร.บ.ไซเบอร์ 2562
> วันที่สร้าง: 2026-04-04
> สถานะ: TEST SET — ยังไม่ผ่าน Mapping Validation

---

## ข้อค้นพบสำคัญเรื่องภาษา

### ❓ คำถามจาก Nik: มีคำศัพท์ EN ปนใน TH หรือไม่?

**คำตอบ: มี และเยอะกว่าที่คาด** ✅

จากการวิเคราะห์ข้อความจริงใน NCSA Standards:
- ข้อความ TH ล้วน: `การกำหนดบทบาทและสิทธิ์การใช้งาน`, `การจัดการทรัพย์สิน`, `การประเมินความเสี่ยง`
- คำ EN ปนโดดๆ: **MFA**, **Firewall**, **WAF**, **IPS/IDS**, **XDR**, **SIEM**, **SOAR**, **DevSecOps**, **OWASP**, **RTO**, **RPO**, **MTPD**, **BYOD**
- คำผสม TH-EN: `Multi-Factor Authentication (MFA)`, `Privileged user`, `Access authorization`

**ผลกระทบต่อ Vector Search:**
- ข้อดี: คำ EN เช่น "MFA" ตรงกับ IEC 62443 SR-1.3 ได้เลย → ลด semantic gap
- ข้อต้องระวัง: TH ล้วนอย่าง `การกำหนดบทบาทและสิทธิ์การใช้งาน` ต้องพึ่ง keywords
- **แนะนำ:** เติม EN keywords ใน Schema `keywords` field ให้ครบ

---

## SAMPLE 1: NCSA — การควบคุมการเข้าถึง (Access Control)

```json
{
  "req_id": "TH-NCSA-WEB-7-1",
  "source_metadata": {
    "law_name": "มาตรฐานการรักษาความมั่นคงปลอดภัยสำหรับเว็บไซต์ พ.ศ. 2568",
    "section": "หมวด 2 การป้องกัน — การควบคุมการเข้าถึง",
    "article_no": "ข้อ 7 (1)",
    "enforcement_date": "2025-09-01",
    "jurisdiction": "Thailand",
    "applicability": "หน่วยงานของรัฐ, หน่วยงาน CII, หน่วยงานควบคุม/กำกับดูแล"
  },
  "requirement_details": {
    "verbatim_text": "ต้องมีการกำหนดบทบาทและสิทธิ์การใช้งาน (Access Authorization) ของผู้ใช้งานระบบ โดยอย่างน้อยต้องครอบคลุม (1) การกำหนดสิทธิ์ตามหน้าที่ (Role-based Access Control) (2) การจำกัดสิทธิ์ของผู้ใช้ที่มีสิทธิ์สูง (Privileged User) (3) การทบทวนสิทธิ์การเข้าถึงเป็นรายไตรมาส",
    "keywords_th": ["สิทธิ์การใช้งาน", "การเข้าถึง", "บทบาท", "ผู้ใช้งาน", "Privileged User"],
    "keywords_en": ["Access Control", "RBAC", "Role-based Access", "Privileged User", "Authorization", "Least Privilege"],
    "penalty_context": "ฝ่าฝืนมาตรา 54 ต้องปรับไม่เกิน 200,000 บาท + ส่งรายงานให้ NCSA ทุกปี",
    "cross_reference_law": "พ.ร.บ.ไซเบอร์ มาตรา 27 (การรักษาข้อมูลส่วนบุคคล)"
  },
  "mapping_hints": {
    "suggested_iec_62443_reference": ["IEC 62443-3-3 SR 1.1 (User Identification)", "IEC 62443-3-3 SR 1.3 (Use Control)", "IEC 62443-2-1 4.3.3.5 (Role-based Access Control)"],
    "maturity_level": "Foundational",
    "package_tier": "Base — ฿95K ขึ้นไป",
    "difficulty": "Medium — มีคำ EN ปน แต่ nested sentence ยาว"
  }
}
```

---

## SAMPLE 2: NCSA — MFA (Multi-Factor Authentication)

```json
{
  "req_id": "TH-NCSA-WEB-7-2",
  "source_metadata": {
    "law_name": "มาตรฐานการรักษาความมั่นคงปลอดภัยสำหรับเว็บไซต์ พ.ศ. 2568",
    "section": "หมวด 2 การป้องกัน — การพิสูจน์ตัวตน",
    "article_no": "ข้อ 7 (2)",
    "enforcement_date": "2025-09-01",
    "jurisdiction": "Thailand",
    "applicability": "หน่วยงานของรัฐ, หน่วยงาน CII"
  },
  "requirement_details": {
    "verbatim_text": "ต้องมีการพิสูจน์ตัวตนแบบหลายปัจจัย (Multi-Factor Authentication: MFA) สำหรับผู้ดูแลระบบ (Administrator) และผู้ใช้งานที่มีสิทธิ์สูง (Privileged User) ทุกราย ทุกช่องทางการเข้าถึง รวมถึงการเข้าถึงผ่านระบบ Network และ Cloud Service",
    "keywords_th": ["พิสูจน์ตัวตน", "หลายปัจจัย", "MFA", "ผู้ดูแลระบบ", "Administrator"],
    "keywords_en": ["MFA", "Multi-Factor Authentication", "Privileged User", "Administrator", "2FA", "Authentication"],
    "penalty_context": "ฝ่าฝืนมาตรา 54 — เข้าข่ายความผิดร้ายแรง (High Penalty) เพราะเกี่ยวข้องกับ CII → ปรับสูงสุด + ต้องรายงานภายใน 72 ชม.",
    "cross_reference_law": "NIS2 Article 21(j) — บังคับ MFA สำหรับ privileged accounts"
  },
  "mapping_hints": {
    "suggested_iec_62443_reference": ["IEC 62443-3-3 SR 1.2 (Software/Device Authentication)", "IEC 62443-2-1 4.3.3.6 (Multifactor Authentication)"],
    "maturity_level": "Foundational",
    "package_tier": "Base — ฿95K ขึ้นไป (MFA ต้องมีในทุกเล่ม)",
    "difficulty": "Low — คำ EN ชัดเจน MFA ตรงกับ IEC เป๊ะ"
  }
}
```

---

## SAMPLE 3: NCSA — การป้องกันมัลแวร์ (Malware Protection)

```json
{
  "req_id": "TH-NCSA-WEB-7-3",
  "source_metadata": {
    "law_name": "มาตรฐานการรักษาความมั่นคงปลอดภัยสำหรับเว็บไซต์ พ.ศ. 2568",
    "section": "หมวด 2 การป้องกัน — การป้องกันมัลแวร์และการตรวจจับ",
    "article_no": "ข้อ 7 (3)",
    "enforcement_date": "2025-09-01",
    "jurisdiction": "Thailand",
    "applicability": "หน่วยงาน CII เท่านั้น (บังคับ)"
  },
  "requirement_details": {
    "verbatim_text": "ต้องจัดให้มีระบบป้องกันมัลแวร์ (Malware Protection) และระบบตรวจจับการบุกรุก (Intrusion Detection System/Intrusion Prevention System: IDS/IPS) ที่เชื่อมต่อกับระบบเครือข่าย โดยมีการ Monitoring ตลอด 24 ชั่วโมง และมีการจัดทำ Log การตรวจจับทุก 30 วัน",
    "keywords_th": ["มัลแวร์", "การบุกรุก", "ตรวจจับ", "เครือข่าย", "การเฝ้าระวัง"],
    "keywords_en": ["Malware", "IDS", "IPS", "Intrusion Detection", "Intrusion Prevention", "Security Monitoring", "XDR", "EDR"],
    "penalty_context": "มาตรา 54(3): หน่วยงาน CII ฝ่าฝืน → ปรับสูงสุด 200,000 บาท + สถานะ NCSA Blacklist",
    "cross_reference_law": "พ.ร.บ.ไซเบอร์ มาตรา 53 — ต้องประเมินความเสี่ยงและเฝ้าระวังภัยร่วมทดสอบความพร้อม"
  },
  "mapping_hints": {
    "suggested_iec_62443_reference": ["IEC 62443-3-3 SR 3.1 (Malicious Code Protection)", "IEC 62443-3-3 SR 3.4 (Software/Firmware Integrity)", "IEC 62443-2-1 4.3.3.4 (Monitoring")]
    "maturity_level": "Advanced",
    "package_tier": "Pro — ฿165K ขึ้นไป (ต้องมี Log + 24/7 monitoring)",
    "difficulty": "Medium-High — มีคำย่อ EN หลายตัว (IDS/IPS/XDR/EDR)"
  }
}
```

---

## SAMPLE 4: พ.ร.บ.ไซเบอร์ มาตรา 54 — การประเมินตนเอง (Self-Assessment)

```json
{
  "req_id": "TH-CYBER-54",
  "source_metadata": {
    "law_name": "พระราชบัญญัติการรักษาความมั่นคงปลอดภัยไซเบอร์ พ.ศ. 2562",
    "section": "หมวด 5 การรักษาความมั่นคงปลอดภัยไซเบอร์",
    "article_no": "มาตรา 54",
    "enforcement_date": "2022-05-28",
    "jurisdiction": "Thailand",
    "applicability": "หน่วยงาน CII ทุกแห่ง"
  },
  "requirement_details": {
    "verbatim_text": "หน่วยงาน CII ต้องจัดให้มีการประเมินตนเอง (Self-Assessment) เทียบกับมาตรฐานขั้นต่ำที่ กปช. กำหนด อย่างน้อยปีละ 1 ครั้ง และต้องจัดทำรายงานผลการประเมินพร้อมหลักฐาน เสนอต่อผู้บริหารสูงสุดของหน่วยงาน และเก็บไว้เพื่อให้ NCSA ตรวจสอบได้",
    "keywords_th": ["ประเมินตนเอง", "มาตรฐานขั้นต่ำ", "รายงาน", "หลักฐาน", "NCSA"],
    "keywords_en": ["Self-Assessment", "CII", "NCSA", "Compliance", "Audit", "Evidence"],
    "penalty_context": "ฝ่าฝืนมาตรา 54: ปรับไม่เกิน 200,000 บาท หรือจำคุกไม่เกิน 1 ปี หรือทั้งปรับทั้งจำ — และเป็นฐานผิดต่อเนื่อง (ฝ่าฝืนทุกวัน = ผิดทุกวัน)",
    "cross_reference_law": "มาตรา 52 — Regulator ตรวจสอบมาตรฐานขั้นต่ำของ CII ได้, มาตรา 53 — ต้องประเมินความเสี่ยง + เฝ้าระวังภัยร่วมทดสอบความพร้อม"
  },
  "mapping_hints": {
    "suggested_iec_62443_reference": ["IEC 62443-2-1 4.2 (Security Program Assessment)", "IEC 62443-2-1 4.3 (Management Review)"],
    "maturity_level": "Foundational",
    "package_tier": "Base — ฿95K ขึ้นไป (นี่คือฐานของทุกเล่ม — Self-Assessment ต้องมีเสมอ)",
    "difficulty": "Low — ภาษา TH ล้วน แต่ scope กว้างมาก"
  }
}
```

---

## SAMPLE 5: พ.ร.บ.ไซเบอร์ มาตรา 58 — การแจ้งเหตุ (Incident Reporting)

```json
{
  "req_id": "TH-CYBER-58",
  "source_metadata": {
    "law_name": "พระราชบัญญัติการรักษาความมั่นคงปลอดภัยไซเบอร์ พ.ศ. 2562",
    "section": "หมวด 5 การรักษาความมั่นคงปลอดภัยไซเบอร์",
    "article_no": "มาตรา 58",
    "enforcement_date": "2022-05-28",
    "jurisdiction": "Thailand",
    "applicability": "หน่วยงาน CII ที่เกิดเหตุภัยคุกคามทางไซเบอร์"
  },
  "requirement_details": {
    "verbatim_text": "หน่วยงาน CII ที่เกิดเหตุภัยคุกคามทางไซเบอร์ที่มีผลกระทบต่อความมั่นคงปลอดภัย ต้องแจ้งเหตุต่อ NCSA (สกมช.) ภายใน 72 ชั่วโมง นับแต่ทราบเหตุ โดยต้องระบุลักษณะเหตุ ผลกระทบ และมาตรการที่ดำเนินการแล้ว",
    "keywords_th": ["แจ้งเหตุ", "เหตุภัยคุกคาม", "NCSA", "72 ชั่วโมง", "รายงาน"],
    "keywords_en": ["Incident Report", "NCSA", "72 hours", "Cyber Incident", "Breach Notification", "CII"],
    "penalty_context": "มาตรา 58 + มาตรา 59: ไม่แจ้งภายนอก 72 ชม. → ปรับสูงสุด 1,000,000 บาท (5เท่าของมาตรา 54) + ข่าวชื่อเสียง NCSA เปิดเผยสู่สาธารณะ",
    "cross_reference_law": "NIS2 Article 23 — แจ้ง incident 24h (สำหรับ EU) / มาตรา 57 — แจ้งเหตุภายใน 24 ชม. กรณีภัยคุกคามร้ายแรง"
  },
  "mapping_hints": {
    "suggested_iec_62443_reference": ["IEC 62443-2-1 4.3.3.7 (Incident Handling)", "IEC 62443-2-1 4.8 (Reporting)"],
    "maturity_level": "Foundational",
    "package_tier": "Base — ฿95K ขึ้นไป (ทุกเล่มต้องมี Incident Response Timeline)",
    "difficulty": "Low — คำชัดเจน แต่มีเรื่อง 72h vs 24h ต้องแยกให้ดี"
  }
}
```

---

## สรุป: ความพร้อม Step 3

| ข้อ | ภาษา | EN ปน | ความยาก | หมายเหตุ |
|-----|------|-------|---------|---------|
| TH-NCSA-WEB-7-1 | TH+EN | Medium | Medium | RBAC, Access Control |
| TH-NCSA-WEB-7-2 | TH+EN | High | Low | MFA — EN ชัดเจน |
| TH-NCSA-WEB-7-3 | TH+EN | High | Med-High | IDS/IPS/XDR — คำย่อเยอะ |
| TH-CYBER-54 | TH ล้วน | None | Low | Scope กว้าง — ใช้ keywords |
| TH-CYBER-58 | TH ล้วน | None | Low | 72h vs 24h ต้อง distinguish |

**สรุปคำตอบคำถาม Nik:**
> มีคำ EN ปน และเยอะพอสมควร — โดยเฉพาะใน NCSA Website Standard
> → Vector Search สามารถจับคู่ได้โดยตรงผ่านคำ EN เหล่านี้
> → แต่ข้อ TH ล้วน (มาตรา 54, 58) ต้องพึ่ง `keywords_en` ใน Schema
> → **แนะนำ: เติม `keywords_en` ทุก requirement เสมอ**

พร้อมแล้วครับ — รอ Step 3: Mapping Logic 🚀
