# -*- coding: utf-8 -*-
{
    'name': "combustible_etecsa",
    'summary': """
       Módulo de Combustible""",
    'description': """Módulo para gestionar el Combustible""",
    'author': "Ing. Jeanye Claro Cartaya  , Ing. Yadier De Quesada",
    'website': "https://www.odoo.com/page/prueba",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['base','fleet','fleet_etecsa','hr','mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/demanda_views.xml',
        'views/menu_items.xml',
        'report/report_anexo_carga_combustible.xml',
        'report/report_menu_items.xml',
    ],
    'demo': [
        'demo/demo.xml'],
    'installable': True,
    'application': True,
}
