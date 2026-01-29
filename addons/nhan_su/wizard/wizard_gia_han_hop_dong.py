# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class WizardGiaHanHopDong(models.TransientModel):
    _name = 'wizard.gia.han.hop.dong'
    _description = 'Wizard gia hạn hợp đồng lao động'
    
    hop_dong_goc_id = fields.Many2one('hop_dong_lao_dong', string="Hợp đồng gốc", required=True)
    
    # Thông tin hợp đồng mới
    loai_hop_dong = fields.Selection([
        ('thu_viec', 'Thử việc'),
        ('co_dinh_1_nam', 'Có định hạn 1 năm'),
        ('co_dinh_3_nam', 'Có định hạn 3 năm'),
        ('vo_dinh_han', 'Vô định hạn'),
        ('mua_vu', 'Theo mùa vụ'),
        ('cong_viec', 'Theo công việc')
    ], string="Loại hợp đồng mới", required=True, default='co_dinh_3_nam')
    
    ngay_bat_dau = fields.Date("Ngày bắt đầu", required=True)
    ngay_ket_thuc = fields.Date("Ngày kết thúc")
    
    # Kế thừa thông tin từ hợp đồng cũ
    luong_co_ban = fields.Float("Lương cơ bản", required=True)
    phu_cap_an_trua = fields.Float("Phụ cấp ăn trưa")
    phu_cap_xang_xe = fields.Float("Phụ cấp xăng xe")
    phu_cap_dien_thoai = fields.Float("Phụ cấp điện thoại")
    phu_cap_khac = fields.Float("Phụ cấp khác")
    
    ghi_chu = fields.Text("Ghi chú")
    
    @api.onchange('hop_dong_goc_id')
    def _onchange_hop_dong_goc(self):
        """Điền thông tin từ hợp đồng cũ"""
        if self.hop_dong_goc_id:
            # Ngày bắt đầu = ngày kết thúc hợp đồng cũ + 1
            if self.hop_dong_goc_id.ngay_ket_thuc:
                self.ngay_bat_dau = self.hop_dong_goc_id.ngay_ket_thuc + timedelta(days=1)
            
            # Kế thừa lương và phụ cấp
            self.luong_co_ban = self.hop_dong_goc_id.luong_co_ban
            self.phu_cap_an_trua = self.hop_dong_goc_id.phu_cap_an_trua
            self.phu_cap_xang_xe = self.hop_dong_goc_id.phu_cap_xang_xe
            self.phu_cap_dien_thoai = self.hop_dong_goc_id.phu_cap_dien_thoai
            self.phu_cap_khac = self.hop_dong_goc_id.phu_cap_khac
    
    @api.onchange('loai_hop_dong', 'ngay_bat_dau')
    def _onchange_loai_hop_dong(self):
        """Tự động tính ngày kết thúc theo loại hợp đồng"""
        if self.ngay_bat_dau:
            if self.loai_hop_dong == 'thu_viec':
                self.ngay_ket_thuc = self.ngay_bat_dau + timedelta(days=60)  # 2 tháng
            elif self.loai_hop_dong == 'co_dinh_1_nam':
                self.ngay_ket_thuc = self.ngay_bat_dau + timedelta(days=365)
            elif self.loai_hop_dong == 'co_dinh_3_nam':
                self.ngay_ket_thuc = self.ngay_bat_dau + timedelta(days=1095)  # 3 năm
            elif self.loai_hop_dong == 'vo_dinh_han':
                self.ngay_ket_thuc = False
    
    def action_xac_nhan_gia_han(self):
        """Tạo hợp đồng mới và đánh dấu hợp đồng cũ đã gia hạn"""
        self.ensure_one()
        
        # Tạo văn bản hợp đồng mới
        VanBan = self.env['van_ban_di']
        van_ban_moi = VanBan.create({
            'loai_van_ban_id': self.hop_dong_goc_id.van_ban_id.loai_van_ban_id.id,
            'trich_yeu': f"Hợp đồng lao động gia hạn - {self.hop_dong_goc_id.nhan_vien_id.name}",
            'ngay_van_ban': fields.Date.today(),
            'noi_dung': f"Gia hạn từ hợp đồng {self.hop_dong_goc_id.so_hop_dong}",
        })
        
        # Tạo hợp đồng mới
        hop_dong_moi = self.env['hop_dong_lao_dong'].create({
            'van_ban_id': van_ban_moi.id,
            'nhan_vien_id': self.hop_dong_goc_id.nhan_vien_id.id,
            'loai_hop_dong': self.loai_hop_dong,
            'ngay_bat_dau': self.ngay_bat_dau,
            'ngay_ket_thuc': self.ngay_ket_thuc,
            'vi_tri_cong_viec': self.hop_dong_goc_id.vi_tri_cong_viec,
            'phong_ban_id': self.hop_dong_goc_id.phong_ban_id.id if self.hop_dong_goc_id.phong_ban_id else False,
            'chuc_vu_id': self.hop_dong_goc_id.chuc_vu_id.id if self.hop_dong_goc_id.chuc_vu_id else False,
            'dia_diem_lam_viec': self.hop_dong_goc_id.dia_diem_lam_viec,
            'mo_ta_cong_viec': self.hop_dong_goc_id.mo_ta_cong_viec,
            'luong_co_ban': self.luong_co_ban,
            'don_vi_tien_te': self.hop_dong_goc_id.don_vi_tien_te,
            'phu_cap_an_trua': self.phu_cap_an_trua,
            'phu_cap_xang_xe': self.phu_cap_xang_xe,
            'phu_cap_dien_thoai': self.phu_cap_dien_thoai,
            'phu_cap_khac': self.phu_cap_khac,
            'bao_hiem_xa_hoi': self.hop_dong_goc_id.bao_hiem_xa_hoi,
            'bao_hiem_y_te': self.hop_dong_goc_id.bao_hiem_y_te,
            'bao_hiem_that_nghiep': self.hop_dong_goc_id.bao_hiem_that_nghiep,
            'gio_lam_viec_tuan': self.hop_dong_goc_id.gio_lam_viec_tuan,
            'ngay_nghi_phep_nam': self.hop_dong_goc_id.ngay_nghi_phep_nam,
            'hop_dong_goc_id': self.hop_dong_goc_id.id,
            'ghi_chu': self.ghi_chu,
        })
        
        # Đánh dấu hợp đồng cũ đã gia hạn
        self.hop_dong_goc_id.write({
            'hop_dong_gia_han_id': hop_dong_moi.id,
            'trang_thai': 'gia_han'
        })
        
        # Gửi thông báo
        self.hop_dong_goc_id.message_post(
            body=f"Hợp đồng đã được gia hạn. Hợp đồng mới: {hop_dong_moi.so_hop_dong}",
            subject="Gia hạn hợp đồng"
        )
        
        # Mở hợp đồng mới
        return {
            'name': 'Hợp đồng lao động mới',
            'type': 'ir.actions.act_window',
            'res_model': 'hop_dong_lao_dong',
            'res_id': hop_dong_moi.id,
            'view_mode': 'form',
            'target': 'current',
        }
