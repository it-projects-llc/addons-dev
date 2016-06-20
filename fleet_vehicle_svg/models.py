# -*- coding: utf-8 -*-
import base64
from lxml import etree
import os
from wand.image import Image
from openerp import models, fields, api


class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    part_ids = fields.One2many('fleet.vehicle.part', 'vehicle_id', 'Parts')
    png_file = fields.Text('PNG', compute='_compute_png', store=False)

    @api.multi
    def _compute_png(self):
        for vehicle in self:
            f = open('/'.join([os.path.dirname(os.path.realpath(__file__)),
                               'static/src/img/car-cutout.svg']), 'r')
            svg_file = f.read()
            dom = etree.fromstring(svg_file)
            for part in vehicle.part_ids:
                if part.state == 'broken':
                    for el in dom.xpath('//*[@id="%s"]' % part.part_id):
                        el.attrib['fill'] = 'red'
            f.close()
            with Image(blob=etree.tostring(dom), format='svg') as img:
                vehicle.png_file = base64.b64encode(img.make_blob('png'))


class fleet_vehicle_part(models.Model):
    _name = 'fleet.vehicle.part'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    part_id = fields.Char('Part ID')
    name = fields.Char('Name')
    state = fields.Selection([('operative', 'Operative'),
                              ('broken', 'Broken')], 
                             string='State',
                             default='operative')
