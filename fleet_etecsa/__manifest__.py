# -*- coding: utf-8 -*-
{
    'name': "fleet_etecsa",

    'summary': """
        Modificaciones a la flota de vehiculos para ETECSA""",

    'description': """
        Modificaciones a la flota de vehiculos para ETECSA
    """,

    'author': "Ing. Yadier A. De Quesada",
    'website': "http://www.etecsa.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','fleet'],

    # always loaded
    'data': [
        #security
        'security/fleet_etecsa_security.xml',
        'security/ir.model.access.csv',
        'views/views_overrides.xml',
        'views/views_forms.xml',
        'views/views_list.xml',
        'views/views_kanban.xml',
        'views/menu_items.xml',
        #reports qweb-pdf
        'report/report_menu_items.xml',
        'report/report_anexo_unico.xml',
        'report/report_anexo_liquidacion.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'installable': True,
    'application': True,
}