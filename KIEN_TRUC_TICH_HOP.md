# KIẾN TRÚC TÍCH HỢP 3 MODULE

## 🔗 Mô hình liên kết giữa 3 module

```
┌─────────────────┐
│   NHAN_SU       │ (Module nền tảng)
│  (Nhân viên)    │
└────────┬────────┘
         │
         │ depends
         ↓
┌─────────────────┐         ┌──────────────────┐
│ QUAN_LY_KHACH_HANG │────────→│  QUAN_LY_VAN_BAN │
│  (Customer/CRM) │ depends │  (Văn bản)       │
└─────────────────┘         └──────────────────┘
```

## 📊 Chi tiết quan hệ

### 1. **Module NHAN_SU** (Độc lập)
**Models:**
- `nhan_vien` (Nhân viên)
- `phong_ban` (Phòng ban)
- `chuc_vu` (Chức vụ)
- `lich_su_lam_viec` (Lịch sử làm việc)

**Không phụ thuộc module nào** (chỉ phụ thuộc base, mail)

---

### 2. **Module QUAN_LY_KHACH_HANG** (Phụ thuộc nhan_su)
**Dependencies:** `['base', 'mail', 'nhan_su']`

**Models:**
- `customer` (Khách hàng)
- `crm_lead` (Cơ hội)
- `crm_interact` (Tương tác)
- `contract` (Hợp đồng)
- `feedback` (Phản hồi)
- `note` (Ghi chú)
- `project_task` (Nhiệm vụ)
- `marketing_campaign` (Chiến dịch marketing)

**Liên kết với nhan_su:**
- `customer.nhan_vien_phu_trach_id` → `nhan_vien`
- `crm_interact.employee_id` → `nhan_vien`
- `note.employee_id` → `nhan_vien`
- `feedback.employee_id` → `nhan_vien`
- `project_task.employee_id` → `nhan_vien`
- `marketing_campaign.employee_id` → `nhan_vien`

---

### 3. **Module QUAN_LY_VAN_BAN** (Phụ thuộc cả 2)
**Dependencies:** `['base', 'mail', 'nhan_su', 'quan_ly_khach_hang']`

**Models:**
- `loai_van_ban` (Loại văn bản: Hợp đồng, Báo giá, Tài liệu pháp lý...)
- `van_ban_di` (Văn bản đi: 6-state workflow)
- `van_ban_den` (Văn bản đến: 7-state workflow)

**Liên kết với nhan_su:**
- `van_ban_di.nhan_vien_soan_thao_id` → `nhan_vien`
- `van_ban_di.nguoi_ky_id` → `nhan_vien`
- `van_ban_den.nhan_vien_tiep_nhan_id` → `nhan_vien`

**Liên kết với quan_ly_khach_hang:**
- `van_ban_di.customer_id` → `customer`
- `van_ban_den.customer_id` → `customer`

**⚠️ Lưu ý quan trọng:**
- `customer` model KHÔNG có One2many ngược về văn bản (`van_ban_di_ids`, `van_ban_den_ids`) để tránh circular dependency
- Quan hệ chỉ một chiều: văn bản → khách hàng
- Có thể xem văn bản của khách hàng qua related fields hoặc view inheritance (chưa implement)

---

## 🆚 So sánh với Module Ban Đầu

### **MODULE BAN ĐẦU (Trước nâng cấp)**

#### quan_ly_van_ban:
❌ Lỗi circular import trong `__init__.py`
❌ Không có workflow states (chỉ có draft/sent)
❌ Không có loại văn bản
❌ Không liên kết với customer
❌ Không liên kết với nhân viên
❌ Không có file đính kèm
❌ Không có tracking (chatter)

#### quan_ly_khach_hang:
❌ Có model `employee` riêng (trùng lặp với nhan_su)
❌ Không liên kết với module nhan_su
❌ Không có văn bản tracking

#### nhan_su:
❌ Chưa có (hoặc rất cơ bản)

---

### **MODULE MỚI NHẤT (Sau nâng cấp)**

#### ✅ **NHAN_SU** - Module nền tảng
**Tính năng mới:**
- 4 models hoàn chỉnh với quan hệ Many2one/One2many
- Auto-generate mã nhân viên (NV-2026-0001)
- Mail.thread integration (chatter, tracking)
- Computed fields: `tuoi`, `tong_thoi_gian_lam_viec`
- Validations: email, phone, ngày sinh, ngày vào làm
- Views hiện đại với widget: badge, statusbar, graph

#### ✅ **QUAN_LY_VAN_BAN** - Quản lý văn bản chuyên nghiệp
**Tính năng mới:**

**1. Loại văn bản (loai_van_ban):**
- 9 loại predefined: Hợp đồng, Báo giá, Tài liệu pháp lý, Hóa đơn, Công văn, Thông báo, Quyết định, Giấy phép, Biên bản
- Thống kê số văn bản theo loại
- Màu sắc phân loại
- Hướng văn bản: đi/đến/cả hai

**2. Văn bản đi (van_ban_di):**
- **6-state workflow:** draft → waiting_approve → approved → waiting_sign → signed → sent (+ cancelled)
- Auto-numbering: VBĐ-2026-0001
- Liên kết: customer_id, nhan_vien_soan_thao_id, nguoi_ky_id
- File đính kèm (Many2many với ir.attachment)
- Computed fields: `qua_han`, `ngay_het_han`, `ngay_con_lai`
- Workflow buttons với attrs visibility
- Mail tracking đầy đủ

**3. Văn bản đến (van_ban_den):**
- **7-state workflow:** new → assigned → processing → waiting_reply → replied → completed → archived
- Dual numbering: `so_van_ban` (từ đơn vị gửi) + `so_den` (số nội bộ VBĐến-2026-0001)
- Tạo văn bản trả lời tự động
- Computed fields: `thoi_gian_xu_ly`, deadline tracking
- Liên kết: customer_id, nhan_vien_tiep_nhan_id

