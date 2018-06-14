# -*- coding: utf-8 -*-
# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class WebsiteSaleCalendar(WebsiteSale):

    @http.route()
    def cart_update(self, product_id, add_qty=1, set_qty=0, checkin=False, checkout=False, **kw):
        request.website.sale_get_order(force_create=1)._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            checkin=checkin,
            checkout=checkout,
            attributes=self._filter_attributes(**kw),
        )
        return request.redirect("/shop/cart")
