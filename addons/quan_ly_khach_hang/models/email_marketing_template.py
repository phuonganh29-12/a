# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EmailMarketingTemplate(models.Model):
    _name = 'email.marketing.template'
    _description = 'Mẫu Email Marketing'
    _rec_name = 'name'
    _order = 'name'
    
    # Thông tin cơ bản
    name = fields.Char("Tên mẫu", required=True)
    ma_mau = fields.Char("Mã mẫu", required=True, copy=False, index=True)
    mo_ta = fields.Text("Mô tả")
    
    # Nội dung email
    subject = fields.Char("Tiêu đề email", required=True,
                         help="Có thể dùng biến: ${ten_khach_hang}, ${ma_khach_hang}, ${ngay_hom_nay}")
    noi_dung_html = fields.Html("Nội dung email", required=True,
                                help="Có thể dùng biến: ${ten_khach_hang}, ${email}, ${dien_thoai}, ${dia_chi}, ${ngay_hom_nay}")
    
    # Loại
    loai_mau = fields.Selection([
        ('welcome', 'Chào mừng khách hàng mới'),
        ('promotion', 'Khuyến mãi'),
        ('newsletter', 'Bản tin'),
        ('birthday', 'Chúc mừng sinh nhật'),
        ('care', 'Chăm sóc khách hàng'),
        ('other', 'Khác')
    ], string="Loại mẫu", default='other')
    
    # Trạng thái
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('active', 'Đang sử dụng'),
        ('archived', 'Lưu trữ')
    ], string="Trạng thái", default='draft', required=True)
    
    # Thống kê
    so_lan_su_dung = fields.Integer("Số lần sử dụng", readonly=True, default=0)
    
    active = fields.Boolean("Active", default=True)
    
    @api.constrains('ma_mau')
    def _check_ma_mau_unique(self):
        """Kiểm tra mã mẫu duy nhất"""
        for record in self:
            if self.search_count([('ma_mau', '=', record.ma_mau), ('id', '!=', record.id)]) > 0:
                raise ValidationError(f"Mã mẫu '{record.ma_mau}' đã tồn tại!")
    
    def thay_the_bien(self, noi_dung, customer):
        """Thay thế biến trong nội dung email"""
        import re
        from datetime import datetime
        
        # Dictionary chứa các biến có thể thay thế
        bien_thay_the = {
            'ten_khach_hang': customer.ten_khach_hang or '',
            'ma_khach_hang': customer.ma_khach_hang or '',
            'email': customer.email or '',
            'dien_thoai': customer.dien_thoai or '',
            'dia_chi': customer.dia_chi or '',
            'website': customer.website or '',
            'ngay_hom_nay': datetime.now().strftime('%d/%m/%Y'),
            'thang_hien_tai': datetime.now().strftime('%m/%Y'),
            'nam_hien_tai': str(datetime.now().year),
        }
        
        # Thay thế các biến ${bien}
        for key, value in bien_thay_the.items():
            pattern = r'\$\{' + key + r'\}'
            noi_dung = re.sub(pattern, str(value), noi_dung)
        
        return noi_dung
    
    def action_test_email(self):
        """Gửi email test"""
        self.ensure_one()
        return {
            'name': 'Gửi Email Test',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.test.email.template',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_template_id': self.id}
        }
    
    def action_activate(self):
        """Kích hoạt mẫu"""
        self.write({'trang_thai': 'active'})
    
    def action_archive_template(self):
        """Lưu trữ mẫu"""
        self.write({'trang_thai': 'archived'})
    
    def action_view_campaigns(self):
        """Xem các chiến dịch sử dụng mẫu này"""
        self.ensure_one()
        return {
            'name': 'Chiến dịch sử dụng mẫu',
            'type': 'ir.actions.act_window',
            'res_model': 'email.marketing.campaign',
            'view_mode': 'tree,form',
            'domain': [('email_template_id', '=', self.id)],
            'context': {'default_email_template_id': self.id}
        }
