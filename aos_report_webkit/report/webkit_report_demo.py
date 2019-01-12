from odoo.addons.aos_report_webkit.webkit_report import webkit_report_extender
from odoo import SUPERUSER_ID

@webkit_report_extender("aos_report_webkit.webkit_demo_report")
def extend_demo(pool, cr, uid, localcontext, context):
    admin = pool.get("res.users").browse(cr, uid, SUPERUSER_ID, context)
    localcontext.update({
        "admin_name": admin.name,
    })
