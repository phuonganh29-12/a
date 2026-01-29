from odoo import models, fields, api
from odoo.exceptions import ValidationError


class VanBanDen(models.Model):
    _name = 'van_ban_den'
    _description = 'Bảng chứa thông tin văn bản đến'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'ten_van_ban'
    _order = 'ngay_nhan desc, id desc'
    _sql_constraints = [
        ('so_van_ban_unique', 'unique(so_van_ban)', 'Số văn bản phải là duy nhất!'),
    ]

    # Thông tin cơ bản
    so_van_ban = fields.Char("Số văn bản", required=True, index=True, tracking=True, 
                              help="Số văn bản theo đơn vị gửi")
    so_den = fields.Char("Số đến", copy=False, default="New", tracking=True,
                         help="Số văn bản đến của đơn vị mình")
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
    ngay_van_ban = fields.Date("Ngày văn bản", required=True, tracking=True,
                                help="Ngày văn bản theo đơn vị gửi")
    ngay_nhan = fields.Date("Ngày nhận", required=True, default=fields.Date.today, tracking=True)
    han_xu_ly = fields.Date("Hạn xử lý", tracking=True)
    ngay_hoan_thanh = fields.Date("Ngày hoàn thành", tracking=True)
    
    # Liên kết với khách hàng (Sổ hóa hồ sơ)
    customer_id = fields.Many2one('customer', string="Khách hàng", tracking=True,
                                  help="Khách hàng gửi/liên quan đến văn bản này")
    
    # File đính kèm
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'van_ban_den_attachment_rel',
        'van_ban_den_id',
        'attachment_id',
        string="File đính kèm"
    )
    so_file_dinh_kem = fields.Integer("Số file", compute='_compute_so_file_dinh_kem', store=True)
    
    # Đơn vị/Người gửi
    don_vi_gui = fields.Char("Đơn vị gửi", required=True, tracking=True)
    nguoi_gui = fields.Char("Người ký (đơn vị gửi)")
    noi_nhan = fields.Char("Nơi nhận")
    
    # Người xử lý (liên kết với module nhan_su)
    nhan_vien_tiep_nhan_id = fields.Many2one('nhan_vien', string="Người tiếp nhận", tracking=True)
    
    # Xử lý
    trang_thai = fields.Selection([
        ('new', 'Mới nhận'),
        ('assigned', 'Đã phân công'),
        ('processing', 'Đang xử lý'),
        ('waiting_reply', 'Chờ trả lời'),
        ('replied', 'Đã trả lời'),
        ('completed', 'Hoàn thành'),
        ('archived', 'Lưu trữ')
    ], string="Trạng thái", default='new', required=True, tracking=True)
    
    # Liên kết văn bản trả lời
    van_ban_tra_loi_ids = fields.One2many('van_ban_di', 'van_ban_den_tra_loi_id', string="Văn bản trả lời")
    
    # Thông tin khác
    active = fields.Boolean("Hoạt động", default=True)
    ghi_chu = fields.Text("Ghi chú")
    y_kien_xu_ly = fields.Text("Ý kiến xử lý")
    
    # Computed fields
    ngay_con_lai = fields.Integer("Số ngày còn lại", compute='_compute_ngay_con_lai', store=True)
    qua_han = fields.Boolean("Quá hạn", compute='_compute_qua_han', store=True)
    thoi_gian_xu_ly = fields.Integer("Thời gian xử lý (ngày)", compute='_compute_thoi_gian_xu_ly', store=True)

    @api.depends('attachment_ids')
    def _compute_so_file_dinh_kem(self):
        """Tính số lượng file đính kèm"""
        for record in self:
            record.so_file_dinh_kem = len(record.attachment_ids)

    @api.depends('han_xu_ly')
    def _compute_ngay_con_lai(self):
        """Tính số ngày còn lại để xử lý"""
        today = fields.Date.today()
        for record in self:
            if record.han_xu_ly:
                delta = record.han_xu_ly - today
                record.ngay_con_lai = delta.days
            else:
                record.ngay_con_lai = 0

    @api.depends('han_xu_ly', 'trang_thai')
    def _compute_qua_han(self):
        """Kiểm tra văn bản có quá hạn không"""
        today = fields.Date.today()
        for record in self:
            if record.han_xu_ly and record.trang_thai not in ['completed', 'archived']:
                record.qua_han = record.han_xu_ly < today
            else:
                record.qua_han = False

    @api.depends('ngay_nhan', 'ngay_hoan_thanh')
    def _compute_thoi_gian_xu_ly(self):
        """Tính thời gian xử lý thực tế"""
        for record in self:
            if record.ngay_hoan_thanh and record.ngay_nhan:
                delta = record.ngay_hoan_thanh - record.ngay_nhan
                record.thoi_gian_xu_ly = delta.days
            else:
                record.thoi_gian_xu_ly = 0

    @api.constrains('ngay_van_ban', 'ngay_nhan')
    def _check_dates(self):
        """Kiểm tra ngày tháng hợp lệ"""
        for record in self:
            if record.ngay_nhan and record.ngay_van_ban:
                if record.ngay_nhan < record.ngay_van_ban:
                    raise ValidationError("Ngày nhận không được trước ngày văn bản!")

    @api.constrains('ngay_nhan', 'han_xu_ly')
    def _check_han_xu_ly(self):
        """Kiểm tra hạn xử lý"""
        for record in self:
            if record.han_xu_ly and record.ngay_nhan:
                if record.han_xu_ly < record.ngay_nhan:
                    raise ValidationError("Hạn xử lý không được trước ngày nhận!")

    @api.model
    def create(self, vals):
        """Tạo số đến tự động"""
        if vals.get('so_den', 'New') == 'New':
            # Tạo số đến theo format: VBĐến-YYYY-XXXX
            year = fields.Date.today().year
            sequence = self.env['ir.sequence'].next_by_code('van_ban_den.sequence')
            if not sequence:
                count = self.search_count([]) + 1
                sequence = str(count).zfill(4)
            vals['so_den'] = f'VBĐến-{year}-{sequence}'
        return super(VanBanDen, self).create(vals)

    def name_get(self):
        """Hiển thị tên văn bản"""
        result = []
        for record in self:
            name = f"[{record.so_den}] {record.ten_van_ban}"
            result.append((record.id, name))
        return result

    def action_assign(self):
        """Phân công xử lý"""
        self.write({'trang_thai': 'assigned'})

    def action_start_processing(self):
        """Bắt đầu xử lý"""
        self.write({'trang_thai': 'processing'})

    def action_request_reply(self):
        """Yêu cầu trả lời"""
        self.write({'trang_thai': 'waiting_reply'})

    def action_replied(self):
        """Đã trả lời"""
        self.write({'trang_thai': 'replied'})

    def action_complete(self):
        """Hoàn thành xử lý"""
        self.write({
            'trang_thai': 'completed',
            'ngay_hoan_thanh': fields.Date.today()
        })

    def action_archive_document(self):
        """Lưu trữ văn bản"""
        self.write({'trang_thai': 'archived'})

    def action_create_reply(self):
        """Tạo văn bản trả lời"""
        self.ensure_one()
        return {
            'name': 'Tạo văn bản trả lời',
            'type': 'ir.actions.act_window',
            'res_model': 'van_ban_di',
            'view_mode': 'form',
            'context': {
                'default_van_ban_den_tra_loi_id': self.id,
                'default_ten_van_ban': f'Trả lời: {self.ten_van_ban}',
                'default_don_vi_nhan': self.don_vi_gui,
                'default_loai_van_ban_id': self.loai_van_ban_id.id,
            },
            'target': 'current',
        }

