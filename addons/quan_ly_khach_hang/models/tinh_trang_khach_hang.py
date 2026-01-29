# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TinhTrangKhachHang(models.Model):
    _name = 'tinh.trang.khach.hang'
    _description = 'Tình Trạng Khách Hàng'
    _order = 'name'

    name = fields.Char(string='Tên tình trạng', required=True)
    mo_ta = fields.Text(string='Mô tả')
    mau_sac = fields.Integer(string='Màu sắc')
    active = fields.Boolean(string='Hoạt động', default=True)
    
    # Trường thống kê
    so_khach_hang = fields.Integer(string='Số khách hàng', compute='_compute_so_khach_hang')
    
    @api.depends('name')
    def _compute_so_khach_hang(self):
        for record in self:
            record.so_khach_hang = self.env['customer'].search_count([
                ('tinh_trang_khach_hang_id', '=', record.id)
            ])
