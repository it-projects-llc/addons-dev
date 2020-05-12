from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit= 'project.task'

    signature_damage_image = fields.Binary(string='Signature')
    signature__damage_added = fields.Boolean("Signature added?", default=False)
    # customer_signature=fields.Boolean("Customer")

    signature_cust_install_image = fields.Binary(string=' Customer Signature')
    signature__cust_intall_added = fields.Boolean("Signature added?", default=False)

    signature_signature_install_image = fields.Binary(string='Signature')
    signature__signature_intall_added = fields.Boolean("Signature added?", default=False)

    signature_dealer_install_image = fields.Binary(string='Dealer')
    signature__dealer_intall_added = fields.Boolean("Signature added?", default=False)

    feedback_signature_image = fields.Binary(string='Signature')
    feedback_signature_added = fields.Boolean("Signature added?", default=False)

    signature_modify_install_image = fields.Binary(string='Modification Signature')
    signature_modify_added = fields.Boolean("Signature added?",default=False)



    #
    # @api.multi
    # def _customer_signature_cus(self):
    #     view_id = self.env.ref('ht_get_digital_approval.digital_sign_popup_form')
    #     ctx = dict()
    #     ctx.update({
    #         'default_customer_signature': True,
    #     })
    #     return
    #     {
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'digital.sign.popup',
    #         'views': [(view_id, 'form')],
    #         'view_id': view_id,
    #         'target': 'new',
    #         'context': ctx,
    #     }
