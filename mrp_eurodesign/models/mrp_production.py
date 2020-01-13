# Copyright 2020 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    def button_mark_as_done_force(self):
        self.ensure_one()
        print('Finished move lines: ', len(self.finished_move_line_ids))
        update_qty = self.env['change.production.qty'].create({
            'mo_id': self.id,
            'product_qty': len(self.finished_move_line_ids)
        })
        update_qty.change_prod_qty()

        self.button_mark_done()
