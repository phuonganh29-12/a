from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError
import re


class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'ho_ten'
    _sql_constraints = [
        ('ma_dinh_danh_unique', 'unique(ma_dinh_danh)', 'Mã định danh nhân viên phải là duy nhất!'),
    ]

    # Thông tin cơ bản
    ma_dinh_danh = fields.Char("Mã nhân viên", required=True, index=True, copy=False, default="New", tracking=True)
    ho_ten_dem = fields.Char("Họ tên đệm", required=True)
    ten = fields.Char("Tên", required=True)
    ho_ten = fields.Char("Họ tên đầy đủ", compute='_compute_ho_ten', store=True)
    
    # Thông tin cá nhân
    ngay_sinh = fields.Date("Ngày sinh", tracking=True)
    tuoi = fields.Integer(string='Tuổi', compute='_compute_tuoi', store=True)
    gioi_tinh = fields.Selection([
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác')
    ], string="Giới tính", tracking=True)
    que_quan = fields.Char("Quê quán")
    dia_chi_hien_tai = fields.Char("Địa chỉ hiện tại")
    cccd = fields.Char("Số CCCD/CMND")
    
    # Thông tin liên hệ
    email = fields.Char("Email", tracking=True)
    so_dien_thoai = fields.Char("Số điện thoại", tracking=True)
    
    # Thông tin công việc
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban", ondelete='set null', tracking=True)
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ", ondelete='set null', tracking=True)
    ngay_vao_lam = fields.Date("Ngày vào làm", tracking=True)
    ngay_nghi_viec = fields.Date("Ngày nghỉ việc", tracking=True)
    trang_thai = fields.Selection([
        ('working', 'Đang làm việc'),
        ('probation', 'Thử việc'),
        ('leave', 'Nghỉ phép'),
        ('quit', 'Đã nghỉ việc')
    ], string="Trạng thái", default='working', required=True, tracking=True)
    
    # Hợp đồng lao động - ĐÃ TẮT
    # hop_dong_ids = fields.One2many('hop_dong_lao_dong', 'nhan_vien_id', string="Hợp đồng lao động")
    # hop_dong_hien_tai_id = fields.Many2one('hop_dong_lao_dong', string="Hợp đồng hiện tại", 
    #                                        compute='_compute_hop_dong_hien_tai', store=False)
    # so_hop_dong = fields.Integer("Số hợp đồng", compute='_compute_so_hop_dong', store=True)
    
    # Thông tin khác
    active = fields.Boolean("Hoạt động", default=True)
    image = fields.Binary("Ảnh", attachment=True)
    ghi_chu = fields.Text("Ghi chú")
    
    # Quan hệ
    lich_su_lam_viec_ids = fields.One2many('lich_su_lam_viec', 'nhan_vien_id', string="Lịch sử làm việc")
    
    # Computed fields
    so_nam_kinh_nghiem = fields.Integer("Số năm kinh nghiệm", compute='_compute_so_nam_kinh_nghiem', store=True)

    @api.depends("ngay_sinh")
    def _compute_tuoi(self):
        """Tính tuổi từ ngày sinh"""
        today = date.today()
        for record in self:
            if record.ngay_sinh:
                record.tuoi = today.year - record.ngay_sinh.year - (
                    (today.month, today.day) < (record.ngay_sinh.month, record.ngay_sinh.day)
                )
            else:
                record.tuoi = 0

    @api.depends("ho_ten_dem", "ten")
    def _compute_ho_ten(self):
        """Tính họ tên đầy đủ từ họ tên đệm và tên"""
        for record in self:
            if record.ho_ten_dem and record.ten:
                record.ho_ten = f"{record.ho_ten_dem} {record.ten}"
            elif record.ten:
                record.ho_ten = record.ten
            elif record.ho_ten_dem:
                record.ho_ten = record.ho_ten_dem
            else:
                record.ho_ten = "Chưa có tên"

    @api.depends("ngay_vao_lam")
    def _compute_so_nam_kinh_nghiem(self):
        """Tính số năm kinh nghiệm"""
        today = date.today()
        for record in self:
            if record.ngay_vao_lam:
                years = today.year - record.ngay_vao_lam.year
                record.so_nam_kinh_nghiem = max(0, years)
            else:
                record.so_nam_kinh_nghiem = 0
    
    # @api.depends('hop_dong_ids')
    # def _compute_so_hop_dong(self):
    #     """Đếm số hợp đồng lao động"""
    #     for record in self:
    #         record.so_hop_dong = len(record.hop_dong_ids)
    
    # def _compute_hop_dong_hien_tai(self):
    #     """Lấy hợp đồng hiện tại (đang hiệu lực hoặc sắp hết hạn)"""
    #     for record in self:
    #         hop_dong = record.hop_dong_ids.filtered(
    #             lambda h: h.trang_thai in ['dang_hieu_luc', 'sap_het_han']
    #         ).sorted('ngay_bat_dau', reverse=True)
    #         # Đảm bảo trả về record hoặc False, không gán .id trực tiếp
    #         if hop_dong:
    #             record.hop_dong_hien_tai_id = hop_dong[0]
    #         else:
    #             record.hop_dong_hien_tai_id = False

    @api.constrains('email')
    def _check_email(self):
        """Validate email"""
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        for record in self:
            if record.email and not re.match(email_pattern, record.email):
                raise ValidationError(f"Email không hợp lệ: {record.email}")

    @api.constrains('so_dien_thoai')
    def _check_phone(self):
        """Validate số điện thoại Việt Nam"""
        phone_pattern = r'^(\+84|0)[1-9]\d{8,9}$'
        for record in self:
            if record.so_dien_thoai and not re.match(phone_pattern, record.so_dien_thoai):
                raise ValidationError("Số điện thoại không hợp lệ! Ví dụ: 0987654321 hoặc +84987654321")

    @api.constrains('ngay_sinh')
    def _check_ngay_sinh(self):
        """Kiểm tra ngày sinh hợp lệ"""
        today = date.today()
        for record in self:
            if record.ngay_sinh:
                if record.ngay_sinh > today:
                    raise ValidationError("Ngày sinh không được vượt quá ngày hiện tại!")
                age = today.year - record.ngay_sinh.year
                if age < 18:
                    raise ValidationError("Nhân viên phải từ 18 tuổi trở lên!")
                if age > 100:
                    raise ValidationError("Ngày sinh không hợp lệ!")

    @api.constrains('ngay_vao_lam', 'ngay_nghi_viec')
    def _check_ngay_lam_viec(self):
        """Kiểm tra ngày làm việc hợp lệ"""
        for record in self:
            if record.ngay_vao_lam and record.ngay_nghi_viec:
                if record.ngay_nghi_viec < record.ngay_vao_lam:
                    raise ValidationError("Ngày nghỉ việc không được trước ngày vào làm!")

    @api.model
    def create(self, vals):
        """Tạo mã nhân viên tự động"""
        if vals.get('ma_dinh_danh', 'New') == 'New':
            # Tìm mã lớn nhất hiện có
            max_record = self.search([], order='ma_dinh_danh desc', limit=1)
            if max_record and max_record.ma_dinh_danh.startswith('NV'):
                try:
                    next_num = int(max_record.ma_dinh_danh.replace('NV', '')) + 1
                except ValueError:
                    next_num = 1
            else:
                next_num = 1
            vals['ma_dinh_danh'] = f'NV{str(next_num).zfill(5)}'
        return super(NhanVien, self).create(vals)

    def name_get(self):
        """Hiển thị tên nhân viên"""
        result = []
        for record in self:
            name = f"[{record.ma_dinh_danh}] {record.ho_ten}"
            result.append((record.id, name))
        return result