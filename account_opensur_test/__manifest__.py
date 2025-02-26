{
    "name": "Account Opensur Test",
    "version": "1.0",
    "summary": "Opensur Test Module",
    "sequence": 10,
    "description": """
        This module allows you to add some behaviors to account module.
    """,
    "category": "Accounting/Accounting",
    "author": "ING. YADIER ABEL DE QUESADA RICARDO",
    "depends": ["base", "account"],
    "auto_install": False,
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/account_move_view.xml",
        "views/res_config_setting.xml",
        "views/res_partner_views.xml",
    ],
    "license": "LGPL-3",
}
