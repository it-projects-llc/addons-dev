from odoo import api, fields, models, _
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta






class FsmSaleOrder(models.Model):
    _inherit = 'sale.order'

    project_ref = fields.Many2one('project.project', string='Project Reference',
                                  default=lambda self: self.env['project.project'].search([],limit = 1)
                                    )
    date_deadline = fields.Datetime(string='Deadline', default=lambda *a: (datetime.today() + relativedelta(days=6)).strftime('%Y-%m-%d'))

    job_name = fields.Char(string='Name', related='name', strore= True, Help='Copy of sale order sequence')

    sales_count =fields.Integer(string="Sales Jobs", compute="compute_job_count")

    @api.multi
    def compute_job_count(self):
        task_env = self.env['project.task']
        count = task_env.search([('name', '=', self.name)])
        self.sales_count = len(count)


    @api.multi
    def convert_to_job(self):
        city_obj = self.env['city.city']
        city_obj1 = city_obj.search([('name', '=', self.partner_invoice_id.city)])
        if city_obj1:
            city_req_id = city_obj1.id
        else:
            city_id_new = city_obj.create({'name': self.partner_invoice_id.city})
            city_req_id = city_id_new.id
        pro_env = self.env['project.task'].create({
                                                    'sale_ord': self.job_name,
                                                    'name' : self.job_name,
                                                    'partner_id':self.partner_id.id,
                                                    'project_id': self.project_ref.id,
                                                    'street': self.partner_invoice_id.street,
                                                     'street2': self.partner_invoice_id.street2,
                                                     'city_id': city_req_id,
                                                     'state_id': self.partner_invoice_id.state_id.id,
                                                     'zip': self.partner_invoice_id.zip,
                                                    # 'date_deadline' : self.date_deadline
                                                             })

        for line in self.order_line:
            job_dict = {    'job_id' : pro_env.id,
                            'product_id':line.product_id.id,
                            'name':line.name,
                            'product_uom_qty': line.product_uom_qty,
                            'price_unit': line.price_unit,
                            'product_uom': line.product_uom.id,
            }

            pro_env.write({ 'order_line_ids' : [(0,0,(job_dict))]

                            })

        view = self.env.ref('project.view_task_form2')

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'current',
            'res_id': pro_env.id,
        }

    @api.multi
    def action_create_fsm(self):
        return {

            'name': _('Sale Jobs'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'kanban,tree,form,calendar,pivot,graph',
            'target': 'current',
            'domain': [('sale_ord', '=', self.job_name),('copy_check','=', False)]
        }
