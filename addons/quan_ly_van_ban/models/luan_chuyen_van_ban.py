# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

class LuanChuyenVanBan(models.Model):
    _name = 'luan_chuyen_van_ban'
    _description = 'Luân chuyển văn bản'
    _order = 'ngay_chuyen desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char("Mã luân chuyển", required=True, copy=False, readonly=True, 
                       default='New', index=True)
    
    # Văn bản được luân chuyển
    van_ban_di_id = fields.Many2one('van_ban_di', string="Văn bản đi", ondelete='cascade')
    van_ban_den_id = fields.Many2one('van_ban_den', string="Văn bản đến", ondelete='cascade')
    
    # Thông tin luân chuyển
    nguoi_chuyen_id = fields.Many2one('nhan_vien', string="Người chuyển",
                                      default=lambda self: self._get_current_employee(),
                                      tracking=True)
    nguoi_nhan_id = fields.Many2one('nhan_vien', string="Người nhận", required=True, 
                                    tracking=True)
    ngay_chuyen = fields.Datetime("Ngày chuyển", default=fields.Datetime.now, required=True,
                                  tracking=True)
    han_xu_ly = fields.Date("Hạn xử lý", tracking=True)
    
    # Nội dung chuyển
    noi_dung_chuyen = fields.Text("Nội dung chuyển/Ý kiến", required=True, tracking=True,
                                  help="Ý kiến chỉ đạo hoặc yêu cầu xử lý")
    muc_do_uu_tien = fields.Selection([
        ('low', 'Thấp'),
        ('normal', 'Bình thường'),
        ('high', 'Cao'),
        ('urgent', 'Khẩn cấp')
    ], string="Mức độ ưu tiên", default='normal', required=True, tracking=True)
    
    # Trạng thái xử lý
    trang_thai = fields.Selection([
        ('cho_nhan', 'Chờ nhận'),
        ('dang_xu_ly', 'Đang xử lý'),
        ('hoan_thanh', 'Hoàn thành'),
        ('tra_lai', 'Trả lại')
    ], string="Trạng thái", default='cho_nhan', required=True, tracking=True)
    
    # Xử lý
    ngay_nhan = fields.Datetime("Ngày nhận", readonly=True, tracking=True)
    ngay_hoan_thanh = fields.Datetime("Ngày hoàn thành", readonly=True, tracking=True)
    y_kien_xu_ly = fields.Text("Ý kiến xử lý", tracking=True)
    file_dinh_kem = fields.Binary("File đính kèm", attachment=True)
    file_dinh_kem_name = fields.Char("Tên file")
    
    # Theo dõi
    qua_han = fields.Boolean("Quá hạn", compute="_compute_qua_han", store=True)
    so_ngay_con_lai = fields.Integer("Số ngày còn lại", compute="_compute_so_ngay_con_lai")
    
    active = fields.Boolean("Active", default=True)
    
    @api.model
    def _get_current_employee(self):
        """Lấy nhân viên hiện tại - Tạm thời trả về False vì nhan_vien không có user_id"""
        # TODO: Cần thêm trường user_id vào model nhan_vien để liên kết với user
        # user = self.env.user
        # employee = self.env['nhan_vien'].search([('user_id', '=', user.id)], limit=1)
        # return employee.id if employee else False
        return False
    
    @api.model
    def create(self, vals):
        """Tạo mã luân chuyển tự động"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('luan.chuyen.van.ban') or 'New'
        return super(LuanChuyenVanBan, self).create(vals)
    
    @api.depends('han_xu_ly', 'trang_thai', 'ngay_hoan_thanh')
    def _compute_qua_han(self):
        """Kiểm tra văn bản có quá hạn không"""
        today = fields.Date.today()
        for record in self:
            if record.han_xu_ly and record.trang_thai not in ['hoan_thanh', 'tra_lai']:
                record.qua_han = record.han_xu_ly < today
            else:
                record.qua_han = False
    
    @api.depends('han_xu_ly', 'trang_thai')
    def _compute_so_ngay_con_lai(self):
        """Tính số ngày còn lại để xử lý"""
        today = fields.Date.today()
        for record in self:
            if record.han_xu_ly and record.trang_thai not in ['hoan_thanh', 'tra_lai']:
                delta = record.han_xu_ly - today
                record.so_ngay_con_lai = delta.days
            else:
                record.so_ngay_con_lai = 0
    
    def action_nhan_van_ban(self):
        """Nhận văn bản"""
        self.ensure_one()
        if self.trang_thai != 'cho_nhan':
            raise UserError("Chỉ có thể nhận văn bản ở trạng thái 'Chờ nhận'!")
        
        # Kiểm tra quyền
        current_employee = self._get_current_employee()
        if current_employee != self.nguoi_nhan_id.id:
            raise UserError("Chỉ người nhận mới có quyền nhận văn bản!")
        
        self.write({
            'trang_thai': 'dang_xu_ly',
            'ngay_nhan': fields.Datetime.now()
        })
        
        # Gửi thông báo
        self.message_post(
            body=f"Văn bản đã được nhận bởi {self.nguoi_nhan_id.ten_nhan_vien}",
            subject="Nhận văn bản"
        )
    
    def action_hoan_thanh(self):
        """Hoàn thành xử lý văn bản"""
        self.ensure_one()
        if self.trang_thai != 'dang_xu_ly':
            raise UserError("Chỉ có thể hoàn thành văn bản đang xử lý!")
        
        if not self.y_kien_xu_ly:
            raise UserError("Vui lòng nhập ý kiến xử lý trước khi hoàn thành!")
        
        self.write({
            'trang_thai': 'hoan_thanh',
            'ngay_hoan_thanh': fields.Datetime.now()
        })
        
        # Gửi thông báo cho người chuyển
        self.message_post(
            body=f"Văn bản đã được hoàn thành bởi {self.nguoi_nhan_id.ten_nhan_vien}<br/>Ý kiến: {self.y_kien_xu_ly}",
            subject="Hoàn thành xử lý văn bản",
            partner_ids=[self.nguoi_chuyen_id.user_id.partner_id.id] if self.nguoi_chuyen_id.user_id else []
        )
    
    def action_tra_lai(self):
        """Trả lại văn bản cho người chuyển"""
        self.ensure_one()
        if self.trang_thai not in ['cho_nhan', 'dang_xu_ly']:
            raise UserError("Không thể trả lại văn bản ở trạng thái hiện tại!")
        
        if not self.y_kien_xu_ly:
            raise UserError("Vui lòng nhập lý do trả lại!")
        
        self.write({
            'trang_thai': 'tra_lai',
        })
        
        # Gửi thông báo
        self.message_post(
            body=f"Văn bản đã được trả lại<br/>Lý do: {self.y_kien_xu_ly}",
            subject="Trả lại văn bản",
            partner_ids=[self.nguoi_chuyen_id.user_id.partner_id.id] if self.nguoi_chuyen_id.user_id else []
        )
    
    def action_chuyen_tiep(self):
        """Chuyển tiếp văn bản cho người khác"""
        self.ensure_one()
        return {
            'name': 'Chuyển tiếp văn bản',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.chuyen.tiep.van.ban',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_luan_chuyen_goc_id': self.id,
                'default_van_ban_di_id': self.van_ban_di_id.id if self.van_ban_di_id else False,
                'default_van_ban_den_id': self.van_ban_den_id.id if self.van_ban_den_id else False,
            }
        }
    
    @api.constrains('nguoi_chuyen_id', 'nguoi_nhan_id')
    def _check_nguoi_chuyen_nhan(self):
        """Kiểm tra người chuyển và người nhận phải khác nhau"""
        for record in self:
            if record.nguoi_chuyen_id == record.nguoi_nhan_id:
                raise ValidationError("Người chuyển và người nhận không thể là cùng một người!")
    
    @api.constrains('han_xu_ly')
    def _check_han_xu_ly(self):
        """Kiểm tra hạn xử lý phải sau ngày chuyển"""
        for record in self:
            if record.han_xu_ly:
                ngay_chuyen_date = record.ngay_chuyen.date() if record.ngay_chuyen else fields.Date.today()
                if record.han_xu_ly < ngay_chuyen_date:
                    raise ValidationError("Hạn xử lý phải sau hoặc bằng ngày chuyển!")
