from odoo import models, fields

class ChungChi(models.Model):
    _name = 'chung_chi'
    _description = 'Chứng chỉ'

    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân viên', required=True)
    ten_chung_chi = fields.Char(string='Tên chứng chỉ', required=True)
    ngay_cap = fields.Date(string='Ngày cấp')
    noi_cap = fields.Char(string='Nơi cấp')
