# -*- coding: utf-8 -*-
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.http import request
from odoo.addons.pos_esign_request.controllers.main import PosESignExtension


class PosESignEvent(PosESignExtension):

    def update_partner_sign(self, vals):
        res = super(PosESignEvent, self).update_partner_sign(vals)

        attendee_id = vals.get('attendee_id', False)
        if res and attendee_id:
            attendee_id = request.env['event.registration'].browse(attendee_id)
            attendee_id.write({
                'sign_attachment_id': res['attachment_id'][0],
            })
            attendee_id.embed_sign_to_pdf()

            res['attendee_id'] = attendee_id.id
            res['signed_terms'] = attendee_id.signed_terms

        print '========================='
        print attendee_id
        print '========================='

        return res
