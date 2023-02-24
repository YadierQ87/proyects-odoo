# -*- coding: utf-8 -*-
{
    'name': "Demanda",

    'summary': """
       Gestionar la Demanda de vestuario de los trabajadores""",

    'description': """
       Modulo Demanda de vestuario de los trabajadores
    """,

    'author': "Ing. Jeanye , Ing. Yadier",
    'website': "http://www.vpor.com",
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [ 'base', 'mail', 'product' , 'hr'],
  
    'data': [
        'security/ir.model.access.csv',
        'views/demandas_views_list.xml',
        'views/demandas_views_form.xml',
        'views/demandas_views_pivot.xml',
        'views/demandas_global_form.xml',
        'views/menu_items.xml',
        #reports qweb-pdf
        'report/report_menu_items.xml',
        'report/report_planilla_captacion.xml',
        'report/report_plantilla_demanda.xml',
        'report/report_planilla_vestuario.xml',
        'report/report_total_vestuario.xml',
        #data
        'data/sequences.xml',
    ],

    'installable': True,
    'application': True,

}