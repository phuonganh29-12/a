from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PhongBan(models.Model):
    _name = 'phong_ban'
    _description = 'Bảng chứa thông tin phòng ban'
    _rec_name = 'ten_phong_ban'
    _sql_constraints = [
        ('ma_phong_ban_unique', 'unique(ma_phong_ban)', 'Mã phòng ban phải là duy nhất!'),
    ]

    # Thông tin cơ bản
    ma_phong_ban = fields.Char("Mã phòng ban", required=True, index=True)
    ten_phong_ban = fields.Char("Tên phòng ban", required=True)
    mo_ta = fields.Text("Mô tả")
    
    # Phòng ban cha (để tạo cấu trúc cây)
    parent_id = fields.Many2one('phong_ban', string="Phòng ban cha", ondelete='cascade')
    child_ids = fields.One2many('phong_ban', 'parent_id', string="Phòng ban con")
    
    # Quản lý
    truong_phong_id = fields.Many2one('nhan_vien', string="Trưởng phòng", ondelete='set null')
    
    # Thông tin khác
    active = fields.Boolean("Hoạt động", default=True)
    ngay_thanh_lap = fields.Date("Ngày thành lập")
    
    # Quan hệ
    nhan_vien_ids = fields.One2many('nhan_vien', 'phong_ban_id', string="Nhân viên")
    
    # Computed fields
    so_nhan_vien = fields.Integer("Số nhân viên", compute='_compute_so_nhan_vien', store=True)

    @api.depends('nhan_vien_ids')
    def _compute_so_nhan_vien(self):
        """Tính số lượng nhân viên trong phòng ban"""
        for record in self:
            record.so_nhan_vien = len(record.nhan_vien_ids)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        """Kiểm tra không được tạo vòng lặp phòng ban"""
        if not self._check_recursion():
            raise ValidationError('Không thể tạo phòng ban cha tạo vòng lặp!')

    def name_get(self):
        """Hiển thị tên phòng ban"""
        result = []
        for record in self:
            name = f"[{record.ma_phong_ban}] {record.ten_phong_ban}"
            result.append((record.id, name))
        return result