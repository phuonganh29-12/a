# -*- coding: utf-8 -*-
from odoo import models, fields, api

class WizardSendEmailMarketing(models.TransientModel):
    _name = 'wizard.send.email.marketing'
    _description = 'Wizard gửi Email Marketing'
    
    campaign_id = fields.Many2one('email.marketing.campaign', string="Chiến dịch", required=True)
    email_template_id = fields.Many2one('email.marketing.template', string="Mẫu email", 
                                        related='campaign_id.email_template_id', readonly=True)
    
    tong_khach_hang = fields.Integer("Tổng khách hàng", related='campaign_id.tong_khach_hang', readonly=True)
    
    gui_ngay = fields.Boolean("Gửi ngay", default=True)
    gui_test = fields.Boolean("Chế độ test (không gửi thực tế)", default=False)
    
    xac_nhan = fields.Boolean("Tôi xác nhận gửi email cho tất cả khách hàng")
    
    def action_send(self):
        """Gửi email marketing"""
        self.ensure_one()
        
        if not self.xac_nhan:
            from odoo.exceptions import ValidationError
            raise ValidationError("Vui lòng xác nhận trước khi gửi!")
        
        campaign = self.campaign_id
        template = campaign.email_template_id
        
        # Lấy danh sách khách hàng
        customers = campaign._get_customers()
        
        if not customers:
            raise ValidationError("Không có khách hàng nào để gửi email!")
        
        # Cập nhật trạng thái
        campaign.write({
            'trang_thai': 'sending',
            'ngay_gui_thuc_te': fields.Datetime.now(),
            'so_email_gui': len(customers)
        })
        
        # Gửi email cho từng khách hàng
        thanh_cong = 0
        that_bai = 0
        EmailLog = self.env['email.marketing.log']
        
        for customer in customers:
            try:
                if not self.gui_test:
                    # Thay thế biến trong subject và nội dung
                    subject = template.thay_the_bien(template.subject, customer)
                    body = template.thay_the_bien(template.noi_dung_html, customer)
                    
                    # Gửi email (sử dụng mail.mail của Odoo)
                    mail_values = {
                        'subject': subject,
                        'body_html': body,
                        'email_to': customer.email,
                        'email_from': self.env.user.email or 'noreply@company.com',
                    }
                    mail = self.env['mail.mail'].create(mail_values)
                    mail.send()
                
                # Tạo log thành công
                EmailLog.create({
                    'campaign_id': campaign.id,
                    'customer_id': customer.id,
                    'trang_thai': 'success',
                    'ghi_chu': 'Test mode' if self.gui_test else 'Sent successfully'
                })
                thanh_cong += 1
                
            except Exception as e:
                # Tạo log thất bại
                EmailLog.create({
                    'campaign_id': campaign.id,
                    'customer_id': customer.id,
                    'trang_thai': 'failed',
                    'loi': str(e)
                })
                that_bai += 1
        
        # Cập nhật kết quả
        campaign.write({
            'trang_thai': 'sent',
            'so_email_thanh_cong': thanh_cong,
            'so_email_that_bai': that_bai
        })
        
        # Tăng số lần sử dụng template
        template.sudo().write({'so_lan_su_dung': template.so_lan_su_dung + 1})
        
        # Thông báo
        message = f"Đã gửi email marketing<br/>"
        message += f"- Thành công: {thanh_cong}<br/>"
        message += f"- Thất bại: {that_bai}"
        if self.gui_test:
            message += "<br/><strong>(Chế độ test - không gửi thực tế)</strong>"
        
        campaign.message_post(body=message)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Hoàn thành!',
                'message': f'Đã gửi {thanh_cong}/{len(customers)} email',
                'type': 'success',
                'sticky': False,
            }
        }


class WizardTestEmailTemplate(models.TransientModel):
    _name = 'wizard.test.email.template'
    _description = 'Wizard test mẫu email'
    
    template_id = fields.Many2one('email.marketing.template', string="Mẫu email", required=True)
    email_test = fields.Char("Email nhận test", required=True, 
                             default=lambda self: self.env.user.email)
    customer_test_id = fields.Many2one('customer', string="Khách hàng mẫu",
                                       help="Dùng để thay thế biến trong email")
    
    def action_send_test(self):
        """Gửi email test"""
        self.ensure_one()
        
        template = self.template_id
        customer = self.customer_test_id
        
        if not customer:
            # Lấy khách hàng đầu tiên có email
            customer = self.env['customer'].search([('email', '!=', False)], limit=1)
            if not customer:
                from odoo.exceptions import ValidationError
                raise ValidationError("Không tìm thấy khách hàng nào có email để test!")
        
        # Thay thế biến
        subject = template.thay_the_bien(template.subject, customer)
        body = template.thay_the_bien(template.noi_dung_html, customer)
        
        # Gửi email
        mail_values = {
            'subject': f"[TEST] {subject}",
            'body_html': body,
            'email_to': self.email_test,
            'email_from': self.env.user.email or 'noreply@company.com',
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Đã gửi!',
                'message': f'Email test đã được gửi đến {self.email_test}',
                'type': 'success',
                'sticky': False,
            }
        }
