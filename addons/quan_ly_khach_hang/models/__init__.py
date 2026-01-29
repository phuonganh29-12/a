# -*- coding: utf-8 -*-

# Import các model cơ bản trước (không phụ thuộc vào model khác)
from . import loai_khach_hang
from . import nguon_khach_hang
from . import tinh_trang_khach_hang
from . import crm_stage

# Import customer sau khi các model phụ thuộc đã được import
from . import customer

# Import các model khác
from . import crm_lead
from . import crm_interact
from . import sale_order
from . import note
from . import feedback
from . import project_task
from . import marketing_campaign
from . import email_marketing_campaign
from . import email_marketing_template
from . import customer_care