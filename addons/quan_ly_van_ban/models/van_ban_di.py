from odoo import models, fields, api
from odoo.exceptions import ValidationError


class VanBanDi(models.Model):
    _name = 'van_ban_di'
    _description = 'Bảng chứa thông tin văn bản đi'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'ten_van_ban'
    _order = 'ngay_van_ban desc, id desc'
    _sql_constraints = [
        ('so_van_ban_unique', 'unique(so_van_ban)', 'Số văn bản phải là duy nhất!'),
    ]

    # Thông tin cơ bản
    so_van_ban = fields.Char("Số văn bản", required=True, index=True, copy=False, default="New", tracking=True)
    ten_van_ban = fields.Char("Tên văn bản", required=True, tracking=True)
    trich_yeu = fields.Text("Trích yếu", tracking=True)
    noi_dung = fields.Html("Nội dung")
    
    # Phân loại
    loai_van_ban_id = fields.Many2one('loai_van_ban', string="Loại văn bản", required=True, tracking=True)
    do_uu_tien = fields.Selection([
        ('low', 'Thấp'),
        ('normal', 'Bình thường'),
        ('high', 'Cao'),
        ('urgent', 'Khẩn cấp')
    ], string="Độ ưu tiên", default='normal', required=True, tracking=True)
    
    do_mat = fields.Selection([
        ('normal', 'Thường'),
        ('internal', 'Nội bộ'),
        ('confidential', 'Mật'),
        ('top_secret', 'Tuyệt mật')
    ], string="Độ mật", default='normal', tracking=True)
    
    # Thời gian
    ngay_van_ban = fields.Date("Ngày văn bản", required=True, default=fields.Date.today, tracking=True)
    ngay_gui = fields.Date("Ngày gửi", tracking=True)
    han_hieu_luc = fields.Date("Hạn hiệu lực")
    
    # File đính kèm
    attachment_ids = fields.Many2many(
        'ir.attachment', 
        'van_ban_di_attachment_rel',
        'van_ban_di_id', 
        'attachment_id',
        string="File đính kèm"
    )
    so_file_dinh_kem = fields.Integer("Số file", compute='_compute_so_file_dinh_kem', store=True)
    
    # Liên kết với khách hàng (Sổ hóa hồ sơ)
    customer_id = fields.Many2one('customer', string="Khách hàng", tracking=True, 
                                  help="Khách hàng liên quan đến văn bản này")
    
    # Đơn vị/Người nhận
    don_vi_nhan = fields.Char("Đơn vị nhận")
    nguoi_nhan = fields.Char("Người nhận")
    
    # Người xử lý (liên kết với module nhan_su)
    nhan_vien_soan_thao_id = fields.Many2one('nhan_vien', string="Người soạn thảo", tracking=True)
    nguoi_ky_id = fields.Many2one('nhan_vien', string="Người ký", tracking=True)
    
    # Trạng thái
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('waiting_approve', 'Chờ phê duyệt'),
        ('approved', 'Đã phê duyệt'),
        ('waiting_sign', 'Chờ ký'),
        ('signed', 'Đã ký'),
        ('sent', 'Đã gửi'),
        ('cancelled', 'Đã hủy')
    ], string="Trạng thái", default='draft', required=True, tracking=True)
    
    # Liên kết
    van_ban_den_tra_loi_id = fields.Many2one('van_ban_den', string="Trả lời văn bản đến")
    
    # Hợp đồng lao động (nếu văn bản này là hợp đồng) - ĐÃ TẮT
    # hop_dong_lao_dong_id = fields.One2many('hop_dong_lao_dong', 'van_ban_id', string="Hợp đồng lao động")
    # la_hop_dong = fields.Boolean("Là hợp đồng lao động", compute='_compute_la_hop_dong', store=True)
    
    # Luân chuyển văn bản
    luan_chuyen_ids = fields.One2many('luan_chuyen_van_ban', 'van_ban_di_id', string="Lịch sử luân chuyển")
    so_lan_luan_chuyen = fields.Integer("Số lần luân chuyển", compute='_compute_so_lan_luan_chuyen', store=True)
    nhan_vien_dang_xu_ly_ids = fields.Many2many('nhan_vien', string="NV đang xử lý", 
                                                  compute='_compute_nhan_vien_dang_xu_ly', store=False)
    
    # Thông tin khác
    active = fields.Boolean("Hoạt động", default=True)
    ghi_chu = fields.Text("Ghi chú")
    
    # Computed fields
    ngay_het_han = fields.Integer("Số ngày đến hạn", compute='_compute_ngay_het_han', store=True)
    qua_han = fields.Boolean("Quá hạn", compute='_compute_qua_han', store=True)

    @api.depends('attachment_ids')
    def _compute_so_file_dinh_kem(self):
        """Tính số lượng file đính kèm"""
        for record in self:
            record.so_file_dinh_kem = len(record.attachment_ids)
    
    # @api.depends('hop_dong_lao_dong_id')
    # def _compute_la_hop_dong(self):
    #     """Kiểm tra văn bản có phải là hợp đồng lao động"""
    #     for record in self:
    #         record.la_hop_dong = bool(record.hop_dong_lao_dong_id)
    
    @api.depends('luan_chuyen_ids')
    def _compute_so_lan_luan_chuyen(self):
        """Tính số lần luân chuyển"""
        for record in self:
            record.so_lan_luan_chuyen = len(record.luan_chuyen_ids)
    
    def _compute_nhan_vien_dang_xu_ly(self):
        """Lấy danh sách nhân viên đang xử lý"""
        for record in self:
            luan_chuyen_active = record.luan_chuyen_ids.filtered(
                lambda x: x.trang_thai in ['cho_nhan', 'dang_xu_ly']
            )
            record.nhan_vien_dang_xu_ly_ids = luan_chuyen_active.mapped('nguoi_nhan_id')

    @api.depends('han_hieu_luc')
    def _compute_ngay_het_han(self):
        """Tính số ngày đến hạn hiệu lực"""
        today = fields.Date.today()
        for record in self:
            if record.han_hieu_luc:
                delta = record.han_hieu_luc - today
                record.ngay_het_han = delta.days
            else:
                record.ngay_het_han = 0

    @api.depends('han_hieu_luc')
    def _compute_qua_han(self):
        """Kiểm tra văn bản có quá hạn không"""
        today = fields.Date.today()
        for record in self:
            if record.han_hieu_luc:
                record.qua_han = record.han_hieu_luc < today
            else:
                record.qua_han = False

    @api.constrains('ngay_van_ban', 'ngay_gui')
    def _check_dates(self):
        """Kiểm tra ngày tháng hợp lệ"""
        for record in self:
            if record.ngay_gui and record.ngay_van_ban:
                if record.ngay_gui < record.ngay_van_ban:
                    raise ValidationError("Ngày gửi không được trước ngày văn bản!")

    @api.constrains('ngay_van_ban', 'han_hieu_luc')
    def _check_han_hieu_luc(self):
        """Kiểm tra hạn hiệu lực"""
        for record in self:
            if record.han_hieu_luc and record.ngay_van_ban:
                if record.han_hieu_luc < record.ngay_van_ban:
                    raise ValidationError("Hạn hiệu lực không được trước ngày văn bản!")

    @api.model
    def create(self, vals):
        """Tạo số văn bản tự động và đồng bộ với Contract"""
        if vals.get('so_van_ban', 'New') == 'New':
            # Tạo số văn bản theo format: VBĐ-YYYY-XXXX
            year = fields.Date.today().year
            sequence = self.env['ir.sequence'].next_by_code('van_ban_di.sequence')
            if not sequence:
                # Nếu chưa có sequence, tạo thủ công
                count = self.search_count([]) + 1
                sequence = str(count).zfill(4)
            vals['so_van_ban'] = f'VBĐ-{year}-{sequence}'
        
        record = super(VanBanDi, self).create(vals)
        return record

    def name_get(self):
        """Hiển thị tên văn bản"""
        result = []
        for record in self:
            name = f"[{record.so_van_ban}] {record.ten_van_ban}"
            result.append((record.id, name))
        return result

    def action_submit_approve(self):
        """Chuyển trạng thái sang chờ phê duyệt"""
        self.write({'trang_thai': 'waiting_approve'})

    def action_approve(self):
        """Phê duyệt văn bản"""
        self.write({'trang_thai': 'approved'})

    def action_request_sign(self):
        """Yêu cầu ký"""
        self.write({'trang_thai': 'waiting_sign'})

    def action_sign(self):
        """Ký văn bản"""
        self.write({'trang_thai': 'signed'})

    def action_send(self):
        """Gửi văn bản"""
        self.write({'trang_thai': 'sent', 'ngay_gui': fields.Date.today()})

    def action_cancel(self):
        """Hủy văn bản"""
        self.write({'trang_thai': 'cancelled'})

    def action_reset_to_draft(self):
        """Chuyển về nháp"""
        self.write({'trang_thai': 'draft'})
    
    def action_luan_chuyen(self):
        """Mở wizard luân chuyển văn bản"""
        self.ensure_one()
        return {
            'name': 'Luân chuyển văn bản',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.luan.chuyen.van.ban',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_van_ban_di_id': self.id,
            }
        }
    

