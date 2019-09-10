# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.api import Environment, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    # ref_attr  = website_sale.product_attributes has attribute customize_show = False
    # ref_table = website_sale_comparison.product_attributes_body has attribute customize_show = True
    # ref_attr  inherit_id = website.product
    # ref_table inherit_id = website.product but ref_table depends on tags added with ref_attr
    # Multi themes are created only for views with attribute customize_show = True it causes error
    # due to ref_attr was not applied for website specified website.product and ref_table do not see xpath paths
    ref_attr = 'website_sale.product_attributes'
    ref_table = 'website_sale_comparison.product_attributes_body'
    env['ir.ui.view'].search([('key', '=', ref_table)]).write({
        'inherit_id': env.ref(ref_attr).id,
    })
