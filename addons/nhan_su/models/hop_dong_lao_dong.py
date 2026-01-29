# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class HopDongLaoDong(models.Model):
    _name = 'hop_dong_lao_dong'
    _description = 'Hợp đồng lao động'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'so_hop_dong'
    _order = 'ngay_ky desc, id desc'
    
    # Liên kết với văn bản
    van_ban_id = fields.Many2one('van_ban_di', string="Văn bản hợp đồng", 
                                 ondelete='set null', tracking=True, check_company=False,
                                 copy=False)
    
    # Thông tin cơ bản
    so_hop_dong = fields.Char("Số hợp đồng", tracking=True)
    ngay_ky = fields.Date("Ngày ký", tracking=True, default=fields.Date.today)
    
    # Nhân viên
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True, 
                                   tracking=True, ondelete='restrict')
    
    # Loại hợp đồng
    loai_hop_dong = fields.Selection([
        ('thu_viec', 'Thử việc'),
        ('co_dinh_1_nam', 'Có định hạn 1 năm'),
        ('co_dinh_3_nam', 'Có định hạn 3 năm'),
        ('vo_dinh_han', 'Vô định hạn'),
        ('mua_vu', 'Theo mùa vụ'),
        ('cong_viec', 'Theo công việc')
    ], string="Loại hợp đồng", required=True, default='thu_viec', tracking=True)
    
    # Thời hạn
    ngay_bat_dau = fields.Date("Ngày bắt đầu", required=True, tracking=True)
    ngay_ket_thuc = fields.Date("Ngày kết thúc", tracking=True,
                                help="Để trống nếu là hợp đồng vô định hạn")
    thoi_han_thang = fields.Integer("Thời hạn (tháng)", compute='_compute_thoi_han', store=True)
    
    # Công việc
    vi_tri_cong_viec = fields.Char("Vị trí công việc", required=True, tracking=True)
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban", tracking=True, check_company=False, copy=False)
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ", tracking=True, check_company=False, copy=False)
    dia_diem_lam_viec = fields.Char("Địa điểm làm việc", tracking=True)
    mo_ta_cong_viec = fields.Text("Mô tả công việc")
    
    # Lương & phúc lợi
    luong_co_ban = fields.Float("Lương cơ bản", required=True, tracking=True)
    don_vi_tien_te = fields.Selection([
        ('VND', 'VNĐ'),
        ('USD', 'USD')
    ], string="Đơn vị", default='VND')
    
    # Phụ cấp
    phu_cap_an_trua = fields.Float("Phụ cấp ăn trưa", tracking=True)
    phu_cap_xang_xe = fields.Float("Phụ cấp xăng xe", tracking=True)
    phu_cap_dien_thoai = fields.Float("Phụ cấp điện thoại", tracking=True)
    phu_cap_khac = fields.Float("Phụ cấp khác", tracking=True)
    tong_phu_cap = fields.Float("Tổng phụ cấp", compute='_compute_tong_phu_cap', store=True)
    
    # Bảo hiểm
    bao_hiem_xa_hoi = fields.Boolean("Bảo hiểm xã hội", default=True, tracking=True)
    bao_hiem_y_te = fields.Boolean("Bảo hiểm y tế", default=True, tracking=True)
    bao_hiem_that_nghiep = fields.Boolean("Bảo hiểm thất nghiệp", default=True, tracking=True)
    
    # Chế độ làm việc
    gio_lam_viec_tuan = fields.Integer("Giờ làm việc/tuần", default=40)
    ngay_nghi_phep_nam = fields.Integer("Ngày nghỉ phép/năm", default=12)
    
    # Trạng thái
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('dang_hieu_luc', 'Đang hiệu lực'),
        ('sap_het_han', 'Sắp hết hạn'),
        ('het_han', 'Hết hạn'),
        ('gia_han', 'Đã gia hạn'),
        ('cham_dut', 'Chấm dứt')
    ], string="Trạng thái", default='draft', required=True, tracking=True)
    
    # Gia hạn
    hop_dong_gia_han_id = fields.Many2one('hop_dong_lao_dong', string="Hợp đồng gia hạn",
                                          readonly=True, check_company=False, copy=False,
                                          help="Hợp đồng mới được gia hạn từ hợp đồng này")
    hop_dong_goc_id = fields.Many2one('hop_dong_lao_dong', string="Hợp đồng gốc",
                                      readonly=True, check_company=False, copy=False,
                                      help="Hợp đồng được gia hạn từ đâu")
    
    # Chấm dứt
    ngay_cham_dut = fields.Date("Ngày chấm dứt", tracking=True)
    ly_do_cham_dut = fields.Text("Lý do chấm dứt", tracking=True)
    
    # Computed
    so_ngay_con_lai = fields.Integer("Số ngày còn lại", compute='_compute_so_ngay_con_lai')
    sap_het_han = fields.Boolean("Sắp hết hạn", compute='_compute_sap_het_han', store=True)
    
    active = fields.Boolean("Active", default=True)
    ghi_chu = fields.Text("Ghi chú")
    
    @api.model
    def default_get(self, fields_list):
        """Override default_get to ensure all Many2one fields have valid defaults"""
        res = super(HopDongLaoDong, self).default_get(fields_list)
        
        # Đảm bảo các trường Many2one không bị set giá trị không hợp lệ
        many2one_fields = ['van_ban_id', 'phong_ban_id', 'chuc_vu_id', 
                          'hop_dong_gia_han_id', 'hop_dong_goc_id']
        for field in many2one_fields:
            if field in res and not res[field]:
                res[field] = False
        
        return res
    
    @api.depends('ngay_bat_dau', 'ngay_ket_thuc')
    def _compute_thoi_han(self):
        """Tính thời hạn hợp đồng theo tháng"""
        for record in self:
            if record.ngay_bat_dau and record.ngay_ket_thuc:
                delta = record.ngay_ket_thuc - record.ngay_bat_dau
                record.thoi_han_thang = int(delta.days / 30)
            else:
                record.thoi_han_thang = 0
    
    @api.depends('phu_cap_an_trua', 'phu_cap_xang_xe', 'phu_cap_dien_thoai', 'phu_cap_khac')
    def _compute_tong_phu_cap(self):
        """Tính tổng phụ cấp"""
        for record in self:
            record.tong_phu_cap = (record.phu_cap_an_trua + record.phu_cap_xang_xe + 
                                  record.phu_cap_dien_thoai + record.phu_cap_khac)
    
    @api.depends('ngay_ket_thuc')
    def _compute_so_ngay_con_lai(self):
        """Tính số ngày còn lại đến hết hạn"""
        today = fields.Date.today()
        for record in self:
            if record.ngay_ket_thuc and record.trang_thai in ['dang_hieu_luc', 'sap_het_han']:
                delta = record.ngay_ket_thuc - today
                record.so_ngay_con_lai = delta.days
            else:
                record.so_ngay_con_lai = 0
    
    @api.depends('ngay_ket_thuc', 'trang_thai')
    def _compute_sap_het_han(self):
        """Kiểm tra hợp đồng sắp hết hạn (còn 30 ngày)"""
        today = fields.Date.today()
        for record in self:
            if record.ngay_ket_thuc and record.trang_thai == 'dang_hieu_luc':
                delta = record.ngay_ket_thuc - today
                record.sap_het_han = 0 < delta.days <= 30
            else:
                record.sap_het_han = False
    
    @api.constrains('ngay_bat_dau', 'ngay_ket_thuc')
    def _check_dates(self):
        """Kiểm tra ngày tháng hợp lệ"""
        for record in self:
            if record.ngay_ket_thuc and record.ngay_bat_dau:
                if record.ngay_ket_thuc <= record.ngay_bat_dau:
                    raise ValidationError("Ngày kết thúc phải sau ngày bắt đầu!")
    
    @api.constrains('luong_co_ban')
    def _check_luong(self):
        """Kiểm tra lương cơ bản"""
        for record in self:
            if record.luong_co_ban <= 0:
                raise ValidationError("Lương cơ bản phải lớn hơn 0!")
    
    @api.model
    def create(self, vals):
        """Override create để xử lý các trường Many2one"""
        # Đảm bảo van_ban_id là False nếu không được cung cấp
        if 'van_ban_id' not in vals:
            vals['van_ban_id'] = False
        
        # Đảm bảo các trường Many2one khác cũng được xử lý đúng
        if vals.get('phong_ban_id') and not self.env['phong_ban'].browse(vals['phong_ban_id']).exists():
            vals['phong_ban_id'] = False
        if vals.get('chuc_vu_id') and not self.env['chuc_vu'].browse(vals['chuc_vu_id']).exists():
            vals['chuc_vu_id'] = False
        if vals.get('hop_dong_goc_id') and not self.env['hop_dong_lao_dong'].browse(vals['hop_dong_goc_id']).exists():
            vals['hop_dong_goc_id'] = False
        if vals.get('hop_dong_gia_han_id') and not self.env['hop_dong_lao_dong'].browse(vals['hop_dong_gia_han_id']).exists():
            vals['hop_dong_gia_han_id'] = False
            
        return super(HopDongLaoDong, self).create(vals)
    
    def write(self, vals):
        """Override write để xử lý các trường Many2one"""
        # Đảm bảo các trường Many2one được xử lý đúng khi cập nhật
        if vals.get('phong_ban_id') and not self.env['phong_ban'].browse(vals['phong_ban_id']).exists():
            vals['phong_ban_id'] = False
        if vals.get('chuc_vu_id') and not self.env['chuc_vu'].browse(vals['chuc_vu_id']).exists():
            vals['chuc_vu_id'] = False
        if vals.get('van_ban_id') and not self.env['van_ban_di'].browse(vals['van_ban_id']).exists():
            vals['van_ban_id'] = False
            
        return super(HopDongLaoDong, self).write(vals)
    
    def action_kich_hoat(self):
        """Kích hoạt hợp đồng"""
        self.ensure_one()
        self.write({'trang_thai': 'dang_hieu_luc'})
        
        # Cập nhật thông tin nhân viên
        if self.nhan_vien_id:
            self.nhan_vien_id.write({
                'phong_ban_id': self.phong_ban_id.id if self.phong_ban_id else False,
                'chuc_vu_id': self.chuc_vu_id.id if self.chuc_vu_id else False,
            })
    
    def action_cham_dut(self):
        """Chấm dứt hợp đồng"""
        self.ensure_one()
        return {
            'name': 'Chấm dứt hợp đồng',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.cham.dut.hop.dong',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_hop_dong_id': self.id}
        }
    
    def action_gia_han(self):
        """Gia hạn hợp đồng"""
        self.ensure_one()
        return {
            'name': 'Gia hạn hợp đồng',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.gia.han.hop.dong',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_hop_dong_goc_id': self.id}
        }
    
    def action_view_van_ban(self):
        """Xem văn bản hợp đồng"""
        self.ensure_one()
        return {
            'name': 'Văn bản hợp đồng',
            'type': 'ir.actions.act_window',
            'res_model': 'van_ban_di',
            'res_id': self.van_ban_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
