# -*- coding: utf-8 -*-

{
    "name": "Agend Medic Laboratory",
    "description": "Laboratory Exams",
    "author": "Ing. Yadier A. De Quesada",
    "depends": [
        "base",
        "contacts",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        # data info
        "data/lab_sequence.xml",
        "data/data_lab.xml",
        "data/data_ir_attachment.xml",
        # views
        "views/order_exams_views.xml",
        "views/partner_views.xml",
        "views/setting_exams.xml",
        "views/account_move.xml",
        "views/company_views.xml",
        # reports
        "report/report_menu_items.xml",
        "report/report_orders_exams.xml",
        # whatsapp wizard
        'wizard/wizard.xml',
    ],
    "application": True,
}
