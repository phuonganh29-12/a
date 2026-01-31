from odoo import models, fields

class ChamCong(models.Model):
    _name = 'cham_cong'
    _description = 'Chấm công'

    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân viên', required=True)
    ngay = fields.Date(string='Ngày', required=True)
    gio_vao = fields.Float(string='Giờ vào')
    gio_ra = fields.Float(string='Giờ ra')
