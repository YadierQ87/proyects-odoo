# -*- coding: utf-8 -*-
{
    'name': "serclinic_general",
    'summary': """
        Servicios Clinicos Especializados""",

    'description': """
        Flujo de Atencion a Pacientes, Modulo general de pacientes
    """,

    'author': "Ing. Yadier SolProb Apps",
    'website': "http://www.solprob.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hospital',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','contacts','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/views_contacts.xml',
        'views/views_equipment.xml',
        'views/views_local_equipment.xml',
        'views/views_study_type.xml',
        'views/menu_items.xml',
    ],
    'application': True,
	'installable': True,
    'auto_install': False,
}