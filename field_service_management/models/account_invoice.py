from odoo import fields,models,tools,api,_



class Account_Invoice(models.Model):
    _inherit='account.invoice'


    job_id=fields.Char('Job')