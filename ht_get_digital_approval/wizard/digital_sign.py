from odoo import fields, models, api
from datetime import date
import logging


logger = logging.getLogger(__name__)


class PotentialDigitalSign(models.TransientModel):

    _name = 'digital.sign.popup'

    signature_image = fields.Binary("Signature")

    @api.model
    def apply_signature(self, cont, sign):
        self.signature = sign
        active_id = cont.get('active_id')
        active_model = str(cont.get('active_model'))
        logger.info('<-----------------------------------------------logger--------------------->')
        if active_id and active_model:
            active_record = self.env[active_model].browse(active_id)
            if active_model == 'purchase.order':
                active_record.signature = self.signature
                active_record.signature_added = True
                return active_record
            elif active_model == 'account.invoice':
                active_record.signature = self.signature
                active_record.signature_added = True
                return active_record
            elif active_model == 'sale.order':
                active_record.signature = self.signature
                active_record.signature_added = True
                return active_record
            elif active_model == 'project.task' and cont.get('search_default_customer_1'):
                active_record.write({'signature_cust_install_image':self.signature,'signature__cust_intall_added':True})
                self._cr.commit()
                logger.info('<-----------------------------------------------logger---------------------> %s',
                            str(self.signature))
                # active_record.signature__cust_intall_added = True
                return active_record
            elif active_model == 'project.task' and cont.get('search_default_signature_1'):
                active_record.signature_signature_install_image = self.signature
                active_record.signature__signature_intall_added = True
                return active_record
            elif active_model == 'project.task' and cont.get('search_default_dealer_1'):
                active_record.signature_dealer_install_image = self.signature
                active_record.signature__dealer_intall_added = True
                return active_record
            elif active_model == 'project.task' and cont.get('search_default_damage_1'):
                active_record.signature_damage_image = self.signature
                active_record.signature__damage_added = True
                return active_record
            elif active_model == 'project.task' and cont.get('search_default_feedback_1'):
                active_record.feedback_signature_image = self.signature
                active_record.feedback_signature_added = True
                return active_record
            elif active_model == 'project.task' and cont.get('search_default_modify_1'):
                active_record.signature_modify_install_image = self.signature
                active_record.signature_modify_added = True
                return active_record
            else:
                return False
        return True

