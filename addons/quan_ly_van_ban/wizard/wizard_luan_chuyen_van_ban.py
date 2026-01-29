# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class WizardLuanChuyenVanBan(models.TransientModel):
    _name = 'wizard.luan.chuyen.van.ban'
    _description = 'Wizard luân chuyển văn bản'
    
    van_ban_di_id = fields.Many2one('van_ban_di', string="Văn bản đi")
    van_ban_den_id = fields.Many2one('van_ban_den', string="Văn bản đến")
    
    # Thông tin luân chuyển
    nguoi_nhan_ids = fields.Many2many('nhan_vien', string="Người nhận", required=True,
                                      help="Có thể chọn nhiều người nhận")
    noi_dung_chuyen = fields.Text("Nội dung chuyển/Ý kiến", required=True,
                                  placeholder="Nhập nội dung chỉ đạo hoặc yêu cầu xử lý")
    han_xu_ly = fields.Date("Hạn xử lý")
    muc_do_uu_tien = fields.Selection([
        ('low', 'Thấp'),
        ('normal', 'Bình thường'),
        ('high', 'Cao'),
        ('urgent', 'Khẩn cấp')
    ], string="Mức độ ưu tiên", default='normal', required=True)
    
    # Tùy chọn
    gui_email_thong_bao = fields.Boolean("Gửi email thông báo", default=True)
    
    def action_luan_chuyen(self):
        """Thực hiện luân chuyển văn bản"""
        self.ensure_one()
        
        if not self.nguoi_nhan_ids:
            raise UserError("Vui lòng chọn ít nhất một người nhận!")
        
        # Lấy thông tin người chuyển
        current_user = self.env.user
        nguoi_chuyen = self.env['nhan_vien'].search([('user_id', '=', current_user.id)], limit=1)
        
        if not nguoi_chuyen:
            raise UserError("Không tìm thấy thông tin nhân viên của bạn!")
        
        # Tạo luân chuyển cho từng người nhận
        luan_chuyen_ids = []
        for nguoi_nhan in self.nguoi_nhan_ids:
            luan_chuyen_vals = {
                'van_ban_di_id': self.van_ban_di_id.id if self.van_ban_di_id else False,
                'van_ban_den_id': self.van_ban_den_id.id if self.van_ban_den_id else False,
                'nguoi_chuyen_id': nguoi_chuyen.id,
                'nguoi_nhan_id': nguoi_nhan.id,
                'noi_dung_chuyen': self.noi_dung_chuyen,
                'han_xu_ly': self.han_xu_ly,
                'muc_do_uu_tien': self.muc_do_uu_tien,
                'trang_thai': 'cho_nhan',
            }
            
            luan_chuyen = self.env['luan_chuyen_van_ban'].create(luan_chuyen_vals)
            luan_chuyen_ids.append(luan_chuyen.id)
            
            # Gửi email thông báo nếu được chọn
            if self.gui_email_thong_bao and nguoi_nhan.user_id:
                self._gui_email_thong_bao(luan_chuyen, nguoi_nhan)
        
        # Hiển thị thông báo thành công
        message = f"Đã luân chuyển văn bản cho {len(self.nguoi_nhan_ids)} người."
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
    
    def _gui_email_thong_bao(self, luan_chuyen, nguoi_nhan):
        """Gửi email thông báo cho người nhận"""
        if not nguoi_nhan.user_id or not nguoi_nhan.user_id.partner_id:
            return
        
        van_ban_name = ""
        if luan_chuyen.van_ban_di_id:
            van_ban_name = f"{luan_chuyen.van_ban_di_id.so_van_ban} - {luan_chuyen.van_ban_di_id.ten_van_ban}"
        elif luan_chuyen.van_ban_den_id:
            van_ban_name = f"{luan_chuyen.van_ban_den_id.so_van_ban_den} - {luan_chuyen.van_ban_den_id.trich_yeu}"
        
        body = f"""
        <p>Kính gửi <strong>{nguoi_nhan.ten_nhan_vien}</strong>,</p>
        <p>Bạn có văn bản mới cần xử lý:</p>
        <ul>
            <li><strong>Văn bản:</strong> {van_ban_name}</li>
            <li><strong>Người chuyển:</strong> {luan_chuyen.nguoi_chuyen_id.ten_nhan_vien}</li>
            <li><strong>Mức độ ưu tiên:</strong> {dict(luan_chuyen._fields['muc_do_uu_tien'].selection)[luan_chuyen.muc_do_uu_tien]}</li>
            <li><strong>Hạn xử lý:</strong> {luan_chuyen.han_xu_ly.strftime('%d/%m/%Y') if luan_chuyen.han_xu_ly else 'Không có'}</li>
            <li><strong>Nội dung:</strong> {luan_chuyen.noi_dung_chuyen}</li>
        </ul>
        <p>Vui lòng kiểm tra và xử lý kịp thời.</p>
        """
        
        luan_chuyen.message_post(
            body=body,
            subject=f'[Luân chuyển văn bản] {van_ban_name}',
            partner_ids=[nguoi_nhan.user_id.partner_id.id],
            message_type='email'
        )
