from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LichSuLamViec(models.Model):
    _name = 'lich_su_lam_viec'
    _description = 'Bảng chứa thông tin lịch sử làm việc'
    _order = 'ngay_bat_dau desc'

    # Thông tin cơ bản
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True, ondelete='cascade')
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban", required=True)
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ", required=True)
    
    # Thời gian
    ngay_bat_dau = fields.Date("Ngày bắt đầu", required=True)
    ngay_ket_thuc = fields.Date("Ngày kết thúc")
    
    # Loại thay đổi
    loai_thay_doi = fields.Selection([
        ('new_hire', 'Tuyển dụng mới'),
        ('promotion', 'Thăng chức'),
        ('transfer', 'Chuyển phòng ban'),
        ('demotion', 'Giáng chức'),
        ('termination', 'Nghỉ việc'),
        ('other', 'Khác')
    ], string="Loại thay đổi", required=True, default='new_hire')
    
    # Thông tin bổ sung
    ly_do = fields.Text("Lý do thay đổi")
    ghi_chu = fields.Text("Ghi chú")
    active = fields.Boolean("Hoạt động", default=True)
    
    # Computed field
    so_ngay = fields.Integer("Số ngày", compute='_compute_so_ngay', store=True)
    dang_ap_dung = fields.Boolean("Đang áp dụng", compute='_compute_dang_ap_dung', store=True)

    @api.depends('ngay_bat_dau', 'ngay_ket_thuc')
    def _compute_so_ngay(self):
        """Tính số ngày làm việc"""
        for record in self:
            if record.ngay_bat_dau:
                if record.ngay_ket_thuc:
                    delta = record.ngay_ket_thuc - record.ngay_bat_dau
                    record.so_ngay = delta.days
                else:
                    delta = fields.Date.today() - record.ngay_bat_dau
                    record.so_ngay = delta.days
            else:
                record.so_ngay = 0

    @api.depends('ngay_ket_thuc')
    def _compute_dang_ap_dung(self):
        """Kiểm tra xem lịch sử này có đang áp dụng không"""
        for record in self:
            record.dang_ap_dung = not record.ngay_ket_thuc

    @api.constrains('ngay_bat_dau', 'ngay_ket_thuc')
    def _check_dates(self):
        """Kiểm tra ngày tháng hợp lệ"""
        for record in self:
            if record.ngay_bat_dau and record.ngay_ket_thuc:
                if record.ngay_ket_thuc < record.ngay_bat_dau:
                    raise ValidationError("Ngày kết thúc không được trước ngày bắt đầu!")

    @api.constrains('nhan_vien_id', 'ngay_bat_dau', 'ngay_ket_thuc')
    def _check_overlap(self):
        """Kiểm tra không được trùng lặp lịch sử"""
        for record in self:
            domain = [
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('id', '!=', record.id),
            ]
            
            # Kiểm tra trùng lặp thời gian
            existing_records = self.search(domain)
            for existing in existing_records:
                # Nếu bản ghi hiện tại không có ngày kết thúc (đang áp dụng)
                if not record.ngay_ket_thuc:
                    if not existing.ngay_ket_thuc:
                        raise ValidationError(
                            "Nhân viên đã có lịch sử làm việc đang áp dụng khác! "
                            "Vui lòng kết thúc lịch sử cũ trước khi tạo mới."
                        )
                    if existing.ngay_ket_thuc >= record.ngay_bat_dau:
                        raise ValidationError("Thời gian làm việc bị trùng lặp!")
                
                # Nếu có ngày kết thúc
                elif record.ngay_ket_thuc:
                    if not existing.ngay_ket_thuc:
                        if record.ngay_ket_thuc >= existing.ngay_bat_dau:
                            raise ValidationError("Thời gian làm việc bị trùng lặp!")
                    else:
                        # Cả hai đều có ngày kết thúc
                        if not (record.ngay_ket_thuc < existing.ngay_bat_dau or 
                               record.ngay_bat_dau > existing.ngay_ket_thuc):
                            raise ValidationError("Thời gian làm việc bị trùng lặp!")

    def name_get(self):
        """Hiển thị tên"""
        result = []
        for record in self:
            name = f"{record.nhan_vien_id.ho_ten} - {record.phong_ban_id.ten_phong_ban} ({record.ngay_bat_dau})"
            result.append((record.id, name))
        return result
