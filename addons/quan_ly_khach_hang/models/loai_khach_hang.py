# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LoaiKhachHang(models.Model):
    _name = 'loai.khach.hang'
    _description = 'Loại Khách Hàng'
    _order = 'name'

    name = fields.Char(string='Tên loại khách hàng', required=True)
    mo_ta = fields.Text(string='Mô tả')
    active = fields.Boolean(string='Hoạt động', default=True)
    
    # Trường thống kê
    so_khach_hang = fields.Integer(string='Số khách hàng', compute='_compute_so_khach_hang')
    
    @api.depends('name')
    def _compute_so_khach_hang(self):
        for record in self:
            record.so_khach_hang = self.env['customer'].search_count([
                ('loai_khach_hang_id', '=', record.id)
            ])
