from odoo import models, fields, api
from datetime import datetime

class ProjectTask(models.Model):
    _name = 'project_task'
    _description = 'Bảng chứa thông tin nhiệm vụ'

    project_task_id = fields.Char("Mã nhiệm vụ", required=True)
    customer_id = fields.Many2one('customer', string="Khách hàng", required=True, ondelete='cascade')
    name = fields.Char("Tên nhiệm vụ", required=True)
    deadline = fields.Date("Hạn chót", required=True)
    actual_completion_date = fields.Date("Thời gian hoàn thành thực tế")
    employee_id = fields.Many2one('nhan_vien', string="Nhân viên phụ trách", ondelete='set null')
    is_overdue = fields.Boolean("Quá hạn", compute="_compute_is_overdue", store=True)

    # Trường tính toán để xác định nhiệm vụ có bị quá hạn hay không
    @api.depends('deadline', 'actual_completion_date')
    def _compute_is_overdue(self):
        for record in self:
            if record.actual_completion_date:
                record.is_overdue = record.actual_completion_date > record.deadline
            else:
                record.is_overdue = False

    # Đặt tên hiển thị cho bản ghi
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.project_task_id}] {record.name}"
            result.append((record.id, name))
        return result
