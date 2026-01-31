from odoo import models, fields

class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Chức vụ'

    name = fields.Char(string='Tên chức vụ', required=True)
    mo_ta = fields.Text(string='Mô tả')
