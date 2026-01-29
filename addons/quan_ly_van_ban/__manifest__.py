# -*- coding: utf-8 -*-
{
    'name': "Quản Lý Văn Bản",

    'summary': """
        Quản lý văn bản đến, văn bản đi và lưu trữ hồ sơ""",

    'description': """
        Module quản lý văn bản bao gồm:
        - Quản lý văn bản đi (soạn thảo, phê duyệt, ký, gửi)
        - Quản lý văn bản đến (tiếp nhận, phân công, xử lý)
        - Phân loại văn bản theo loại
        - Đính kèm file PDF, Word, Excel...
        - Quy trình phê duyệt và ký số
        - Theo dõi hạn xử lý, quá hạn
        - Liên kết với nhân viên, khách hàng
        - Tracking lịch sử thay đổi
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'license': 'LGPL-3',
    'category': 'Productivity',
    'version': '1.0.0',

    # Module phụ thuộc
    'depends': ['base', 'mail', 'nhan_su', 'quan_ly_khach_hang'],

    # Dữ liệu luôn load
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/loai_van_ban_data.xml',
        'data/mau_van_ban_data.xml',
        'data/mau_hop_dong_lao_dong.xml',
        'views/loai_van_ban.xml',
        'views/van_ban_di.xml',
        'views/van_ban_den.xml',
        'views/mau_van_ban.xml',
        'views/luan_chuyen_van_ban.xml',
        'views/customer_inherit.xml',
        'wizard/wizard_tao_van_ban_tu_mau_view.xml',
        'wizard/wizard_luan_chuyen_van_ban_view.xml',
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
