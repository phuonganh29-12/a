from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale_order'
    _description = 'Bảng chứa thông tin lịch sử giao dịch'

    sale_order_id = fields.Char("Mã lịch sử giao dịch", required=True)
    sale_order_name = fields.Char("Tên lịch sử giao dịch")
    customer_id = fields.Many2one('customer', string="Khách hàng", required=True, ondelete='cascade')
    date_order = fields.Datetime("Ngày đặt hàng", required=True)
    amount_total = fields.Float("Tổng giá trị đơn hàng", required=True)

    # Đặt tên hiển thị cho bản ghi
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.sale_order_id}] {record.sale_order_name}"
            result.append((record.id, name))
        return result
