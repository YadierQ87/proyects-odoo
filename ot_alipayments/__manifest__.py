# -*- coding: utf-8 -*-

{
    "name": "AliCuotas",
    "description": "AliQuotas payment system for condominiums",
    "author": "Open-Tech / Solprob Systems",
    "depends": [
        "base",
        "account",
        "product",
        "sale_management",
        "om_account_followup",
    ],
    "data": [
        "data/data_ot.xml",
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "wizard/wizard.xml",
        "views/partner_view.xml",
        "views/account_move.xml",
        "views/property_view.xml",
        "views/ir_ui_menu.xml",
        "report/report_consumption.xml",
        "report/report_invoice.xml",
        "report/report_menu_items.xml",
    ],
    "application": True,
}
