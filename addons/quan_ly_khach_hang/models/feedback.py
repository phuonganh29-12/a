from odoo import models, fields, api

class Feedback(models.Model):
    _name = 'feedback'
    _description = 'Bảng chứa thông tin phản hồi'

    feedback_id = fields.Char("Mã phản hồi", required=True)
    feedback_name = fields.Char("Tên phản hồi")
    customer_id = fields.Many2one('customer', string="Khách hàng", required=True, ondelete='cascade')
    feedback = fields.Text("Nội dung phản hồi", required=True)
    feedback_date = fields.Datetime("Ngày phản hồi", required=True)
    rating = fields.Selection([
        ('1', '1 sao'),
        ('2', '2 sao'),
        ('3', '3 sao'),
        ('4', '4 sao'),
        ('5', '5 sao')
    ], string="Đánh giá", required=True)
    employee_id = fields.Many2one('nhan_vien', string="Nhân viên", ondelete='set null')

    # Đặt tên hiển thị cho bản ghi
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.feedback_id}] {record.feedback_name}"
            result.append((record.id, name))
        return result
