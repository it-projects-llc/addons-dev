# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) 2010 Camptocamp SA (http://www.camptocamp.com)
# Author : Vincent Renaville

from odoo.tools.translate import _
from odoo import fields, models, api


class ReportWebkitActions(models.TransientModel):
    _name = "report.webkit.actions"
    _description = "Webkit Actions"

    print_button = fields.Boolean("Add print button", default=True, help="Check this to add a Print action for this "
                                                                         "Report in the sidebar of the corresponding "
                                                                         "document types")
    open_action = fields.Boolean("Open added action", default=False, help="Check this to view the newly added internal "
                                                                          "print action after creating it "
                                                                          "(technical view) ")

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
        Changes the view dynamically

        :param view_id: id of the view or None
        :param view_type: type of the view to return if view_id is None ('form', 'tree', ...)
        :param toolbar: true to include contextual actions
        :param submenu: deprecated
        :return: New arch of view.
        """
        res = super(ReportWebkitActions, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                               toolbar=toolbar, submenu=submenu)
        record_id = self._context.get('active_id') or False
        active_model = self._context.get('active_model')

        if not record_id or (active_model and active_model != 'ir.actions.report.xml'):
            return res

        report = self.env['ir.actions.report'].browse(record_id)
        default_value = self.env['ir.default'].search([('value', '=', report.type + ','
                                                        + str(self._context.get('active_id')))])
        if default_value is not None:
            res['arch'] = '''
            <form string="Add Print Buttons"> 
                <label string="Report Action already exist for this report."/>
            </form>
            '''
        return res

    def do_action(self):
        """ This Function Open added Action.
         @return: Dictionary of ir.values form.
        """
        report_obj = self.env['ir.actions.report']

        # TODO: fix and check

        for current in self:
            report = report_obj.browse(self._context.get('active_id'))
            if current.print_button:
                res = self.env['ir.default'].set(report.model, report.report_name, report.type + ','
                                                 + str(self._context.get('active_id', False)))
            else:
                res = self.env['ir.default'].set(
                                    'action', 
                                    'client_print_multi', 
                                    report.report_name, 
                                    [report.model, 0],
                                    report.type + ',' + str(self._context.get('active_id', False)))
            if res[0]:
                if not current.open_action:
                    return {'type': 'ir.actions.act_window_close'}

                return {
                    'name': _('Client Actions Connections'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_id': res[0],
                    'res_model': 'ir.default',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                }                   
