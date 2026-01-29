from odoo import models, fields, api

class Note(models.Model):
    _name = 'note'
    _description = 'Bảng chứa thông tin ghi chú'

    note_id = fields.Char("Mã ghi chú", required=True)
    note_name = fields.Char("Tên ghi chú")
    customer_id = fields.Many2one('customer', string="Khách hàng", required=True, ondelete='cascade')
    note = fields.Text("Nội dung ghi chú", required=True)
    date = fields.Datetime("Ngày tạo ghi chú", required=True)
    employee_id = fields.Many2one('nhan_vien', string="Nhân viên", ondelete='set null')

    # Đặt tên hiển thị cho bản ghi
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.note_id}] {record.note_name}"
            result.append((record.id, name))
        return result
