# -*- coding: utf-8 -*-
{
    'name': 'MC Product Restrictions',
    'version': '10.0.1.0.0',
    'summary': 'Restrict product and account visibility per user.',
    'author': 'Your Company',
    'license': 'LGPL-3',
    'website': 'https://example.com',
    'category': 'Product',
    'depends': ['base', 'product', 'account'],
    'data': [
        'security/res_groups.xml',
        'security/ir_rule_data.xml',
        'views/res_users_view.xml',
    ],
    'installable': True,
    'application': False,
}
