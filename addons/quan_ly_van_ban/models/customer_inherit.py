# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CustomerInherit(models.Model):
    _inherit = 'customer'
    
    # Văn bản đi của khách hàng
    van_ban_count = fields.Integer("Số lượng văn bản", compute="_compute_van_ban_count", store=False)
    van_ban_ids = fields.One2many('van_ban_di', 'customer_id', string="Văn bản", readonly=True)
    
    # Tính toán số lượng văn bản của khách hàng
    def _compute_van_ban_count(self):
        for record in self:
            record.van_ban_count = len(record.van_ban_ids)
