from odoo import models, fields, api


class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Bảng chứa thông tin chức vụ'
    _rec_name = 'ten_chuc_vu'
    _sql_constraints = [
        ('ma_chuc_vu_unique', 'unique(ma_chuc_vu)', 'Mã chức vụ phải là duy nhất!'),
    ]

    # Thông tin cơ bản
    ma_chuc_vu = fields.Char("Mã chức vụ", required=True, index=True)
    ten_chuc_vu = fields.Char("Tên chức vụ", required=True)
    mo_ta = fields.Text("Mô tả công việc")
    
    # Cấp bậc
    cap_bac = fields.Integer("Cấp bậc", help="Số càng lớn cấp bậc càng cao")
    
    # Thông tin khác
    active = fields.Boolean("Hoạt động", default=True)
    
    # Quan hệ
    nhan_vien_ids = fields.One2many('nhan_vien', 'chuc_vu_id', string="Nhân viên")
    
    # Computed fields
    so_nhan_vien = fields.Integer("Số nhân viên", compute='_compute_so_nhan_vien', store=True)

    @api.depends('nhan_vien_ids')
    def _compute_so_nhan_vien(self):
        """Tính số lượng nhân viên có chức vụ này"""
        for record in self:
            record.so_nhan_vien = len(record.nhan_vien_ids)

    def name_get(self):
        """Hiển thị tên chức vụ"""
        result = []
        for record in self:
            name = f"[{record.ma_chuc_vu}] {record.ten_chuc_vu}"
            result.append((record.id, name))
        return result