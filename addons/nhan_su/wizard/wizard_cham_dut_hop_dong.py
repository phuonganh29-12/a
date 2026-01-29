# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class WizardChamDutHopDong(models.TransientModel):
    _name = 'wizard.cham.dut.hop.dong'
    _description = 'Wizard chấm dứt hợp đồng lao động'
    
    hop_dong_id = fields.Many2one('hop_dong_lao_dong', string="Hợp đồng", required=True)
    ngay_cham_dut = fields.Date("Ngày chấm dứt", required=True, default=fields.Date.today)
    ly_do_cham_dut = fields.Text("Lý do chấm dứt", required=True)
    
    def action_xac_nhan_cham_dut(self):
        """Xác nhận chấm dứt hợp đồng"""
        self.ensure_one()
        
        if self.ngay_cham_dut < self.hop_dong_id.ngay_bat_dau:
            raise ValidationError("Ngày chấm dứt không thể trước ngày bắt đầu hợp đồng!")
        
        # Cập nhật hợp đồng
        self.hop_dong_id.write({
            'ngay_cham_dut': self.ngay_cham_dut,
            'ly_do_cham_dut': self.ly_do_cham_dut,
            'trang_thai': 'cham_dut'
        })
        
        # Gửi thông báo
        self.hop_dong_id.message_post(
            body=f"Hợp đồng đã chấm dứt vào ngày {self.ngay_cham_dut.strftime('%d/%m/%Y')}<br/>Lý do: {self.ly_do_cham_dut}",
            subject="Chấm dứt hợp đồng"
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': 'Đã chấm dứt hợp đồng lao động',
                'type': 'success',
                'sticky': False,
            }
        }
