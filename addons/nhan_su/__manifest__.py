# -*- coding: utf-8 -*-
{
    'name': "Quản lý Nhân sự",

    'summary': """
        Quản lý thông tin nhân viên, phòng ban, chức vụ và lịch sử làm việc""",

    'description': """
        Module quản lý nhân sự bao gồm:
        - Quản lý thông tin nhân viên
        - Quản lý phòng ban (có cấu trúc phân cấp)
        - Quản lý chức vụ
        - Theo dõi lịch sử làm việc của nhân viên
        - Tự động tính toán tuổi, số năm kinh nghiệm
        - Validation email, số điện thoại
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'version': '1.0.0',

    # Module phụ thuộc
    'depends': ['base', 'mail'],

    # Dữ liệu luôn load
    'data': [
        'security/ir.model.access.csv',
        'views/phong_ban.xml',
        'views/chuc_vu.xml',
        # 'views/hop_dong_lao_dong.xml',  # Đã tắt
        'views/nhan_vien.xml',
        'views/lich_su_lam_viec.xml',
        # 'wizard/wizard_hop_dong_view.xml',  # Đã tắt
        'views/menu.xml',
    ],
    
    # Demo data
    'demo': [
        'demo/demo.xml',
    ],
    
    # Module có thể cài đặt
    'installable': True,
    'application': True,
    'auto_install': False,
}
