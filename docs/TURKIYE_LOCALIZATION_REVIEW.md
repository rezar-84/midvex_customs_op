# Türkiye Localization Review - midvex_customs_op

This document reviews how well the Import & Customs Operations module supports Turkey (Türkiye) customs processes (Gümrük İşlemleri) and evaluates operational terminology.

---

## 1. Customs Concepts Alignment

### A. GTİP (Gümrük Tarife İstatistik Pozisyonu)
* **Current Support**: The module defines `hs_code` in [product_template.py](file:///home/rubuntu/Projects/midvex_customs_op/models/product_template.py#L13) and [customs_operation_line.py](file:///home/rubuntu/Projects/midvex_customs_op/models/customs_operation_line.py#L30) with the string label "HS/GTİP Code".
* **Gaps**: Türkiye customs requires a 12-digit GTİP format. The field is currently a plain Char field without character validation. Lots of errors occur if typos are entered in GTİP codes.
* **Recommendation**: Add a Python regex constraint on `hs_code` verifying a 12-digit numeric format when the destination country is Turkey.

### B. Beyanname (Gümrük Beyannamesi)
* **Current Support**: The module includes `customs_declaration_number` and `customs_declaration_date` fields.
* **Gaps**: A Turkish customs declaration number is always a 16-digit alphanumeric reference (consisting of year, customs office code, regime code, and registration number, e.g. 26340000IM123456).
* **Recommendation**: Implement input mask validation for Turkish declaration numbers.

### C. Gümrük Müdürlüğü (Customs Office)
* **Current Support**: Model has a plain `customs_office` Char field.
* **Gaps**: Free-text fields lead to dirty database entries (e.g. "Ambarli", "Ambarlı Gümrük", "Ambarli Mud"). Turkey has a standard set of active customs offices (Gümrük Müdürlükleri) managed by the Ministry of Trade.
* **Recommendation**: Convert `customs_office` from a Char field to a Many2one referencing a new master model `customs.office` pre-seeded with Turkey's active customs ports (e.g. Ambarlı, Erenköy, Dilovası, Gemlik).

### D. Gümrük Müşaviri (Customs Broker)
* **Current Support**: `broker_id` Many2one links to standard partner contacts. This is fully sufficient.

### E. KKDF (Kaynak Kullanımını Destekleme Fonu)
* **Current Support**: Not represented. KKDF is a 6% tax applied to imports paid via credit/deferred payment terms (accepted as a cost on import).
* **Recommendation**: Add a specific monetary field `cost_kkdf` to the Costs tab and include it in `cost_total` computations.

### F. Damga Vergisi (Stamp Tax)
* **Current Support**: Supported via `cost_stamp_tax` on `customs.operation`.

### G. Ardiye & Antrepo (Storage & Bonded Warehouse)
* **Current Support**: Supported via `cost_storage` on `customs.operation`.
* **Gaps**: Does not differentiate between port demurrage (demurraj) and bonded warehouse storage (antrepo ardiye). These are handled by different vendors and have different tax/apportionment implications.
* **Recommendation**: Split `cost_storage` into `cost_demurrage` (Demurraj) and `cost_warehouse_storage` (Ardiye/Antrepo).

### H. Muayene (Inspection & Inspection Channels)
* **Current Support**: Operates via `inspection_required` and `inspection_date` boolean/date fields.
* **Gaps**: Turkey uses a 4-color routing channel system:
  * **Kırmızı Hat (Red Line)**: Physical check and document audit (Fiziki muayene ve belge kontrolü).
  * **Sarı Hat (Yellow Line)**: Document check only (Belge kontrolü).
  * **Mavi Hat (Blue Line)**: Post-clearance audit (Sonradan kontrol).
  * **Yeşil Hat (Green Line)**: Immediate clearance (Muayene yok).
* **Recommendation**: Add a selection field `customs_line_channel` with values `['red', 'yellow', 'blue', 'green']` labeled "Gümrük Muayene Hattı".

---

## 2. Import Cost Structures

Turkey imports involve complex tax structures. Here is the compliance status of current cost fields:

| Cost Type (Türkçe) | Field Code | Purpose | Validation Status |
|---|---|---|---|
| **Gümrük Vergisi** | `cost_customs_tax` | Customs Tax | OK |
| **KDV (KDV Matrahı)** | *Missing* | Value Added Tax (VAT) paid at customs | **Missing** - crucial for tax declarations. |
| **KKDF** | *Missing* | Deferred payment tax | **Missing** |
| **Damga Vergisi** | `cost_stamp_tax` | Stamp Tax on declaration | OK |
| **Ardiye / Antrepo** | `cost_storage` | Storage fees | OK |
| **Müşavirlik Ücreti** | `cost_broker_expenses` | Broker fee | OK |
| **Demurraj** | *Missing* | Ship/container delay fee | **Missing** (merged in storage) |
| **Ordino Ücreti** | *Missing* | Delivery Order fee | **Missing** (often goes to other) |

---

## 3. Operational Language (Terminology Review)

The Turkish translations in [tr_TR.po](file:///home/rubuntu/Projects/midvex_customs_op/i18n/tr_TR.po) were audited for natural flow:

* **Unnatural Labels Identified**:
  * `Warehouse Delivery` -> translated as "Depo Teslimi". **Fix**: Change to "Depoya Giriş Tarihi" or "Depo Kabul Tarihi".
  * `Damaged Product` -> translated as "Hasarlı Ürün". **Fix**: Change to "Hasarlı Ürün Tespit Edildi".
  * `Ready to Ship` -> translated as "Sevkıyata Hazır". **Fix**: Standard Turkish spelling is "Sevkiyata Hazır" (replace 'ı' with 'i').
  * `Customs Office` -> translated as "Gümrük Ofisi". **Fix**: In Turkey, this is always called "Gümrük Müdürlüğü".
