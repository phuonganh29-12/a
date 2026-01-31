from odoo import models, fields

class PhongBan(models.Model):
    _name = 'phong_ban'
    _description = 'Phòng ban'

    name = fields.Char(string='Tên phòng ban', required=True)
    ghi_chu = fields.Text(string='Ghi chú')
