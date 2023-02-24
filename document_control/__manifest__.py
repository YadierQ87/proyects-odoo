# -*- coding: utf-8 -*-
{
    'name': "Document Control",

    'summary': """This module is used to limit the sale if the documents are expired""",

    'description': """
        This module is used to limit the sale if the documents are expired
    """,

    'author': "YadierQ87-Solprob Digital",
    'website': "-",
    'category': 'Documents',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale_management',
        'contacts',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/document_views.xml',
        'views/res_partner_views.xml',
        # for data sample and sequences
        'data/data.xml',
        'data/sequences.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license":'OPL-1',
}
