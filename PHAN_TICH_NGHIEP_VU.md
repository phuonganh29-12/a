# PHÂN TÍCH NGHIỆP VỤ TÍCH HỢP 3 MODULE
## Quản lý Khách hàng + Quản lý Văn bản + Nhân sự

---

## 📋 MỤC LỤC
1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Phân tích nghiệp vụ từng module](#2-phân-tích-nghiệp-vụ-từng-module)
3. [Phân tích nghiệp vụ tích hợp](#3-phân-tích-nghiệp-vụ-tích-hợp)
4. [Thiết kế database](#4-thiết-kế-database)
5. [Kế hoạch phát triển](#5-kế-hoạch-phát-triển)

---

## 1. TỔNG QUAN Dự ÁN

### 1.1 Mục tiêu
Xây dựng hệ thống tích hợp quản lý toàn diện:
- **Quản lý khách hàng (CRM)**: Lưu trữ thông tin, theo dõi tương tác, đơn hàng
- **Quản lý văn bản**: Quản lý văn bản đến/đi, loại văn bản, lưu trữ tài liệu
- **Quản lý nhân sự (HR)**: Quản lý nhân viên, phòng ban, chức vụ, lịch sử làm việc

### 1.2 Yêu cầu từ hình ảnh
> **"Sổ hóa hồ sơ: Toàn bộ hợp đồng, báo giá, tài liệu pháp lý được gắn trực tiếp vào hồ sơ khách hàng để tra cứu tập trung."**

**Ý nghĩa:**
- Mọi văn bản liên quan đến khách hàng phải được lưu trữ tập trung
- Dễ dàng tra cứu, quản lý hồ sơ khách hàng
- Liên kết giữa khách hàng - văn bản - nhân viên phụ trách

---

## 2. PHÂN TÍCH NGHIỆP VỤ TỪNG MODULE

### 2.1 MODULE QUẢN LÝ KHÁCH HÀNG (quan_ly_khach_hang)

#### 2.1.1 Hiện trạng
**Models có sẵn:**
1. `customer` - Khách hàng
2. `crm_lead` - Cơ hội bán hàng
3. `crm_interact` - Tương tác khách hàng
4. `contract` - Hợp đồng
5. `sale_order` - Đơn hàng
6. `feedback` - Phản hồi
7. `note` - Ghi chú
8. `project_task` - Nhiệm vụ dự án
9. `marketing_campaign` - Chiến dịch marketing
10. `employee` - Nhân viên (nội bộ module)
11. `crm_stage` - Giai đoạn cơ hội

#### 2.1.2 Nghiệp vụ chính
1. **Quản lý thông tin khách hàng**
   - Phân loại: Cá nhân/Công ty
   - Thông tin cơ bản: Tên, email, SĐT, địa chỉ, ngày sinh
   - Validation: Email, SĐT theo format Việt Nam
   - Tự động tăng mã khách hàng

2. **Quản lý tương tác**
   - Loại tương tác: Cuộc gọi, Email, Meeting
   - Ghi nhận nhân viên phụ trách
   - Thống kê số lần tương tác

3. **Quản lý hợp đồng**
   - Trạng thái: Đang hoạt động/Đã kết thúc
   - Liên kết với khách hàng

4. **Quản lý đơn hàng**
   - Lịch sử giao dịch
   - Tổng giá trị đơn hàng
   - Thống kê doanh thu

5. **Email Marketing**
   - Gửi email sinh nhật
   - Gửi email chào mừng

#### 2.1.3 Computed Fields
- `age` - Tuổi (từ ngày sinh)
- `age_group` - Nhóm tuổi
- `sale_order_group` - Nhóm theo số đơn hàng
- `total_contracts` - Tổng số hợp đồng
- `total_interactions` - Tổng số tương tác
- `total_sale_orders` - Tổng số đơn hàng
- `total_amount` - Tổng doanh thu
- `near_birthday` - Gần sinh nhật (7 ngày)

---

### 2.2 MODULE QUẢN LÝ VĂN BẢN (quan_ly_van_ban)

#### 2.2.1 Hiện trạng
**Models có sẵn:**
1. `van_ban_den` - Văn bản đến
2. `van_ban_di` - Văn bản đi
3. `loai_van_ban` - Loại văn bản

#### 2.2.2 Cấu trúc hiện tại

**Model: van_ban_den**
- `so_van_ban_den` - Số hiệu văn bản
- `ten_van_ban` - Tên văn bản
- `so_hieu_van_ban` - Số hiệu văn bản (trùng?)
- `noi_gui_den` - Nơi gửi đến

**Model: van_ban_di**
- `ma_dinh_danh` - Tên văn bản

**Model: loai_van_ban**
- `ma_loai_van_ban` - Mã loại
- `ten_loai_van_ban` - Tên loại

#### 2.2.3 Vấn đề cần giải quyết
❌ **Thiếu các trường quan trọng:**
- Không có file đính kèm (attachment)
- Không có ngày văn bản
- Không có trích yếu/nội dung
- Không có người ký
- Không có độ ưu tiên/mức độ bảo mật
- Không liên kết với khách hàng
- Không liên kết với nhân viên phụ trách

---

### 2.3 MODULE NHÂN SỰ (nhan_su)

#### 2.3.1 Hiện trạng
**Models có sẵn:**
1. `nhan_vien` - Nhân viên
2. `phong_ban` - Phòng ban
3. `chuc_vu` - Chức vụ
4. `lich_su_lam_viec` - Lịch sử làm việc

#### 2.3.2 Cấu trúc hiện tại

**Model: nhan_vien**
- `ma_dinh_danh` - Mã nhân viên
- `ho_ten_dem` - Họ tên đệm
- `ten` - Tên
- `ho_ten` - Họ tên đầy đủ (computed)
- `ngay_sinh` - Ngày sinh (kiểu Integer - SAI)
- `tuoi` - Tuổi (computed)
- `gioi_tinh` - Giới tính
- `que_quan` - Quê quán
- `email` - Email
- `so_dien_thoai` - Số điện thoại
- `lich_su_lam_viec_ids` - Lịch sử làm việc

**Model: phong_ban**
- `ma_phong_ban` - Mã phòng ban
- `ten_phong_ban` - Tên phòng ban

**Model: chuc_vu**
- `ma_chuc_vu` - Mã chức vụ
- `ten_chuc_vu` - Tên chức vụ

**Model: lich_su_lam_viec**
- `nhan_vien_id` - Nhân viên

#### 2.3.3 Vấn đề cần giải quyết
❌ **Các lỗi và thiếu sót:**
1. `ngay_sinh` là Integer thay vì Date
2. Thiếu liên kết `nhan_vien` với `phong_ban`
3. Thiếu liên kết `nhan_vien` với `chuc_vu`
4. Model `lich_su_lam_viec` chỉ có 1 trường
5. Thiếu trường ngày vào làm, trạng thái làm việc
6. Module `employee` trong `quan_ly_khach_hang` và `nhan_vien` trong `nhan_su` bị trùng nghiệp vụ

---

## 3. PHÂN TÍCH NGHIỆP VỤ TÍCH HỢP

### 3.1 Mối quan hệ giữa các module

```
                    ┌─────────────────┐
                    │   NHÂN VIÊN     │
                    │   (nhan_su)     │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                │                         │
                ▼                         ▼
    ┌──────────────────┐      ┌──────────────────┐
    │  KHÁCH HÀNG      │      │   VĂN BẢN        │
    │(quan_ly_khach_   │◄────►│(quan_ly_van_ban) │
    │      hang)       │      │                  │
    └──────────────────┘      └──────────────────┘
```

### 3.2 Các nghiệp vụ tích hợp cần phát triển

#### 3.2.1 **Gắn văn bản vào hồ sơ khách hàng**

**Use Cases:**

**UC1: Tạo hợp đồng cho khách hàng**
- Actor: Nhân viên kinh doanh
- Mô tả: 
  1. Nhân viên tạo văn bản loại "Hợp đồng"
  2. Chọn khách hàng liên quan
  3. Upload file PDF hợp đồng
  4. Hệ thống tự động gắn văn bản vào hồ sơ khách hàng
  5. Khách hàng có thể xem tất cả hợp đồng của mình

**UC2: Tạo báo giá cho khách hàng**
- Actor: Nhân viên kinh doanh
- Mô tả:
  1. Tạo văn bản loại "Báo giá"
  2. Liên kết với khách hàng
  3. Upload file báo giá
  4. Ghi nhận ngày gửi, hạn hiệu lực

**UC3: Lưu trữ tài liệu pháp lý**
- Actor: Nhân viên pháp lý
- Mô tả:
  1. Upload giấy tờ pháp lý của khách hàng (GPKD, MST, etc.)
  2. Gắn vào hồ sơ khách hàng
  3. Phân loại theo loại văn bản

**UC4: Tra cứu hồ sơ tập trung**
- Actor: Nhân viên bất kỳ
- Mô tả:
  1. Vào hồ sơ khách hàng
  2. Xem tab "Văn bản liên quan"
  3. Thấy tất cả: Hợp đồng, Báo giá, Tài liệu pháp lý
  4. Download/Preview văn bản

#### 3.2.2 **Quản lý nhân viên phụ trách**

**UC5: Phân công nhân viên phụ trách khách hàng**
- Actor: Quản lý
- Mô tả:
  1. Chọn khách hàng
  2. Phân công nhân viên kinh doanh phụ trách
  3. Nhân viên được thông báo
  4. Có thể xem danh sách khách hàng của mình

**UC6: Ghi nhận nhân viên soạn thảo văn bản**
- Actor: Nhân viên
- Mô tả:
  1. Khi tạo văn bản, tự động ghi nhận người tạo
  2. Có thể chỉ định người ký
  3. Có thể chỉ định người nhận (nếu văn bản đến)

**UC7: Thống kê hiệu suất nhân viên**
- Actor: Quản lý
- Mô tả:
  1. Xem số lượng khách hàng của mỗi nhân viên
  2. Số văn bản đã xử lý
  3. Số hợp đồng đã ký
  4. Doanh thu từ khách hàng phụ trách

#### 3.2.3 **Quy trình nghiệp vụ tích hợp**

**Quy trình 1: Từ Cơ hội → Hợp đồng → Đơn hàng**

```
1. Nhận thông tin khách hàng tiềm năng
   └─> Tạo CRM Lead (crm_lead)
   └─> Phân công nhân viên (nhan_vien)

2. Tương tác với khách hàng
   └─> Ghi nhận tương tác (crm_interact)
   └─> Gửi báo giá (van_ban_di loại "Báo giá")

3. Khách hàng đồng ý
   └─> Chuyển Lead thành Customer (customer)
   └─> Tạo hợp đồng (contract)
   └─> Upload văn bản hợp đồng (van_ban_di loại "Hợp đồng")
   └─> Gắn vào hồ sơ khách hàng

4. Thực hiện giao dịch
   └─> Tạo đơn hàng (sale_order)
   └─> Tạo hóa đơn (van_ban_di loại "Hóa đơn")

5. Sau bán hàng
   └─> Thu thập feedback (feedback)
   └─> Lưu ghi chú (note)
```

**Quy trình 2: Xử lý văn bản đến từ khách hàng**

```
1. Văn bản đến từ khách hàng
   └─> Tạo văn bản đến (van_ban_den)
   └─> Gắn với khách hàng (customer)
   └─> Phân công nhân viên xử lý (nhan_vien)

2. Nhân viên xử lý
   └─> Ghi nhận tương tác (crm_interact)
   └─> Tạo task nếu cần (project_task)

3. Trả lời khách hàng
   └─> Tạo văn bản đi (van_ban_di)
   └─> Liên kết với văn bản đến (trả lời)
```

---

## 4. THIẾT KẾ DATABASE

### 4.1 Sửa đổi/Bổ sung Model VĂN BẢN

#### 4.1.1 Model: van_ban_di (Văn bản đi)

**Cần bổ sung:**
```python
# Thông tin cơ bản
so_van_ban = fields.Char("Số văn bản", required=True)
ten_van_ban = fields.Char("Tên văn bản", required=True)
trich_yeu = fields.Text("Trích yếu")
noi_dung = fields.Html("Nội dung")

# Phân loại
loai_van_ban_id = fields.Many2one('loai_van_ban', string="Loại văn bản")
do_uu_tien = fields.Selection([
    ('low', 'Thấp'),
    ('normal', 'Bình thường'),
    ('high', 'Cao'),
    ('urgent', 'Khẩn cấp')
], default='normal')

# Thời gian
ngay_van_ban = fields.Date("Ngày văn bản", required=True)
ngay_gui = fields.Date("Ngày gửi")
han_xu_ly = fields.Date("Hạn xử lý")

# File đính kèm
attachment_ids = fields.Many2many('ir.attachment', string="File đính kèm")

# Liên kết
customer_id = fields.Many2one('customer', string="Khách hàng")
nhan_vien_soan_thao_id = fields.Many2one('nhan_vien', string="Người soạn thảo")
nguoi_ky_id = fields.Many2one('nhan_vien', string="Người ký")
don_vi_nhan = fields.Char("Đơn vị nhận")

# Trạng thái
trang_thai = fields.Selection([
    ('draft', 'Nháp'),
    ('waiting', 'Chờ ký'),
    ('signed', 'Đã ký'),
    ('sent', 'Đã gửi')
], default='draft')
```

#### 4.1.2 Model: van_ban_den (Văn bản đến)

**Cần bổ sung:**
```python
# Thông tin cơ bản
so_van_ban = fields.Char("Số văn bản", required=True)
ten_van_ban = fields.Char("Tên văn bản", required=True)
trich_yeu = fields.Text("Trích yếu")

# Phân loại
loai_van_ban_id = fields.Many2one('loai_van_ban', string="Loại văn bản")
do_uu_tien = fields.Selection([...])

# Thời gian
ngay_van_ban = fields.Date("Ngày văn bản")
ngay_nhan = fields.Date("Ngày nhận", required=True)
han_xu_ly = fields.Date("Hạn xử lý")

# File đính kèm
attachment_ids = fields.Many2many('ir.attachment', string="File đính kèm")

# Liên kết
customer_id = fields.Many2one('customer', string="Từ khách hàng")
nhan_vien_xu_ly_id = fields.Many2one('nhan_vien', string="Người xử lý")
don_vi_gui = fields.Char("Đơn vị gửi")

# Xử lý
trang_thai = fields.Selection([
    ('new', 'Mới nhận'),
    ('processing', 'Đang xử lý'),
    ('replied', 'Đã trả lời'),
    ('archived', 'Lưu trữ')
], default='new')
van_ban_tra_loi_id = fields.Many2one('van_ban_di', string="Văn bản trả lời")
```

### 4.2 Sửa đổi Model NHÂN VIÊN

#### 4.2.1 Sửa lỗi model nhan_vien

```python
# SỬA
ngay_sinh = fields.Date("Ngày sinh")  # Đổi từ Integer sang Date

# BỔ SUNG
phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban")
chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ")
ngay_vao_lam = fields.Date("Ngày vào làm")
trang_thai = fields.Selection([
    ('working', 'Đang làm việc'),
    ('leave', 'Nghỉ phép'),
    ('quit', 'Đã nghỉ việc')
], default='working')

# Liên kết với module khác
customer_phu_trach_ids = fields.Many2many('customer', string="Khách hàng phụ trách")
van_ban_di_ids = fields.One2many('van_ban_di', 'nhan_vien_soan_thao_id', string="Văn bản đã soạn")
van_ban_den_ids = fields.One2many('van_ban_den', 'nhan_vien_xu_ly_id', string="Văn bản cần xử lý")
```

### 4.3 Sửa đổi Model KHÁCH HÀNG

**Bổ sung vào model customer:**
```python
# Liên kết với nhân viên
nhan_vien_phu_trach_id = fields.Many2one('nhan_vien', string="Nhân viên phụ trách")

# Liên kết với văn bản
van_ban_di_ids = fields.One2many('van_ban_di', 'customer_id', string="Văn bản đi")
van_ban_den_ids = fields.One2many('van_ban_den', 'customer_id', string="Văn bản đến")

# Thống kê văn bản
total_van_ban = fields.Integer("Tổng số văn bản", compute="_compute_total_van_ban")
```

### 4.4 Loại bỏ trùng lặp

**Vấn đề:** Module `quan_ly_khach_hang` có model `employee`, module `nhan_su` có model `nhan_vien`

**Giải pháp:**
1. Xóa model `employee` trong `quan_ly_khach_hang`
2. Sửa tất cả tham chiếu `employee` thành `nhan_vien`
3. Module `quan_ly_khach_hang` sẽ depend vào module `nhan_su`

---

## 5. KẾ HOẠCH PHÁT TRIỂN

### 5.1 Giai đoạn 1: Chuẩn bị (2-3 ngày)

**Bước 1.1: Sửa lỗi module nhan_su**
- [ ] Sửa kiểu dữ liệu `ngay_sinh` từ Integer → Date
- [ ] Bổ sung trường `phong_ban_id`, `chuc_vu_id`
- [ ] Bổ sung trường `ngay_vao_lam`, `trang_thai`
- [ ] Sửa logic tính tuổi
- [ ] Test module nhan_su

**Bước 1.2: Loại bỏ trùng lặp**
- [ ] Backup database
- [ ] Migrate dữ liệu từ `employee` sang `nhan_vien`
- [ ] Xóa model `employee` trong quan_ly_khach_hang
- [ ] Sửa tất cả references
- [ ] Thêm dependency: quan_ly_khach_hang depends nhan_su
- [ ] Test migration

**Bước 1.3: Sửa/bổ sung module quan_ly_van_ban**
- [ ] Bổ sung các trường thiếu cho `van_ban_di`
- [ ] Bổ sung các trường thiếu cho `van_ban_den`
- [ ] Tạo view mới với đầy đủ trường
- [ ] Test module quan_ly_van_ban

### 5.2 Giai đoạn 2: Tích hợp (3-4 ngày)

**Bước 2.1: Tích hợp văn bản - khách hàng**
- [ ] Thêm trường `customer_id` vào van_ban_di
- [ ] Thêm trường `customer_id` vào van_ban_den
- [ ] Thêm trường `van_ban_di_ids`, `van_ban_den_ids` vào customer
- [ ] Tạo view "Văn bản" trong form khách hàng (notebook tab)
- [ ] Test tích hợp

**Bước 2.2: Tích hợp nhân viên - văn bản**
- [ ] Thêm trường nhân viên vào van_ban_di
- [ ] Thêm trường nhân viên vào van_ban_den
- [ ] Tạo domain filter: nhân viên chỉ thấy văn bản của mình
- [ ] Test phân quyền

**Bước 2.3: Tích hợp nhân viên - khách hàng**
- [ ] Thêm trường `nhan_vien_phu_trach_id` vào customer
- [ ] Thêm trường `customer_phu_trach_ids` vào nhan_vien
- [ ] Tạo view danh sách khách hàng của nhân viên
- [ ] Test phân công

### 5.3 Giai đoạn 3: Chức năng nâng cao (3-4 ngày)

**Bước 3.1: Upload/Download file**
- [ ] Tích hợp ir.attachment
- [ ] Tạo widget upload file trong form văn bản
- [ ] Tạo chức năng preview PDF
- [ ] Tạo chức năng download
- [ ] Test upload/download

**Bước 3.2: Quy trình phê duyệt văn bản**
- [ ] Tạo workflow: draft → waiting → signed → sent
- [ ] Tạo button chuyển trạng thái
- [ ] Gửi thông báo khi cần ký
- [ ] Test workflow

**Bước 3.3: Thống kê báo cáo**
- [ ] Báo cáo văn bản theo khách hàng
- [ ] Báo cáo văn bản theo nhân viên
- [ ] Báo cáo hợp đồng sắp hết hạn
- [ ] Dashboard tổng quan
- [ ] Test báo cáo

### 5.4 Giai đoạn 4: Hoàn thiện (2-3 ngày)

**Bước 4.1: Security & Access Rights**
- [ ] Cấu hình ir.model.access.csv
- [ ] Tạo security groups
- [ ] Phân quyền theo vai trò
- [ ] Test security

**Bước 4.2: UI/UX**
- [ ] Tối ưu giao diện
- [ ] Thêm icon, màu sắc
- [ ] Tạo menu hợp lý
- [ ] Test UX

**Bước 4.3: Testing & Documentation**
- [ ] Test tích hợp toàn bộ
- [ ] Viết user manual
- [ ] Viết technical documentation
- [ ] Demo cho stakeholder

---

## 6. DANH SÁCH LOẠI VĂN BẢN MẪU

```python
LOAI_VAN_BAN = [
    ('hop_dong', 'Hợp đồng'),
    ('bao_gia', 'Báo giá'),
    ('hoa_don', 'Hóa đơn'),
    ('bien_ban', 'Biên bản'),
    ('cong_van', 'Công văn'),
    ('thong_bao', 'Thông báo'),
    ('quyet_dinh', 'Quyết định'),
    ('tai_lieu_phap_ly', 'Tài liệu pháp lý'),
    ('giay_phep', 'Giấy phép'),
    ('chung_nhan', 'Chứng nhận'),
    ('don_khieu_nai', 'Đơn khiếu nại'),
    ('bao_cao', 'Báo cáo'),
    ('khac', 'Khác'),
]
```

---

## 7. KIẾN TRÚC HỆ THỐNG

### 7.1 Sơ đồ quan hệ Entity Relationship Diagram (ERD)

```
┌─────────────────────────────────────────────────────────────┐
│                     PHÒNG BAN                               │
│  - ma_phong_ban                                             │
│  - ten_phong_ban                                            │
└──────────────┬──────────────────────────────────────────────┘
               │
               │ Many2one
               │
┌──────────────▼──────────────────────────────────────────────┐
│                    NHÂN VIÊN                                │
│  - ma_dinh_danh                                             │
│  - ho_ten, email, sdt                                       │
│  - phong_ban_id (Many2one → phong_ban)                      │
│  - chuc_vu_id (Many2one → chuc_vu)                          │
│  - customer_phu_trach_ids (Many2many → customer)            │
└──────────────┬──────────────────────────────────────────────┘
               │
       ┌───────┼───────┐
       │               │
       │               │ One2many
       │               │
┌──────▼───────┐  ┌────▼────────────────────────────────────┐
│  VĂN BẢN ĐI  │  │          KHÁCH HÀNG                     │
│              │  │  - customer_id                          │
│  - customer  │  │  - customer_name, email, phone          │
│  - nhan_vien │◄─┤  - nhan_vien_phu_trach_id (Many2one)   │
│  - loai_vb   │  │  - van_ban_di_ids (One2many)            │
│  - file      │  │  - van_ban_den_ids (One2many)           │
└──────────────┘  │  - contract_ids                         │
                  │  - sale_order_ids                       │
┌──────────────┐  │  - interact_ids                         │
│ VĂN BẢN ĐẾN │  │                                         │
│              │  └─────────────────────────────────────────┘
│  - customer  │◄──┘
│  - nhan_vien │
│  - loai_vb   │
│  - file      │
└──────────────┘
```

---

## 8. CÁC USE CASE CHI TIẾT

### USE CASE 1: Tạo hợp đồng cho khách hàng mới

**Actor:** Nhân viên kinh doanh

**Precondition:** 
- Đã có thông tin khách hàng trong hệ thống
- Nhân viên đã đăng nhập

**Flow:**
1. Nhân viên vào menu "Văn bản đi" → Click "Tạo mới"
2. Điền thông tin:
   - Số văn bản: HD-2026-001
   - Tên: Hợp đồng cung cấp dịch vụ
   - Loại: Hợp đồng
   - Khách hàng: Chọn từ danh sách
   - Ngày văn bản: 27/01/2026
   - Hạn hiệu lực: 27/01/2027
3. Upload file PDF hợp đồng
4. Click "Lưu"
5. Hệ thống tự động:
   - Gán người soạn thảo = nhân viên hiện tại
   - Gắn văn bản vào hồ sơ khách hàng
   - Tạo bản ghi contract liên kết
6. Gửi thông báo cho quản lý ký duyệt

**Postcondition:**
- Văn bản được lưu với trạng thái "Chờ ký"
- Khách hàng có thể xem văn bản trong hồ sơ
- Quản lý nhận được thông báo

---

### USE CASE 2: Xử lý văn bản đến từ khách hàng

**Actor:** Nhân viên hành chính

**Flow:**
1. Nhận văn bản từ khách hàng (email/bưu điện)
2. Vào menu "Văn bản đến" → "Tạo mới"
3. Điền thông tin:
   - Số văn bản: Theo văn bản gốc
   - Từ khách hàng: Chọn customer
   - Ngày nhận: Hôm nay
   - Trích yếu: "Yêu cầu báo giá dịch vụ X"
4. Upload file scan văn bản
5. Phân công nhân viên xử lý
6. Hệ thống gửi thông báo cho nhân viên được phân công
7. Nhân viên xử lý văn bản và tạo văn bản trả lời

**Postcondition:**
- Văn bản đến được lưu và gắn với khách hàng
- Nhân viên xử lý nhận thông báo
- Có thể tracking trạng thái xử lý

---

### USE CASE 3: Tra cứu hồ sơ khách hàng

**Actor:** Nhân viên bất kỳ (có quyền)

**Flow:**
1. Vào menu "Khách hàng"
2. Tìm kiếm khách hàng (theo tên, mã, SĐT)
3. Mở form khách hàng
4. Click tab "Văn bản liên quan"
5. Xem danh sách:
   - Hợp đồng (5 bản)
   - Báo giá (3 bản)
   - Tài liệu pháp lý (2 bản)
   - Công văn (7 bản)
6. Click vào văn bản cần xem
7. Preview hoặc Download file

**Postcondition:**
- Nhân viên nắm được toàn bộ lịch sử văn bản với khách hàng
- Dễ dàng tra cứu khi cần

---

## 9. TỔNG KẾT

### 9.1 Lợi ích của hệ thống tích hợp

✅ **Quản lý tập trung:**
- Mọi thông tin về khách hàng ở một chỗ
- Không cần tìm kiếm văn bản rời rạc

✅ **Tăng hiệu quả làm việc:**
- Nhân viên dễ dàng tra cứu
- Quy trình xử lý văn bản rõ ràng
- Tự động hóa thông báo

✅ **Kiểm soát tốt hơn:**
- Biết ai đang phụ trách khách hàng nào
- Tracking văn bản đã gửi/nhận
- Báo cáo thống kê chính xác

✅ **Tuân thủ pháp lý:**
- Lưu trữ đầy đủ tài liệu
- Dễ dàng cung cấp khi cần audit
- Quản lý phiên bản văn bản

### 9.2 Rủi ro cần lưu ý

⚠️ **Migration dữ liệu:**
- Cần backup trước khi chuyển đổi
- Test kỹ trên môi trường dev

⚠️ **Performance:**
- Nhiều file đính kèm có thể làm chậm hệ thống
- Cần tối ưu database

⚠️ **Security:**
- Văn bản nhạy cảm cần mã hóa
- Phân quyền chặt chẽ

⚠️ **User adoption:**
- Cần đào tạo nhân viên sử dụng
- Hướng dẫn rõ ràng

---

**Tài liệu này là nền tảng để bắt đầu coding. Mọi thắc mắc xin liên hệ team leader.**
