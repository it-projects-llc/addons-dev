from odoo.addons.aos_report_webkit.webkit_report import webkit_report_extender
from odoo import SUPERUSER_ID, api
from odoo.http import request


@webkit_report_extender("aos_report_webkit.webkit_demo_report")
def extend_demo(localcontext):
    env = api.Environment(request.cr, SUPERUSER_ID, request.context)
    localcontext.update({
        "admin_name": env.user.name,
    })
