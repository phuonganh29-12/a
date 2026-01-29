# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class EmailMarketingCampaign(models.Model):
    _name = 'email.marketing.campaign'
    _description = 'Chiến dịch Email Marketing'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'ngay_tao desc, id desc'
    
    # Thông tin cơ bản
    name = fields.Char("Tên chiến dịch", required=True, tracking=True)
    ma_chien_dich = fields.Char("Mã chiến dịch", required=True, copy=False, 
                                default="New", index=True, tracking=True)
    mo_ta = fields.Text("Mô tả")
    
    # Template
    email_template_id = fields.Many2one('email.marketing.template', string="Mẫu email", 
                                        required=True, tracking=True)
    
    # Đối tượng
    doi_tuong = fields.Selection([
        ('all', 'Tất cả khách hàng'),
        ('filter', 'Lọc theo điều kiện'),
        ('manual', 'Chọn thủ công')
    ], string="Đối tượng gửi", required=True, default='all', tracking=True)
    
    # Điều kiện lọc
    loai_khach_hang_ids = fields.Many2many('loai.khach.hang', 
                                           relation='campaign_loai_kh_rel',
                                           column1='campaign_id',
                                           column2='loai_khach_hang_id',
                                           string="Loại khách hàng")
    tinh_trang_ids = fields.Many2many('tinh.trang.khach.hang', 
                                      relation='campaign_tinh_trang_rel',
                                      column1='campaign_id',
                                      column2='tinh_trang_id',
                                      string="Tình trạng")
    nguon_khach_ids = fields.Many2many('nguon.khach.hang', 
                                       relation='campaign_nguon_kh_rel',
                                       column1='campaign_id',
                                       column2='nguon_khach_hang_id',
                                       string="Nguồn khách hàng")
    
    # Chọn thủ công
    customer_ids = fields.Many2many('customer', 
                                    relation='campaign_customer_rel',
                                    column1='campaign_id',
                                    column2='customer_id',
                                    string="Khách hàng")
    
    # Thời gian
    ngay_tao = fields.Datetime("Ngày tạo", default=fields.Datetime.now, readonly=True)
    ngay_gui_du_kien = fields.Datetime("Ngày gửi dự kiến", tracking=True)
    ngay_gui_thuc_te = fields.Datetime("Ngày gửi thực tế", readonly=True, tracking=True)
    
    # Trạng thái
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('scheduled', 'Đã lên lịch'),
        ('sending', 'Đang gửi'),
        ('sent', 'Đã gửi'),
        ('cancelled', 'Đã hủy')
    ], string="Trạng thái", default='draft', required=True, tracking=True)
    
    # Thống kê
    tong_khach_hang = fields.Integer("Tổng KH", compute='_compute_tong_khach_hang', store=True)
    so_email_gui = fields.Integer("Số email đã gửi", readonly=True)
    so_email_thanh_cong = fields.Integer("Gửi thành công", readonly=True)
    so_email_that_bai = fields.Integer("Gửi thất bại", readonly=True)
    so_email_mo = fields.Integer("Số email đã mở", readonly=True)
    so_click = fields.Integer("Số lượt click", readonly=True)
    
    # Tỷ lệ
    ty_le_thanh_cong = fields.Float("Tỷ lệ thành công (%)", compute='_compute_ty_le', store=True)
    ty_le_mo = fields.Float("Tỷ lệ mở (%)", compute='_compute_ty_le', store=True)
    ty_le_click = fields.Float("Tỷ lệ click (%)", compute='_compute_ty_le', store=True)
    
    # Kết quả
    email_log_ids = fields.One2many('email.marketing.log', 'campaign_id', string="Lịch sử gửi")
    
    active = fields.Boolean("Active", default=True)
    ghi_chu = fields.Text("Ghi chú")
    
    @api.depends('doi_tuong', 'customer_ids', 'loai_khach_hang_ids', 'tinh_trang_ids', 'nguon_khach_ids')
    def _compute_tong_khach_hang(self):
        """Tính tổng số khách hàng sẽ nhận email"""
        for record in self:
            if record.doi_tuong == 'all':
                record.tong_khach_hang = self.env['customer'].search_count([('email', '!=', False)])
            elif record.doi_tuong == 'filter':
                domain = [('email', '!=', False)]
                if record.loai_khach_hang_ids:
                    domain.append(('loai_khach_hang_id', 'in', record.loai_khach_hang_ids.ids))
                if record.tinh_trang_ids:
                    domain.append(('tinh_trang_khach_hang_id', 'in', record.tinh_trang_ids.ids))
                if record.nguon_khach_ids:
                    domain.append(('nguon_khach_hang_id', 'in', record.nguon_khach_ids.ids))
                record.tong_khach_hang = self.env['customer'].search_count(domain)
            elif record.doi_tuong == 'manual':
                record.tong_khach_hang = len(record.customer_ids.filtered(lambda c: c.email))
            else:
                record.tong_khach_hang = 0
    
    @api.depends('so_email_gui', 'so_email_thanh_cong', 'so_email_mo', 'so_click')
    def _compute_ty_le(self):
        """Tính các tỷ lệ thống kê"""
        for record in self:
            if record.so_email_gui > 0:
                record.ty_le_thanh_cong = (record.so_email_thanh_cong / record.so_email_gui) * 100
                record.ty_le_mo = (record.so_email_mo / record.so_email_gui) * 100
                record.ty_le_click = (record.so_click / record.so_email_gui) * 100
            else:
                record.ty_le_thanh_cong = 0
                record.ty_le_mo = 0
                record.ty_le_click = 0
    
    @api.model
    def create(self, vals):
        """Tạo mã chiến dịch tự động"""
        if vals.get('ma_chien_dich', 'New') == 'New':
            vals['ma_chien_dich'] = self.env['ir.sequence'].next_by_code('email.marketing.campaign') or 'New'
        return super(EmailMarketingCampaign, self).create(vals)
    
    def action_schedule(self):
        """Lên lịch gửi"""
        self.ensure_one()
        if not self.ngay_gui_du_kien:
            raise ValidationError("Vui lòng chọn ngày gửi dự kiến!")
        if self.tong_khach_hang == 0:
            raise ValidationError("Không có khách hàng nào được chọn!")
        self.write({'trang_thai': 'scheduled'})
        self.message_post(body=f"Chiến dịch đã được lên lịch gửi vào {self.ngay_gui_du_kien.strftime('%d/%m/%Y %H:%M')}")
    
    def action_send_now(self):
        """Gửi email ngay"""
        self.ensure_one()
        if self.tong_khach_hang == 0:
            raise ValidationError("Không có khách hàng nào được chọn!")
        
        return {
            'name': 'Gửi Email Marketing',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.send.email.marketing',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_campaign_id': self.id}
        }
    
    def action_cancel(self):
        """Hủy chiến dịch"""
        self.ensure_one()
        self.write({'trang_thai': 'cancelled'})
        self.message_post(body="Chiến dịch đã bị hủy")
    
    def action_view_logs(self):
        """Xem lịch sử gửi email"""
        self.ensure_one()
        return {
            'name': 'Lịch sử gửi email',
            'type': 'ir.actions.act_window',
            'res_model': 'email.marketing.log',
            'view_mode': 'tree,form',
            'domain': [('campaign_id', '=', self.id)],
            'context': {'default_campaign_id': self.id}
        }
    
    def _get_customers(self):
        """Lấy danh sách khách hàng theo điều kiện"""
        self.ensure_one()
        if self.doi_tuong == 'all':
            return self.env['customer'].search([('email', '!=', False)])
        elif self.doi_tuong == 'filter':
            domain = [('email', '!=', False)]
            if self.loai_khach_hang_ids:
                domain.append(('loai_khach_hang_id', 'in', self.loai_khach_hang_ids.ids))
            if self.tinh_trang_ids:
                domain.append(('tinh_trang_khach_hang_id', 'in', self.tinh_trang_ids.ids))
            if self.nguon_khach_ids:
                domain.append(('nguon_khach_hang_id', 'in', self.nguon_khach_ids.ids))
            return self.env['customer'].search(domain)
        elif self.doi_tuong == 'manual':
            return self.customer_ids.filtered(lambda c: c.email)
        return self.env['customer']


