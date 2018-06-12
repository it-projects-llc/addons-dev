# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _, tools
from odoo.addons.base.ir.ir_config_parameter import IrConfigParameter as IrConfigParameterOriginal, _default_parameters

_logger = logging.getLogger(__name__)
PROP_NAME = _('Default value for "%s"')

DATABASE_SECRET_KEY = 'database.secret'


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    value = fields.Text(company_dependent=True, website_dependent=True)

    @api.model
    def create(self, vals):
        res = super(IrConfigParameter, self).create(vals)
        # make value company independent
        domain = self.env['ir.property']._get_domain('value', self._name)
        domain += [('res_id', '=', '%s,%s' % (self._name, res.id))]
        prop = self.env['ir.property'].search(domain)
        prop.company_id = None
        prop.name = PROP_NAME % res.key
        res._update_db_value(vals.get('value'))
        return res

    @api.multi
    def _update_db_value(self, value):
        """Store value in db column. We can use it only directly,
        because ORM treat value as computed multi-company field"""
        self.ensure_one()
        self.env.cr.execute("UPDATE ir_config_parameter SET value=%s WHERE id = %s", (value, self.id, ))

    @api.model
    def reset_database_secret(self):
        value, groups = _default_parameters[DATABASE_SECRET_KEY]()
        self.set_param(DATABASE_SECRET_KEY, value, groups=groups)
        return value

    @api.model
    def get_param(self, key, default=False):
        company_id = self.env.context.get('company_id')
        if not company_id:
            website_id = self.env.context.get('website_id')
            if website_id:
                website = self.env['website'].browse(website_id)
                company_id = website.company_id and website.company_id.id

        if not company_id:
            company_id = self.env.user.company_id.id

        self_company = self.with_context(force_company=company_id)
        res = super(IrConfigParameter, self_company).get_param(key, default)
        if key == DATABASE_SECRET_KEY and not res:
            # If we have empty database.secret, we reset it automatically
            # otherwise admin cannot even login

            # TODO: we don't really need to reset database.secret, because in current version of the module column value is presented and up-to-date. Keep it until we are sure, that without this redefinition everything works after migration from previous versions fo the module.

            return self_company.reset_database_secret()

        return res

    @api.model
    @tools.ormcache_context('self._uid', 'key', keys=("force_company",))
    def _get_param(self, key):
        _logger.debug('_get_param(%s) context: %s', key, self.env.context)
        # call undecorated super method. See odoo/tools/cache.py::ormcache and http://decorator.readthedocs.io/en/stable/tests.documentation.html#getting-the-source-code
        return IrConfigParameterOriginal._get_param.__wrapped__(self, key)

    @api.multi
    def _create_default_value(self, value):
        """Set company-independent default value"""
        self.ensure_one()
        domain = [
            ('company_id', '=', False),
            ('res_id', '=', '%s,%s' % (self._name, self.id))
        ]

        existing = self.env['ir.property'].search(domain)
        if existing:
            # already exists
            return existing

        _logger.debug('Create default value for %s', self.key)
        return self.env['ir.property'].create({
            'fields_id': self.env.ref('base.field_ir_config_parameter_value').id,
            'res_id': '%s,%s' % (self._name, self.id),
            'name': PROP_NAME % self.key,
            'value': value,
            'type': 'text',
        })

    def _auto_init(self):
        cr = self.env.cr
        # rename "value" to "value_tmp"
        # to don't lose values, because during installation the column "value" is deleted
        cr.execute("ALTER TABLE ir_config_parameter RENAME COLUMN value TO value_tmp")
        return super(IrConfigParameter, self)._auto_init()

    def _auto_end(self):
        super(IrConfigParameter, self)._auto_end()
        cr = self.env.cr

        # rename "value_tmp" back to "value_tmp"
        cr.execute("ALTER TABLE ir_config_parameter RENAME COLUMN value_tmp TO value")

        for r in self.env['ir.config_parameter'].sudo().search([]):
            cr.execute("SELECT key,value FROM ir_config_parameter WHERE id = %s", (r.id, ))
            res = cr.dictfetchone()
            value = res.get('value')
            # value may be empty after migration from previous module version
            if value:
                # create default value if it doesn't exist
                r._create_default_value(value)