#### ✅ **QUAN_LY_KHACH_HANG** - CRM tích hợp
**Thay đổi quan trọng:**
- ❌ Xóa model `employee` riêng
- ✅ Dùng `nhan_vien` từ module nhan_su
- ✅ Tất cả 5 models (crm_interact, note, feedback, project_task, marketing_campaign) đều link đến `nhan_vien`
- ✅ customer.nhan_vien_phu_trach_id để assign nhân viên phụ trách
- ⚠️ Chưa có One2many `van_ban_di_ids/van_ban_den_ids` (để tránh circular dependency khi load module)

---

## 🎯 Tính năng "Sổ hóa hồ sơ" (Đã implement)

**Mục tiêu:** "Toàn bộ hợp đồng, báo giá, tài liệu pháp lý được gắn trực tiếp vào hồ sơ khách hàng để tra cứu tập trung"

### Cách hoạt động hiện tại:

1. **Tạo văn bản đi/đến:**
   - Chọn loại văn bản (Hợp đồng, Báo giá, Tài liệu pháp lý...)
   - Chọn khách hàng từ dropdown `customer_id`
   - Upload file đính kèm
   - Theo dõi workflow (phê duyệt, ký, gửi)

2. **Tra cứu từ khách hàng:**
   - Mở Customer record
   - Có thể search văn bản liên quan bằng filter `customer_id = [customer_name]`
   - (Hoặc thêm tab "Hồ sơ văn bản" bằng view inheritance - chưa implement để tránh circular dependency)

### Ưu điểm so với ban đầu:
✅ Văn bản được phân loại rõ ràng (9 loại)
✅ Workflow chặt chẽ, không bị sót bước
✅ Tracking đầy đủ lịch sử thay đổi
✅ File đính kèm chuyên nghiệp
✅ Deadline và overdue warning
✅ Link 2 chiều: văn bản ↔ khách hàng (qua customer_id)
✅ Link với nhân viên: ai soạn, ai ký, ai tiếp nhận
✅ Auto-numbering duy nhất

---

## 📦 Cấu trúc Database

**Database:** `dnu` (Fresh install)

**Module install order:**
1. `nhan_su` (không depend gì)
2. `quan_ly_khach_hang` (depends nhan_su)
3. `quan_ly_van_ban` (depends cả 2)

**⚠️ Không thể đảo ngược thứ tự!** Nếu không sẽ gặp KeyError khi load.

---

## 🔧 Các thay đổi kỹ thuật quan trọng

### Fix circular dependency:
- **Trước:** quan_ly_khach_hang ⟷ quan_ly_van_ban (lỗi không load được)
- **Sau:** quan_ly_khach_hang → quan_ly_van_ban (một chiều)

### Fix field references:
- **Trước:** employee_id → 'employee' (model không tồn tại)
- **Sau:** employee_id → 'nhan_vien' (từ module nhan_su)

### Fix default values:
- **Trước:** `default=lambda self: self.env.user.id` (gán res.users ID vào nhan_vien field → lỗi)
- **Sau:** Không dùng default, user tự chọn nhân viên

### Fix button states:
- **Trước:** `states="draft"` (tìm field tên 'state' → lỗi)
- **Sau:** `attrs="{'invisible': [('trang_thai', '!=', 'draft')]}"` (dùng field đúng)

### Fix view XML:
- **Trước:** Nhiều field trùng lặp, duplicate </page> tags
- **Sau:** Clean XML, không trùng lặp

---

## 📈 Roadmap tiếp theo (Chưa implement)

### Giai đoạn 2: View Integration
- Thêm tab "📁 Hồ sơ văn bản" vào customer form bằng view inheritance
- Smart buttons hiển thị số văn bản của khách hàng
- Computed field `total_van_ban` an toàn

### Giai đoạn 3: Automation
- Email tự động khi văn bản được gửi
- Notification deadline sắp hết hạn
- Workflow approval qua email

### Giai đoạn 4: Portal
- Customer portal xem văn bản của mình
- Download file đính kèm
- Ký điện tử

### Giai đoạn 5: Reporting
- Dashboard thống kê văn bản
- Báo cáo theo loại, theo khách hàng, theo nhân viên
- Phân tích hiệu suất xử lý

---

## 🎓 Bài học kinh nghiệm

1. **Dependency order quan trọng:** Phải design từ module độc lập → module phụ thuộc
2. **Tránh circular dependency:** Không để 2 module depend lẫn nhau
3. **Field references phải chính xác:** Đảm bảo comodel_name tồn tại khi load
4. **View inheritance > Direct edit:** Dùng inheritance để mở rộng view của module khác
5. **Testing incremental:** Test từng module một, rồi test tích hợp
6. **Database migration:** Có metadata cũ → phải tạo database mới
7. **Default values cẩn thận:** Không gán cross-model ID vào Many2one field

---

## ✅ Kết luận

**Module hiện tại đã hoàn thành:**
- ✅ Tích hợp 3 module chặt chẽ
- ✅ Workflow văn bản chuyên nghiệp
- ✅ Liên kết khách hàng - văn bản - nhân viên
- ✅ Sổ hóa hồ sơ cơ bản (qua customer_id)
- ✅ Không còn lỗi circular dependency
- ✅ Database clean, không conflicts

**Chức năng còn thiếu:**
- ⏳ View tab văn bản trong customer form (có thể thêm bằng inheritance)
- ⏳ Email automation
- ⏳ Advanced reporting
- ⏳ Customer portal

Nhưng **core functionality đã hoàn chỉnh và sẵn sàng sử dụng!**
