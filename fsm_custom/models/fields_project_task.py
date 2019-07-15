from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError,Warning
import base64
import logging
logger = logging.getLogger(__name__)


class FieldsProjectTask(models.Model):
    _inherit = 'project.task'

    # @api.depends('image_o2m')
    # def _compute_color_change(self):
    #     for line in self.image_o2m:
    #         if line.id:
    #             self.custom_install_color=True
    #         else:
    #             self.custom_install_color = False




    copy_check = fields.Boolean('Copy Check', help='True once Additional Site Visit menu is clicked')
    stage_copy_id = fields.Many2one('project.task.type', string='Stage' ,related='stage_id')
    # job_seq = fields.Char('Job Sequence')
    parent_name = fields.Many2one('project.task','Parent Name')
    dob = fields.Date('Date of birth')
    mobile_no = fields.Char('Mobile Phone')
    product_location = fields.Selection([('vendor_wh', 'Vendor WH'), ('cg_wh', 'CG WH'),('customer_site', 'Customer Site'),
                                         ('multiple_location', 'Multiple locations')], string='Product Location')
    plan_hours = fields.Float(string='Planned Hours')
    fast_view = fields.Many2many('job.list', string='Fast View')
    site_cross_street = fields.Text('Site Cross Street')
    po_no = fields.Integer('PO#')
    product_availability_date = fields.Date('Product Availability Date')
    rma_rmt_no = fields.Integer('RMA/RMT#')
    property_type = fields.Selection(
        [('single family', 'Single Family'), ('Townhome', 'Townhome'), ('Duplex', 'Duplex'),
         ('Hi-rise', 'Hi-rise'), ('Other', 'Other')], string='Type of Property')
    sale_ord = fields.Char('Sale Order', help='Copy of related sale order No.')
    give_rating = fields.Selection([('1', 'No Rating'),('2', 'Unhappy'),('3', 'Good'),('4', 'Average'),('5', 'Satisfied'),('6', 'Happy')], string="Rating")

    give_feedback = fields.Text('Feedback', help="Reason of the rating")
    give_signature = fields.Char('Signature')

    image_o2m = fields.One2many('image.line', 'image_m2o', string='Image Line')
    # image_set = fields.Binary(string='Image')

    child_count = fields.Integer(string="Site Visit", compute='compute_job_count')

    modify_line_ids = fields.One2many(
        comodel_name='modify.line',
        inverse_name='modify_id',
        string='Modify Line',
        help='create the product name,price and quantity')

    # child_ids = fields.One2many('project.task.display', 'child_project', string='Child ID' )

    # @api.multi
    # def compute_job_count(self):

    driveway_type = fields.Selection([('Concrete', 'Concrete'), ('Gravel/Rock', 'Gravel/Rock'), ('Other', 'Other')], string='Driveway Type/Condition')
    high_rise_acc = fields.Selection([('Elevator', 'Elevator'), ('Loading', 'Loading'), ('Dock', 'Dock'), ('steps', 'Steps')], string='High-rise Access')
    type_of_flooring = fields.Selection([('Tile', 'Tile'), ('Wood', 'Wood'), ('Concrete', 'Concrete')], string='Type of Flooring')
    number_of_steps = fields.Integer('Number of steps')
    number_of_landing = fields.Integer('Number of landings')
    cabinets_installed = fields.Boolean('Cabinet Installed')
    counter_tops_installed = fields.Boolean('Counter-tops Installed')
    back_splash_installed = fields.Boolean('Backsplash Installed')
    gas_installed = fields.Boolean('Gas Installed')
    electrical_complete = fields.Boolean('Electrical Complete')
    plumbing_complete = fields.Boolean('Plumbing Complete')
    fix_repairs = fields.Text('Fix/Repair Install Others')

    dishwasher = fields.Boolean('Dishwasher')
    appliance_secure_1 = fields.Boolean('Appliance Secured', related='dishwasher')
    supply_line_connected_1 = fields.Boolean('Supply Line Connected(HOT)', related='dishwasher',)
    checked_function_1 = fields.Boolean('Checked Function', related='dishwasher', store=True)
    operation_explained_1 = fields.Boolean('Operations Explained', related='dishwasher', store=True)
    drain_connected_1 = fields.Boolean('Drain Connected', related='dishwasher', store=True)
    tci = fields.Boolean('Toe Click Installed', related='dishwasher', store=True)
    packing_material_removed_1 = fields.Boolean('Packing Material Removed', related='dishwasher', store=True)

    washer = fields.Boolean('Washer')
    appliance_secure_2 = fields.Boolean('Appliance Secured', related='washer', store=True)
    supply_line_connected_2 = fields.Boolean('Supply Line Connected/Duck Connected', related='washer', store=True)
    checked_function_2 = fields.Boolean('Checked Function', related='washer', store=True)
    operation_explained_2 = fields.Boolean('Operations Explained',  related='washer', store=True)
    drain_connected_2 = fields.Boolean('Drain Connected',  related='washer', store=True)
    shipping_struts_removed_2 = fields.Boolean('Shipping Struts Removed',  related='washer', store=True)
    packing_material_removed_2 = fields.Boolean('Packing Material Removed',  related='washer', store=True)

    dryer = fields.Boolean('Dryer')
    appliance_secure_3 = fields.Boolean('Appliance Secured', related='dryer', store=True)
    supply_line_connected_3 = fields.Boolean('Supply Line Connected/Duck Connected', related='dryer', store=True )
    checked_function_3 =  fields.Boolean('Checked Function', related='dryer', store=True)
    operation_explained_3= fields.Boolean('Operations Explained', related='dryer', store=True)
    drain_connected_3 = fields.Boolean('Drain Connected',related='dryer', store=True)
    shipping_struts_removed_3 = fields.Boolean('Shipping Struts Removed',related='dryer', store=True)
    packing_material_removed_3 = fields.Boolean('Packing Material Removed', related='dryer', store=True)

    cooktop = fields.Boolean('Cooktop')
    appliance_secure_4 = fields.Boolean('Appliance Secured', related='cooktop', store=True)
    electrical_connected_4 = fields.Boolean('Electrical Connected', related='cooktop', store=True )
    gas_connected_4 = fields.Boolean('Gas Connected', related='cooktop', store=True)
    operation_explained_4 = fields.Boolean('Operations Explained', related='cooktop', store=True)
    all_bnr_ignite_4 = fields.Boolean('All Burners Ignite', related='cooktop', store=True)
    packing_material_removed_4 = fields.Boolean('Packing Material Removed', related='cooktop', store=True)
    grates_knob_4 =  fields.Boolean('Grates & Knobs Present', related='cooktop', store=True)

    range = fields.Boolean('Range')
    appliance_secure_5 = fields.Boolean('Appliance Secured',related='range', store=True )
    electrical_connected_5 = fields.Boolean('Electrical Connected', related='range', store=True)
    gas_connected_5 = fields.Boolean('Gas Connected', related='range', store=True)
    operation_explained_5 = fields.Boolean('Operations Explained', related='range', store=True)
    all_bnr_ignite_5 = fields.Boolean('All Burners Ignite', related='range', store=True)
    packing_material_removed_5 = fields.Boolean('Packing Material Removed', related='range', store=True)
    grates_knob_5 = fields.Boolean('Grates & Knobs Present', related='range', store=True)

    downdraft = fields.Boolean('Downdraft')
    appliance_secure_6 = fields.Boolean('Appliance Secured', related='downdraft', store=True )
    raise_lowers_6 = fields.Boolean('Raise/Lowers', related='downdraft', store=True)
    remote_mounted_6 = fields.Boolean('Remote Mounted', related='downdraft', store=True)
    filters_installed_6 = fields.Boolean('Filters Installed',related='downdraft', store=True)
    electrical_connected_6 = fields.Boolean('Electrical Connected', related='downdraft', store=True)
    operation_explained_6 = fields.Boolean('Operations Explained', related='downdraft', store=True)
    packing_material_removed_6 = fields.Boolean('Packing Material Removed', related='downdraft', store=True)

    ice_machine = fields.Boolean('Ice Machine')
    appliance_secure_7 = fields.Boolean('Appliance Secured', related='ice_machine', store=True)
    electrical_connected_7 = fields.Boolean('Electrical Connected', related='ice_machine', store=True)
    supply_line_connected_7 = fields.Boolean('Supply Line Connected',related='ice_machine', store=True )
    drain_line_connected_7 = fields.Boolean('Drain Line Connected', related='ice_machine', store=True)
    functions_properly_7 = fields.Boolean('Functions  Properly', related='ice_machine', store=True)
    panel_installed_7 = fields.Boolean('Panel Installed', related='ice_machine', store=True)
    pump_working_7 = fields.Boolean('Pump Working', related='ice_machine', store=True)

    refrigerator =  fields.Boolean('Refrigerator')
    appliance_secure_8 = fields.Boolean('Appliance Secured', related='refrigerator', store=True)
    anti_tip_mounted_8 = fields.Boolean('Anti Tip Mounted', related='refrigerator', store=True)
    electrical_connected_8 = fields.Boolean('Electrical Connected', related='refrigerator', store=True)
    water_line_connected_8 = fields.Boolean('Water Line Connected', related='refrigerator', store=True)
    operation_explained_8 = fields.Boolean('Operations Explained', related='refrigerator', store=True)
    water_purged_8 = fields.Boolean('Water Purged', related='refrigerator', store=True)
    ice_maker_on_8 = fields.Boolean('Ice Maker On', related='refrigerator', store=True)

    freezer = fields.Boolean('Freezer')
    appliance_secure_9 = fields.Boolean('Appliance Secured', related='freezer', store=True)
    anti_tip_mounted_9 = fields.Boolean('Anti Tip Mounted',related='freezer', store=True )
    electrical_connected_9 = fields.Boolean('Electrical Connected',related='freezer', store=True)
    water_line_connected_9 = fields.Boolean('Water Line Connected', related='freezer', store=True)
    operation_explained_9 = fields.Boolean('Operations Explained', related='freezer', store=True)
    water_purged_9 = fields.Boolean('Water Purged', related='freezer', store=True)
    ice_maker_on_9 = fields.Boolean('Ice Maker On', related='freezer', store=True)

    hood = fields.Boolean('Hood')
    appliance_secure_10 = fields.Boolean('Appliance Secured', related='hood', store=True)
    electrical_connected_10 = fields.Boolean('Electrical Connected', related='hood', store=True)
    duct_connected_sealed_10 = fields.Boolean('Duct Connected & Sealed', related='hood', store=True)
    functions_properly_10 = fields.Boolean('Functions  Properly', related='hood', store=True)
    packing_material_removed_10 = fields.Boolean('Packing Material Removed', related='hood', store=True)
    grates_installed_10 = fields.Boolean('Grates Installed', related='hood', store=True)
    flow_test_10 = fields.Boolean('Flow Test', related='hood', store=True)

    microwave_oven = fields.Boolean('Microwave Oven')
    trim_kit_open_11 = fields.Boolean('Trim Kit Installed/Open Closes', related='microwave_oven', store=True)
    appliance_secure_11 = fields.Boolean('Appliance Secured',related='microwave_oven', store=True)
    electrical_connected_11 = fields.Boolean('Electrical Connected', related='microwave_oven', store=True)
    trim_kit_11 = fields.Boolean('Trim Kit Installed', related='microwave_oven', store=True)
    packing_material_removed_11 = fields.Boolean('Packing Material Removed', related='microwave_oven', store=True)
    operation_explained_11 = fields.Boolean('Operations Explained', related='microwave_oven', store=True)
    open_closes_11 = fields.Boolean('Opens/Closes', related='microwave_oven', store=True)
    functions_properly_11 = fields.Boolean('Functions  Properly', related='microwave_oven', store=True)

    other = fields.Boolean('Other')
    appliance_secure_12 = fields.Boolean('Appliance Secured', related='other', store=True)
    power_water_12 = fields.Boolean('Power/ Water', related='other', store=True)
    trim_kit_12 = fields.Boolean('Trim Kit Installed', related='other', store=True)
    operation_explained_12 = fields.Boolean('Operations Explained', related='other', store=True)
    packing_material_removed_12 = fields.Boolean('Packing Material Removed', related='other', store=True)

    description = fields.Text('Description')

    signature_damage = fields.Binary('Signature')
    many_image = fields.One2many('image.damage','damage_id',string='Image', attachment=True)
    text_damage = fields.Text('Description')

    # cust_state = fields.Selection(
    #     [('normal', 'In Progress'), ('blocked', 'Blocked'), ('done', 'Ready for next stage')],
    #     string='Kanban State')

    custom_install_color=fields.Boolean("Checked")
    custom_damage_color=fields.Boolean("Checked")
    invoice_count = fields.Integer(string='Invoice', compute='_compute_invoice_create')

    @api.depends('invoice_check')
    def _compute_invoice_create(self):
        for order in self:
            if order.invoice_check:
                invoice_id = self.env['account.invoice'].search([('job_id', '=', order.job_sequence)])
                order.invoice_count = len(invoice_id)

    @api.multi
    def action_view_invoices(self):
        invoices = self.env['account.invoice'].search([('job_id', '=', self.job_sequence)])
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    # @api.multi
    # def write(self, vals):
    #     res = super(FieldsProjectTask, self).write(vals)
    #     if self.kanban_state=='blocked':
    #         raise UserError(_("You are not allowed to change this, because it is blocked"))
    #     else:
    #         return res

    # @api.multi
    # def color_change(self):
    #     if self.custom_install_color:
    #         return {
    #             'type': 'ir.actions.client',
    #             'tag': 'reload',
    #         }






    @api.onchange('many_image')
    def onchange_damage_color(self):
        if self.many_image:
            for line in self.many_image:
                if line:
                    self.custom_damage_color = True
                    break
        else:
            self.custom_damage_color = False

    @api.onchange('image_o2m')
    def onchange_install_color(self):
        if self.image_o2m:
            for line in self.image_o2m:
                if line:
                    self.custom_install_color=True
                    break
        else:
            self.custom_install_color=False

    @api.multi
    def write(self, vals):
        if 'kanban_state' not in vals:
            vals['kanban_state'] = self.kanban_state

        result = super(FieldsProjectTask, self).write(vals)

        return result


    @api.multi
    def compute_job_count(self):
        for id in self:
            id.child_count =0
            task_env = self.env['project.task']
            count = task_env.search([('parent_name','=', id.id)])
            for jobs in count:
                id.child_count += 1

    @api.multi
    def fsm_button(self):
        return {

            'name': _('Site Visit'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'kanban,tree,form,calendar,pivot,graph',
            'target': 'current',
            'domain': [('parent_name','=', self.id)]
        }

    @api.multi
    def sale_button(self):
        ord_obj = self.env['sale.order'].search([('name', '=', self.sale_ord)])

        view = self.env.ref('sale.view_order_form')


        return {
            'name': _('Sale Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'current',
            'domain': [('name', '=', self.sale_ord)],
            'res_id': ord_obj.id,

        }



    @api.multi
    def copy_custom(self,  default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = _("%s (site visit)") % self.name
        if 'remaining_hours' not in default:
            default['remaining_hours'] = self.planned_hours
        if not default.get('copy_check'):
            default['copy_check'] = True
        if not default.get('parent_name'):
            default['parent_name'] = self.id
        return super(FieldsProjectTask, self).copy(default)


    @api.multi
    def rating_feedback(self):
        rating = ''
        if self.give_rating == '1':
            rating = 'No Rating'
        elif self.give_rating == '2':
            rating = '*'
        elif self.give_rating == '3':
            rating = '**'
        elif self.give_rating == '4':
            rating = '***'
        elif self.give_rating == '5':
            rating = '****'
        elif self.give_rating == '6':
            rating = '*****'
        return rating


    @api.multi
    def send_install_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        installation_template_id=False
        logger.info('<-----------------------------------------------installation_template_id---------------------> %s',
                    installation_template_id)
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            logger.info(
                '<-----------------------------------------------compose_form_id---------------------> %s',
                compose_form_id)
            # template_id = self.env['mail.template'].browse(compose_form_id)
            # template_id.write({'template_id':24})
            installation_template_id = self.env.ref('fsm_custom.email_template_installation_details_email').id
            logger.info(
                '<-----------------------------------------------installation_template_id---------------------> %s',
                installation_template_id)
            # template_id.write({'template_id': installation_template_id})

        except ValueError:
            compose_form_id = False
        logger.info(
            '<-----------------------------------------------pdf1---------------------> %s',
            )
        pdf, _ = self.env.ref('fsm_custom.action_report_custom_install').sudo().render_qweb_pdf([self.id])
        #pdf = self.env['report'].sudo().get_pdf([self.id], 'fsm_custom.report_custom_template_install')
        logger.info(
            '<-----------------------------------------------pdf---------------------> %s',
            pdf)

        image_line_ids = self.env['image.line'].search([('image_m2o', '=', self.id)]).ids
        logger.info(
            '<-----------------------------------------------image_line_ids---------------------> %s',
            image_line_ids)
        attachment_ids = []
        attachment_ids.append(self.env['ir.attachment'].create({
            'name': self.name+'.pdf',
            'type': 'binary',
            'datas': base64.encodestring(pdf),
            'datas_fname':self.name+'.pdf',
            'res_model': 'project.task',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        }).id)
        logger.info(
            '<-----------------------------------------------attachment_ids---------------------> %s',
            attachment_ids)


        for rec in image_line_ids:
            attachment = self.env['ir.attachment'].search([('res_id', '=', rec), ('res_model', '=', 'image.line'),('res_field','=','image_set')])
            if attachment:
                attachment_ids.append(attachment.id)
        ctx = dict()
        ctx.update({
            'default_res_id': self.ids[0],
            'default_template_id': installation_template_id,
            'default_attachment_ids':attachment_ids,
        })
        logger.info(
            '<-----------------------------------------------ctx---------------------> %s',
            attachment_ids)




        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def send_damage_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            # template_id = self.env['mail.template'].browse(compose_form_id)
            demage_template_id=self.env.ref('fsm_custom.email_template_damages_details_email').id
        except ValueError:
            compose_form_id = False
        pdf = self.env.ref('fsm_custom.action_report_custom_damage').render_qweb_pdf([self.id])
        #pdf = self.env['report'].sudo().get_pdf([self.id], 'fsm_custom.report_custom_template_damage')

        image_line_ids = self.env['image.damage'].search([('damage_id', '=', self.id)]).ids
        attachment_ids = []
        attachment_ids.append(self.env['ir.attachment'].create({
            'name': self.name + '.pdf',
            'type': 'binary',
            'datas': base64.encodestring(pdf[0]),
            'datas_fname': self.name + '.pdf',
            'res_model': 'project.task',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        }).id)
        # if self.signature_damage_image:
        #     attachment_ids.append(self.env['ir.attachment'].create({
        #         'name': 'Customer Signature.pdf',
        #         'datas': self.signature_damage_image,
        #         'datas_fname': 'Customer Signature',
        #         'res_model': 'music_audiofile',
        #         'type': 'binary'
        #     }).id)

        for rec in image_line_ids:
            attachment = self.env['ir.attachment'].search(
                [('res_id', '=', rec), ('res_model', '=', 'image.damage'), ('res_field', '=', 'damage_image')])
            if attachment:
                attachment_ids.append(attachment.id)
        ctx = dict()
        ctx.update({
            'default_res_id': self.ids[0],
            'default_template_id':demage_template_id,
            'default_attachment_ids': attachment_ids,

        })

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def send_feedback_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            # template_id = self.env['mail.template'].browse(compose_form_id)
            feedback_template_id = self.env.ref('fsm_custom.email_template_feedback_email').id
        except ValueError:
            compose_form_id = False
        pdf, _ = self.env.ref('fsm_custom.action_report_custom_feedback').sudo().render_qweb_pdf([self.id])
        #pdf = self.env['report'].sudo().get_pdf([self.id], 'fsm_custom.report_custom_template_feedback')

        # image_line_ids = self.env['image.damage'].search([('damage_id', '=', self.id)]).ids
        attachment_ids = []
        attachment_ids.append(self.env['ir.attachment'].create({
            'name': self.name + '.pdf',
            'type': 'binary',
            'datas': base64.encodestring(pdf),
            'datas_fname': self.name + '.pdf',
            'res_model': 'project.task',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        }).id)

        ctx = dict()
        ctx.update({
            'default_res_id': self.ids[0],
            'default_template_id': feedback_template_id,
            'default_attachment_ids': attachment_ids,

        })

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def email_modify_lines(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            modify_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            modification_id = self.env.ref('fsm_custom.email_template_modification_lines').id
        except ValueError:
            modify_form_id = False
        # pdf1 = self.env['report']
        # pdf  = pdf1.sudo().get_pdf([self.id], 'fsm_custom.report_custom_modification')
        pdf, _ = self.env.ref('fsm_custom.action_report_modification_lines').sudo().render_qweb_pdf([self.id])
        #pdf = self.env['report'].sudo().get_pdf([self.id], 'fsm_custom.report_custom_modification')

        attachment_ids = []
        attachment_ids.append(self.env['ir.attachment'].create({
            'name': self.name + '.pdf',
            'type': 'binary',
            'datas': base64.encodestring(pdf),
            'datas_fname': self.name + '.pdf',
            'res_model': 'project.task',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        }).id)
        ctx = dict()
        ctx.update({
            'default_res_id': self.ids[0],
            'default_template_id': modification_id,
            'default_attachment_ids': attachment_ids,

        })

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(modify_form_id, 'form')],
            'view_id': modify_form_id,
            'target': 'new',
            'context': ctx,
        }



#####################################################################################
class AdditionalSiteVisit(models.Model):
    _name = 'additional.site.wizard'

    @api.multi
    def confirm_copy(self):
        default = self._context.get("active_ids")
        obj_id  = self.env['project.task']
        def_obj = obj_id.browse(default)
        rec_id = def_obj.copy_custom()
        # old_id=self.env['project.task'].browse(self._context.get('active_id'))
        # for line in old_id.order_line_ids:
        #     if not line.check_box:
        #         vals={'invoice_id':rec_id.id,
        #                 'product_id':line.product_id.id,
        #               'product_uom_qty':line.product_uom_qty,
        #               'price_unit':line.price_unit,
        #               'name':line.name,
        #               'product_uom':line.product_uom}
        #         self.env['job.line'].create(vals)

        return {
            'name': _('Sale Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_type': 'form',
            'view_mode': 'form',
            # 'views': [(view.id, 'form')],
            # 'view_id': view.id,
            'target': 'current',
            # 'domain': [('name', '=', self.sale_ord)],
            'res_id': rec_id.id,

        }




#########################################################################################################################
class ImageDisplayLine(models.Model):
    _name = 'image.line'

    image_m2o = fields.Many2one('project.task')
    # name = fields.Char('Name')
    # age = fields.Integer('Age')
    db_datas = fields.Binary('Database Data')
    store_fname = fields.Char('Stored Filename')
    # image_set = fields.Many2many(comodel_name="ir.attachment", relation="std_doc_attach_rel", column1='stud_id',
    #                                  column2='attach_id', string="Student Docs")

    image_set = fields.Binary(string='Image',attachment=True)




class ImageDisplayDameg(models.Model):
    _name = 'image.damage'

    damage_id = fields.Many2one('project.task')
    store_fname = fields.Char('Stored Filename')

    damage_image = fields.Binary('Database Data', attachment=True)

class ModifyLine(models.Model):
    _name = 'modify.line'
    _inherit = 'sale.order.line'

    modify_id = fields.Many2one(
        comodel_name='project.task',
        string='Job Modify',
        help='This field is a related to jobs view in create a jobs')

    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Order Reference',
        required=False,
        help='This field is a sale order reference field')

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            self.price_unit = line.product_id.list_price
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })


class JobList(models.Model):
    _name = 'job.list'
    _rec_name = 'job_name'

    job_name = fields.Char('Job Name')


class FieldsCustomer(models.Model):
    _inherit = 'res.partner'

    property_contact = fields.Many2one('res.partner', string='Property Contact')


