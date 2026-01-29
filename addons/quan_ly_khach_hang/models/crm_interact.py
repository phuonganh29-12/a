from odoo import models, fields, api

class CrmInteract(models.Model):
    _name = 'crm_interact'
    _description = 'Bảng chứa thông tin tương tác'

    crm_interact_id = fields.Char("Mã tương tác", required=True)
    crm_interact_name = fields.Char("Tên tương tác")
    customer_id = fields.Many2one('customer', string="Khách hàng", required=True, ondelete='cascade')
    interaction_type = fields.Selection([
        ('call', 'Cuộc gọi'),
        ('email', 'Email'),
        ('meeting', 'Meeting')
    ], string="Loại tương tác", required=True)
    date = fields.Datetime("Ngày tương tác", required=True)
    note = fields.Text("Ghi chú về tương tác")
    employee_id = fields.Many2one('nhan_vien', string="Nhân viên", ondelete='set null')

    # Đặt tên hiển thị cho bản ghi
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.crm_interact_id}] {record.crm_interact_name}"
            result.append((record.id, name))
        return result
