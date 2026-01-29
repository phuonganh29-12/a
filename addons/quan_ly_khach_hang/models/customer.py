import re
from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date

class Customer(models.Model):
    _name = 'customer'
    _description = 'Bảng chứa thông tin khách hàng'
    _sql_constraints = [
        ('customer_id_unique', 'unique(customer_id)', 'Mã khách hàng phải là duy nhất!'),
    ]
    near_birthday = fields.Boolean(
    "Gần tới sinh nhật",
    compute="_compute_near_birthday",
    store=False,
    help="Kiểm tra xem có gần tới sinh nhật khách hàng (trong vòng 7 ngày) hay không"
    )

    # Các trường cơ bản
    customer_id = fields.Char("Mã khách hàng", required=True, index=True, copy=False, default="New")
    customer_name = fields.Char("Tên khách hàng")
    email = fields.Char("Email")
    phone = fields.Char("Số điện thoại")
    address = fields.Char("Địa chỉ")
    gender = fields.Selection([
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác')
    ], string="Giới tính")
    date_of_birth = fields.Date("Ngày sinh")
    age = fields.Integer("Tuổi", compute="_compute_age", store=True)
    income_level = fields.Selection([
        ('0-20tr', '0-20 triệu/tháng'),
        ('20-50tr', '20-50 triệu/tháng'),
        ('50-70tr', '50-70 triệu/tháng'),
        ('70-100tr', '70-100 triệu/tháng'),
        ('100tr+', '100 triệu trở lên')
    ], string="Mức thu nhập")
    image = fields.Binary("Ảnh", attachment=True)
    company_name = fields.Char("Tên công ty")
    tax_code = fields.Char("Mã số thuế")
    customer_type = fields.Selection([
        ('individual', 'Cá nhân'),
        ('company', 'Công ty')
    ], string="Loại khách hàng", default="individual")
    active = fields.Boolean("Active", default=True)
    customer_status = fields.Selection([
        ('new', 'Mới'),
        ('active', 'Đang hoạt động'),
        ('inactive', 'Không hoạt động')
    ], string="Trạng thái", default="new")
    
    # Phân loại khách hàng
    loai_khach_hang_id = fields.Many2one('loai.khach.hang', string="Loại KH", 
                                         help="Phân loại khách hàng (VIP, Thường, Tiềm năng...)")
    nguon_khach_hang_id = fields.Many2one('nguon.khach.hang', string="Nguồn KH",
                                          help="Nguồn tìm kiếm khách hàng (Facebook, Website, Giới thiệu...)")
    tinh_trang_khach_hang_id = fields.Many2one('tinh.trang.khach.hang', string="Tình trạng",
                                                help="Tình trạng hiện tại của khách hàng")

    # Trường liên kết với các model khác
    sale_order_ids = fields.One2many('sale_order', inverse_name='customer_id', string="Đơn hàng")
    interact_ids = fields.One2many('crm_interact', inverse_name='customer_id', string="Tương tác")
    # contract_ids = fields.One2many('contract', inverse_name='customer_id', string="Hợp đồng")  # Đã xóa - dùng van_ban_di
    lead_ids = fields.One2many('crm_lead', inverse_name='customer_id', string="Cơ hội")
    feedback_ids = fields.One2many('feedback', inverse_name='customer_id', string="Phản hồi")
    task_ids = fields.One2many('project_task', inverse_name='customer_id', string="Nhiệm vụ dự án")
    note_ids = fields.One2many('note', inverse_name='customer_id', string="Ghi chú")
    
    # Liên kết văn bản - Sổ hóa hồ sơ
    # NOTE: Các field này sẽ được thêm bởi module quan_ly_van_ban
    # van_ban_di_ids = fields.One2many('van_ban_di', inverse_name='customer_id', string="Văn bản đi")
    # van_ban_den_ids = fields.One2many('van_ban_den', inverse_name='customer_id', string="Văn bản đến")
    
    # Nhân viên phụ trách từ module nhan_su
    nhan_vien_phu_trach_id = fields.Many2one('nhan_vien', string="Nhân viên phụ trách",
                                             help="Nhân viên chăm sóc khách hàng này")
    
    # Email Marketing
    email_marketing_log_ids = fields.One2many('email.marketing.log', 'customer_id', string="Lịch sử email marketing")
    so_email_nhan = fields.Integer("Số email nhận", compute='_compute_email_stats', store=True)
    so_email_mo = fields.Integer("Số email mở", compute='_compute_email_stats', store=True)
    
    # Customer Care
    customer_care_ids = fields.One2many('customer.care', 'customer_id', string="Lịch sử chăm sóc")
    so_lan_cham_soc = fields.Integer("Số lần chăm sóc", compute='_compute_care_stats', store=True)
    lan_cham_soc_cuoi = fields.Datetime("Lần chăm sóc cuối", compute='_compute_care_stats', store=True)

    # Trường tính toán (computed fields)
    # total_contracts = fields.Integer("Tổng số hợp đồng", compute="_compute_total_contracts", store=True)  # Đã xóa - dùng van_ban_di
    total_interactions = fields.Integer("Tổng số tương tác", compute="_compute_total_interactions", store=True)
    total_sale_orders = fields.Integer("Tổng số đơn hàng", compute="_compute_total_sale_orders", store=True)
    total_amount = fields.Float("Tổng số tiền đơn hàng", compute="_compute_total_amount", store=True)

    age_group = fields.Selection([
        ('0-20', '0-20 tuổi'),
        ('20-30', '20-30 tuổi'),
        ('30-40', '30-40 tuổi'),
        ('40-50', '40-50 tuổi'),
        ('50+', 'Trên 50 tuổi')
    ], string="Nhóm độ tuổi", compute="_compute_age_group", store=True)

    # Trường mới: Nhóm số đơn hàng
    sale_order_group = fields.Selection([
        ('0', '0 đơn hàng'),
        ('1-5', '1-5 đơn hàng'),
        ('5-10', '5-10 đơn hàng'),
        ('10+', 'Trên 10 đơn hàng')
    ], string="Nhóm số đơn hàng", compute="_compute_sale_order_group", store=True)

    @api.depends('age')
    def _compute_age_group(self):
        for record in self:
            age = record.age
            if age <= 20:
                record.age_group = '0-20'
            elif 20 < age <= 30:
                record.age_group = '20-30'
            elif 30 < age <= 40:
                record.age_group = '30-40'
            elif 40 < age <= 50:
                record.age_group = '40-50'
            else:
                record.age_group = '50+'

    @api.depends('total_sale_orders')
    def _compute_sale_order_group(self):
        for record in self:
            orders = record.total_sale_orders
            if orders == 0:
                record.sale_order_group = '0'
            elif 1 <= orders <= 5:
                record.sale_order_group = '1-5'
            elif 5 < orders <= 10:
                record.sale_order_group = '5-10'
            else:
                record.sale_order_group = '10+'

    # Ràng buộc cho email
    @api.constrains('email')
    def _check_email(self):
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        for record in self:
            if record.email and not re.match(email_pattern, record.email):
                raise ValidationError("Email không hợp lệ: %s" % record.email)
            
    @api.constrains('phone')
    def _check_phone(self):
        phone_pattern = r'^(\+84|0)[1-9]\d{8,9}$'  # Ví dụ: +84981234567 hoặc 0981234567
        for record in self:
            if record.phone and not re.match(phone_pattern, record.phone):
                raise ValidationError("Số điện thoại không hợp lệ! Ví dụ hợp lệ: 0987654321 hoặc +84987654321")
            
    # Tính toán tổng số hợp đồng
    # @api.depends('contract_ids')
    # def _compute_total_contracts(self):
    #     for record in self:
    #         record.total_contracts = len(record.contract_ids)
    
    # Tính toán tổng số tương tác
    @api.depends('interact_ids')
    def _compute_total_interactions(self):
        for record in self:
            record.total_interactions = len(record.interact_ids)

    # Tính toán tổng số đơn hàng
    @api.depends('sale_order_ids')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.sale_order_ids.mapped('amount_total')) or 0.0
    
    @api.depends('email_marketing_log_ids')
    def _compute_email_stats(self):
        """Tính thống kê email marketing"""
        for record in self:
            record.so_email_nhan = len(record.email_marketing_log_ids)
            record.so_email_mo = len(record.email_marketing_log_ids.filtered(lambda l: l.da_mo))
    
    @api.depends('customer_care_ids')
    def _compute_care_stats(self):
        """Tính thống kê chăm sóc khách hàng"""
        for record in self:
            care_completed = record.customer_care_ids.filtered(lambda c: c.trang_thai == 'completed')
            record.so_lan_cham_soc = len(care_completed)
            if care_completed:
                record.lan_cham_soc_cuoi = max(care_completed.mapped('ngay_cham_soc'))
            else:
                record.lan_cham_soc_cuoi = False

    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):
        today = fields.Date.today()
        for record in self:
            if record.date_of_birth:
            # Kiểm tra ngày trong tương lai
                if record.date_of_birth > today:
                    raise ValidationError("Ngày sinh không được vượt quá ngày hiện tại!")
            # Kiểm tra ngày hợp lệ
                try:
                    date(record.date_of_birth.year, record.date_of_birth.month, record.date_of_birth.day)
                except ValueError:
                    raise ValidationError("Ngày sinh không hợp lệ!")

    @api.depends('date_of_birth')
    def _compute_age(self):
        today = fields.Date.today()
        for record in self:
            record.age = 0
            if record.date_of_birth:
                record.age = (today - record.date_of_birth).days // 365

    @api.depends('date_of_birth')
    def _compute_near_birthday(self):
        today = fields.Date.today()
        for record in self:
            if record.date_of_birth:
                birthday = record.date_of_birth.replace(year=today.year)
                # Nếu sinh nhật đã qua trong năm nay, chuyển sang năm sau
                if birthday < today:
                    birthday = birthday.replace(year=today.year + 1)
                days_until_birthday = (birthday - today).days
                record.near_birthday = 0 <= days_until_birthday <= 7
            else:
                record.near_birthday = False

    @api.constrains('customer_name', 'email', 'phone', 'customer_type', 'company_name', 'tax_code')
    def _check_required_fields(self):
        for record in self:
            # Kiểm tra các trường bắt buộc cố định
            if not record.customer_name:
                raise ValidationError("Vui lòng nhập Tên khách hàng!")
            if not record.email:
                raise ValidationError("Vui lòng nhập Email!")
            if not record.phone:
                raise ValidationError("Vui lòng nhập Số điện thoại!")
            
            # Kiểm tra các trường bắt buộc động (khi customer_type là company)
            if record.customer_type == 'company':
                if not record.company_name:
                    raise ValidationError("Vui lòng nhập Tên công ty!")
                if not record.tax_code:
                    raise ValidationError("Vui lòng nhập Mã số thuế!")
                
    # Đặt tên hiển thị cho bản ghi
    def name_get(self):
        result = []
        for record in self:
            if record.customer_type == 'company':
                name = f"[{record.customer_id}] {record.customer_name} (Công ty)"
            else:
                name = f"[{record.customer_id}] {record.customer_name}"
            result.append((record.id, name))
        return result

    @api.model
    def create(self, vals):
        if vals.get('customer_id', 'New') == 'New':
            sequence = self.env['ir.sequence'].search([('code', '=', 'customer.id')], limit=1)
        # Lấy mã lớn nhất hiện có
            max_record = self.search([], order='customer_id desc', limit=1)
            max_code = max_record.customer_id if max_record else 'KH00000'
        # Kiểm tra và lấy số tiếp theo
            try:
                next_num = int(max_code.replace('KH', '')) + 1
            except ValueError:
                next_num = 1  # Bắt đầu từ 1 nếu không có mã hợp lệ
            sequence.write({'number_next': next_num})
            vals['customer_id'] = self.env['ir.sequence'].next_by_code('customer.id') or 'New'
        return super(Customer, self).create(vals)
    
    def action_send_birthday_email(self):
        """Gửi email chúc mừng sinh nhật cho khách hàng"""
        self.ensure_one()  # Đảm bảo chỉ xử lý một bản ghi
    
        if not self.email:
            raise ValidationError("Khách hàng này chưa có email!")
    
    # Tạo template email nếu chưa tồn tại
        template = self.env.ref('quan_ly_khach_hang.mail_template_customer_birthday', raise_if_not_found=False)
        if not template:
            template = self.env['mail.template'].create({
                'name': 'Chúc mừng sinh nhật khách hàng',
                'subject': 'Chúc mừng sinh nhật - {{ object.customer_name }}',
                'model_id': self.env['ir.model']._get('customer').id,
                'email_from': '${user.email_formatted | safe}',
                'email_to': '${object.email | safe}',
                'body_html': """
                    <div style="margin: 0px; padding: 0px;">
                        <p>Kính gửi <strong>${object.customer_name}</strong>,</p>
                        <p>Chúng tôi xin gửi lời chúc mừng sinh nhật tốt đẹp nhất đến bạn! 
                        Chúc bạn một ngày sinh nhật thật vui vẻ, hạnh phúc và thành công.</p>
                        <p>Cảm ơn bạn đã luôn đồng hành cùng chúng tôi.</p>
                        <p>Trân trọng,<br/>
                        Đội ngũ công ty chúng tôi</p>
                    </div>
                """,
            })
    
    # Gửi email
        template.send_mail(self.id, force_send=True)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': f'Email chúc mừng sinh nhật đã được gửi tới {self.email}',
                'type': 'success',
                'sticky': False,
            }
        }

    # Thêm vào cuối class Customer trong customer.py
    def action_send_welcome_email(self):
        """Gửi email chào mừng cho khách hàng"""
        self.ensure_one()  # Đảm bảo chỉ xử lý một bản ghi
    
        if not self.email:
            raise ValidationError("Khách hàng này chưa có email!")
    
    # Tạo template email nếu chưa tồn tại
        template = self.env.ref('quan_ly_khach_hang.mail_template_customer_welcome', raise_if_not_found=False)
        if not template:
            template = self.env['mail.template'].create({
                'name': 'Chào mừng khách hàng mới',
                'subject': 'Chào mừng bạn đến với Công ty chúng tôi - {{ object.customer_name }}',
                'model_id': self.env['ir.model']._get('customer').id,
                'email_from': '${user.email_formatted | safe}',
                'email_to': '${object.email | safe}',
                'body_html': """
                    <div style="margin: 0px; padding: 0px;">
                        <p>Kính gửi <strong>${object.customer_name}</strong>,</p>
                        <p>Chào mừng bạn đến với Công ty chúng tôi! 
                        Chúng tôi rất vui được đồng hành cùng bạn trong hành trình sắp tới.</p>
                        <p>Nếu bạn có bất kỳ câu hỏi nào, đừng ngần ngại liên hệ với chúng tôi qua email này hoặc số điện thoại ${user.company_id.phone}.</p>
                        <p>Trân trọng,<br/>
                        Đội ngũ Công ty chúng tôi</p>
                    </div>
                """,
            })
    
    # Gửi email
        template.send_mail(self.id, force_send=True)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': f'Email chào mừng đã được gửi tới {self.email}',
                'type': 'success',
                'sticky': False,
            }
    }

    #def action_send_welcome_email(self):
    #   """Gửi email chào mừng cho khách hàng"""
    #    self.ensure_one()   

    @api.depends('interact_ids')
    def _compute_recent_interactions(self):
        today = fields.Date.today()
        start_of_month = today.replace(day=1)
        for record in self:
            recent = record.interact_ids.filtered(
                lambda x: x.date and x.date.date() >= start_of_month
            )
            record.recent_interactions = len(recent)
    
    # @api.depends('van_ban_di_ids', 'van_ban_den_ids')
    # def _compute_total_van_ban(self):
    #     """Tính tổng số văn bản của khách hàng"""
    #     for record in self:
    #         record.total_van_ban = len(record.van_ban_di_ids) + len(record.van_ban_den_ids)