class EmailMarketingLog(models.Model):
    _name = 'email.marketing.log'
    _description = 'Lịch sử gửi Email Marketing'
    _rec_name = 'customer_id'
    _order = 'ngay_gui desc, id desc'
    
    campaign_id = fields.Many2one('email.marketing.campaign', string="Chiến dịch", 
                                  required=True, ondelete='cascade')
    customer_id = fields.Many2one('customer', string="Khách hàng", required=True, ondelete='cascade')
    email = fields.Char("Email", related='customer_id.email', store=True)
    
    ngay_gui = fields.Datetime("Ngày gửi", default=fields.Datetime.now)
    trang_thai = fields.Selection([
        ('success', 'Thành công'),
        ('failed', 'Thất bại'),
        ('bounced', 'Bị trả về')
    ], string="Trạng thái", required=True, default='success')
    
    da_mo = fields.Boolean("Đã mở", default=False)
    ngay_mo = fields.Datetime("Ngày mở")
    so_lan_mo = fields.Integer("Số lần mở", default=0)
    
    da_click = fields.Boolean("Đã click", default=False)
    ngay_click = fields.Datetime("Ngày click")
    so_lan_click = fields.Integer("Số lần click", default=0)
    
    loi = fields.Text("Lỗi (nếu có)")
    ghi_chu = fields.Text("Ghi chú")
