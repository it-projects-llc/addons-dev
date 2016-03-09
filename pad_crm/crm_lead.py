# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp.osv import fields, osv

class lead(osv.osv):
    _name = "crm.lead"
    _inherit = ["crm.lead",'pad.common']
    _columns = {
        'description_pad': fields.char('Description PAD', pad_content_field='description')
    }
