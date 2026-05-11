{
    'name': 'Components Request',
    'version': '19.0.1.0.0',
    'installable': True,
    'application': True,
    'depends': [
        'purchase',
        'stock',
        'hr',
        'product',
    ],
    'data': [
        'security/requisition_groups.xml',
        'security/ir_user_rules.xml',
        'security/ir.model.access.csv',
        'wizard/create_po_views.xml',
        'views/requisition_component_views.xml',
        'views/requisition_component_menus.xml',
    ],
}
