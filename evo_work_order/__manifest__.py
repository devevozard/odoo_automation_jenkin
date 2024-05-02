{
    'name': 'Evo Work Order',
    'summary':'Work Order',
    'version': '15.0',
    'description':"""Work Order """, 
    'author': 'Evozard',
    'website': 'http://evozard.com/',
    'category': 'HR',
    'depends': ['sale','project','base','hr','stock','contacts','sale_management','calendar'],
    'data': [
            "security/ir.model.access.csv",
            "views/work_order_view.xml",
            "views/activity_type.xml",
            "views/warehouse_view.xml",
            "views/avalibility_calendar_view.xml",
            "views/workorder_report_views.xml",
            "views/responsible_availability_views.xml",
            "wizards/workorder_wizard_views.xml",
            "wizards/workorder_report_wizard_view.xml",
            "wizards/activity_onchange_wizard_views.xml"

        ],
    'assets': {
           'web.assets_backend': [
               'evo_work_order/static/src/js/kanban_button.js',
           ],
           'web.assets_qweb': [
               'evo_work_order/static/src/xml/kanban_button.xml',
           ],
        },
    'installable': True,
    'license':'OPL-1',
    'images': [],
    'auto_install': False,
    'application': True,
}
            
       
            
