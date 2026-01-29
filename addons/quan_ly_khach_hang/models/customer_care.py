# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CustomerCare(models.Model):
    _name = 'customer.care'
    _description = 'Chăm sóc khách hàng'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'tieu_de'
    _order = 'ngay_cham_soc desc, id desc'
    
    # Thông tin cơ bản
    ma_cham_soc = fields.Char("Mã chăm sóc", required=True, copy=False, 
                              default="New", index=True, readonly=True)
    customer_id = fields.Many2one('customer', string="Khách hàng", required=True, 
                                  tracking=True, ondelete='cascade')
    
    # Loại chăm sóc
    loai_cham_soc = fields.Selection([
        ('call', 'Gọi điện'),
        ('email', 'Gửi email'),
        ('visit', 'Thăm hỏi trực tiếp'),
        ('gift', 'Tặng quà'),
        ('meeting', 'Họp gặp'),
        ('other', 'Khác')
    ], string="Loại chăm sóc", required=True, default='call', tracking=True)
    
    # Thông tin
    tieu_de = fields.Char("Tiêu đề", required=True, tracking=True)
    mo_ta = fields.Text("Mô tả", tracking=True)
    noi_dung = fields.Html("Nội dung chi tiết")
    
    # Người thực hiện
    nhan_vien_id = fields.Many2one('nhan_vien', string="Người thực hiện", 
                                   default=lambda self: self.env.user.id if self.env.user else False,
                                   tracking=True)
    
    # Thời gian
    ngay_du_kien = fields.Datetime("Ngày dự kiến", required=True, tracking=True,
                                    default=fields.Datetime.now)
    ngay_cham_soc = fields.Datetime("Ngày thực hiện", tracking=True)
    
    # Kết quả
    trang_thai = fields.Selection([
        ('planned', 'Đã lên kế hoạch'),
        ('in_progress', 'Đang thực hiện'),
        ('completed', 'Đã hoàn thành'),
        ('cancelled', 'Đã hủy')
    ], string="Trạng thái", default='planned', required=True, tracking=True)
    
    ket_qua = fields.Selection([
        ('very_good', 'Rất tốt'),
        ('good', 'Tốt'),
        ('normal', 'Bình thường'),
        ('not_good', 'Không tốt'),
        ('failed', 'Thất bại')
    ], string="Kết quả", tracking=True)
    
    phan_hoi_khach_hang = fields.Text("Phản hồi của khách hàng", tracking=True)
    
    # Chi phí
    chi_phi = fields.Float("Chi phí", tracking=True)
    don_vi_tien_te = fields.Selection([
        ('VND', 'VNĐ'),
        ('USD', 'USD')
    ], string="Đơn vị", default='VND')
    
    # File đính kèm
    attachment_ids = fields.Many2many('ir.attachment', string="File đính kèm")
    
    # Hành động tiếp theo
    can_hanh_dong_tiep = fields.Boolean("Cần hành động tiếp theo", default=False)
    hanh_dong_tiep_theo = fields.Text("Hành động tiếp theo")
    ngay_hanh_dong_tiep = fields.Date("Ngày hành động tiếp")
    
    active = fields.Boolean("Active", default=True)
    ghi_chu = fields.Text("Ghi chú")
    
    @api.model
    def create(self, vals):
        """Tạo mã chăm sóc tự động"""
        if vals.get('ma_cham_soc', 'New') == 'New':
            vals['ma_cham_soc'] = self.env['ir.sequence'].next_by_code('customer.care') or 'New'
        return super(CustomerCare, self).create(vals)
    
    def action_start(self):
        """Bắt đầu chăm sóc"""
        self.ensure_one()
        self.write({'trang_thai': 'in_progress'})
        self.message_post(body="Bắt đầu chăm sóc khách hàng")
    
    def action_complete(self):
        """Hoàn thành"""
        self.ensure_one()
        if not self.ngay_cham_soc:
            self.write({
                'trang_thai': 'completed',
                'ngay_cham_soc': fields.Datetime.now()
            })
        else:
            self.write({'trang_thai': 'completed'})
        
        self.message_post(
            body=f"Hoàn thành chăm sóc khách hàng<br/>Kết quả: {dict(self._fields['ket_qua'].selection).get(self.ket_qua, '')}"
        )
        
        # Tạo activity tiếp theo nếu cần
        if self.can_hanh_dong_tiep and self.hanh_dong_tiep_theo:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=self.hanh_dong_tiep_theo,
                date_deadline=self.ngay_hanh_dong_tiep or fields.Date.today(),
                user_id=self.nhan_vien_id.id if self.nhan_vien_id else self.env.user.id
            )
    
    def action_cancel(self):
        """Hủy"""
        self.ensure_one()
        self.write({'trang_thai': 'cancelled'})
        self.message_post(body="Đã hủy chăm sóc khách hàng")
    
    def action_view_customer(self):
        """Xem khách hàng"""
        self.ensure_one()
        return {
            'name': 'Khách hàng',
            'type': 'ir.actions.act_window',
            'res_model': 'customer',
            'res_id': self.customer_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
