from odoo import models, fields

class LichSuCongTac(models.Model):
    _name = 'lich_su_cong_tac'
    _description = 'Lịch sử công tác'

    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân viên', required=True)
    phong_ban = fields.Char(string='Phòng ban')
    chuc_vu = fields.Char(string='Chức vụ')
    tu_ngay = fields.Date(string='Từ ngày')
    den_ngay = fields.Date(string='Đến ngày')
