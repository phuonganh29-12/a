from odoo import models, fields, api


class LoaiVanBan(models.Model):
    _name = 'loai_van_ban'
    _description = 'Bảng chứa thông tin loại văn bản'
    _rec_name = 'ten_loai_van_ban'
    _order = 'sequence, ten_loai_van_ban'
    _sql_constraints = [
        ('ma_loai_van_ban_unique', 'unique(ma_loai_van_ban)', 'Mã loại văn bản phải là duy nhất!'),
    ]

    # Thông tin cơ bản
    ma_loai_van_ban = fields.Char("Mã loại", required=True, index=True)
    ten_loai_van_ban = fields.Char("Tên loại văn bản", required=True)
    mo_ta = fields.Text("Mô tả")
    
    # Thứ tự hiển thị
    sequence = fields.Integer("Thứ tự", default=10)
    
    # Phân loại theo hướng
    huong_van_ban = fields.Selection([
        ('both', 'Cả đi và đến'),
        ('outgoing', 'Chỉ văn bản đi'),
        ('incoming', 'Chỉ văn bản đến')
    ], string="Hướng văn bản", default='both', required=True,
       help="Loại văn bản này dùng cho văn bản đi, đến hay cả hai")
    
    # Màu sắc (để phân biệt trên giao diện)
    color = fields.Integer("Màu sắc")
    
    # Thông tin khác
    active = fields.Boolean("Hoạt động", default=True)
    
    # Quan hệ
    van_ban_di_ids = fields.One2many('van_ban_di', 'loai_van_ban_id', string="Văn bản đi")
    van_ban_den_ids = fields.One2many('van_ban_den', 'loai_van_ban_id', string="Văn bản đến")
    
    # Computed fields
    so_van_ban_di = fields.Integer("Số VB đi", compute='_compute_so_van_ban', store=True)
    so_van_ban_den = fields.Integer("Số VB đến", compute='_compute_so_van_ban', store=True)
    tong_van_ban = fields.Integer("Tổng số VB", compute='_compute_so_van_ban', store=True)

    @api.depends('van_ban_di_ids', 'van_ban_den_ids')
    def _compute_so_van_ban(self):
        """Tính số lượng văn bản"""
        for record in self:
            record.so_van_ban_di = len(record.van_ban_di_ids)
            record.so_van_ban_den = len(record.van_ban_den_ids)
            record.tong_van_ban = record.so_van_ban_di + record.so_van_ban_den

    def name_get(self):
        """Hiển thị tên loại văn bản"""
        result = []
        for record in self:
            name = f"[{record.ma_loai_van_ban}] {record.ten_loai_van_ban}"
            result.append((record.id, name))
        return result

