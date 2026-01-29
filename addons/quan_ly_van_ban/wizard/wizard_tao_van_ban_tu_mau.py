# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
from datetime import datetime

class WizardTaoVanBanTuMau(models.TransientModel):
    _name = 'wizard.tao.van.ban.tu.mau'
    _description = 'Wizard tạo văn bản từ mẫu'
    
    mau_van_ban_id = fields.Many2one('mau_van_ban', string="Chọn mẫu", required=True)
    loai_van_ban_id = fields.Many2one('loai_van_ban', string="Loại văn bản", required=True)
    
    # Chọn đối tượng liên quan
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên")
    customer_id = fields.Many2one('customer', string="Khách hàng")
    
    # Các trường của văn bản
    so_van_ban = fields.Char("Số văn bản")
    trich_yeu = fields.Char("Trích yếu", required=True)
    ngay_van_ban = fields.Date("Ngày văn bản", default=fields.Date.today, required=True)
    
    # Preview
    noi_dung_preview = fields.Html("Nội dung (Preview)", compute="_compute_noi_dung_preview", store=False)
    
    # Tùy chọn xuất
    xuat_file_word = fields.Boolean("Xuất file Word", default=True, 
                                     help="Tự động tải file Word sau khi tạo văn bản")
    
    @api.onchange('mau_van_ban_id')
    def _onchange_mau_van_ban_id(self):
        """Tự động điền loại văn bản khi chọn mẫu"""
        if self.mau_van_ban_id:
            self.loai_van_ban_id = self.mau_van_ban_id.loai_van_ban_id
    
    @api.depends('mau_van_ban_id', 'nhan_vien_id', 'customer_id', 'so_van_ban', 'ngay_van_ban')
    def _compute_noi_dung_preview(self):
        """Tạo preview nội dung với dữ liệu đã merge"""
        for wizard in self:
            if wizard.mau_van_ban_id:
                data_dict = wizard._tao_du_lieu_merge()
                wizard.noi_dung_preview = wizard.mau_van_ban_id.thay_the_bien(
                    wizard.mau_van_ban_id.noi_dung_html, 
                    data_dict
                )
            else:
                wizard.noi_dung_preview = ""
    
    def _tao_du_lieu_merge(self):
        """Tạo dictionary dữ liệu để merge vào mẫu"""
        self.ensure_one()
        
        today = self.ngay_van_ban or fields.Date.today()
        
        data = {
            'so_van_ban': self.so_van_ban or 'NEW',
            'ngay_hom_nay': today.strftime('%d/%m/%Y'),
            'ngay_thang_nam': f"Ngày {today.day} tháng {today.month} năm {today.year}",
            'nam_hien_tai': str(today.year),
            'trich_yeu': self.trich_yeu or '',
        }
        
        # Dữ liệu nhân viên
        if self.nhan_vien_id:
            data.update({
                'ten_nhan_vien': self.nhan_vien_id.ten_nhan_vien or '',
                'ma_nhan_vien': self.nhan_vien_id.ma_nhan_vien or '',
                'chuc_vu': self.nhan_vien_id.chuc_vu_id.ten_chuc_vu if self.nhan_vien_id.chuc_vu_id else '',
                'phong_ban': self.nhan_vien_id.phong_ban_id.ten_phong_ban if self.nhan_vien_id.phong_ban_id else '',
                'email_nhan_vien': self.nhan_vien_id.email or '',
                'sdt_nhan_vien': self.nhan_vien_id.so_dien_thoai or '',
            })
        
        # Dữ liệu khách hàng
        if self.customer_id:
            data.update({
                'ten_khach_hang': self.customer_id.customer_name or '',
                'ma_khach_hang': self.customer_id.customer_id or '',
                'email_khach_hang': self.customer_id.email or '',
                'sdt_khach_hang': self.customer_id.phone or '',
                'dia_chi_khach_hang': self.customer_id.address or '',
            })
        
        return data
    
    def action_tao_van_ban(self):
        """Tạo văn bản từ mẫu"""
        self.ensure_one()
        
        if not self.mau_van_ban_id:
            raise UserError("Vui lòng chọn mẫu văn bản!")
        
        # Tạo dữ liệu merge
        data_dict = self._tao_du_lieu_merge()
        
        # Thay thế biến trong nội dung
        noi_dung_final = self.mau_van_ban_id.thay_the_bien(
            self.mau_van_ban_id.noi_dung_html, 
            data_dict
        )
        
        # Tạo văn bản đi mới
        van_ban_vals = {
            'loai_van_ban_id': self.loai_van_ban_id.id,
            'so_van_ban': self.so_van_ban,
            'trich_yeu': self.trich_yeu,
            'ngay_van_ban': self.ngay_van_ban,
            'noi_dung': noi_dung_final,
            'nhan_vien_id': self.nhan_vien_id.id if self.nhan_vien_id else False,
            'customer_id': self.customer_id.id if self.customer_id else False,
        }
        
        van_ban = self.env['van_ban_di'].create(van_ban_vals)
        
        # Xuất file Word nếu được chọn
        if self.xuat_file_word:
            return self.action_xuat_word(van_ban, data_dict)
        
        # Mở form văn bản vừa tạo
        return {
            'name': 'Văn bản đi',
            'type': 'ir.actions.act_window',
            'res_model': 'van_ban_di',
            'res_id': van_ban.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_xuat_word(self, van_ban=None, data_dict=None):
        """Xuất file Word từ mẫu"""
        self.ensure_one()
        
        if not data_dict:
            data_dict = self._tao_du_lieu_merge()
        
        try:
            # Tạo file Word
            word_data = self.mau_van_ban_id.xuat_word(data_dict)
            
            # Tạo tên file
            file_name = f"{self.mau_van_ban_id.ma_mau}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            
            # Tạo attachment
            attachment = self.env['ir.attachment'].create({
                'name': file_name,
                'type': 'binary',
                'datas': base64.b64encode(word_data),
                'res_model': 'van_ban_di',
                'res_id': van_ban.id if van_ban else False,
                'mimetype': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            })
            
            # Trả về action download file
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }
            
        except Exception as e:
            raise UserError(f"Lỗi khi xuất file Word: {str(e)}")
    
    def action_preview(self):
        """Chỉ xem preview, không tạo văn bản"""
        self.ensure_one()
        # Force recompute preview
        self._compute_noi_dung_preview()
        return {
            'type': 'ir.actions.do_nothing',
        }
