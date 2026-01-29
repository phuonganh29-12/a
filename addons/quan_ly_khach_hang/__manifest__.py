# -*- coding: utf-8 -*-
{
    'name': "quan_ly_khach_hang",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'nhan_su'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/email_marketing_sequence.xml',
        'data/email_template.xml',
        'data/cron.xml',
        'views/customer.xml',
        'views/crm_lead.xml',
        'views/crm_interact.xml',
        # 'views/contract.xml',  # Đã xóa - dùng van_ban_di từ module quan_ly_van_ban
        'views/sale_order.xml',
        'views/note.xml',
        'views/feedback.xml',
        'views/project_task.xml',
        'views/marketing_campaign.xml',
        'views/email_marketing_campaign.xml',
        'views/email_marketing_template.xml',
        'views/customer_care.xml',
        'views/customer_dashboard.xml',
        'wizard/wizard_email_marketing_view.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
