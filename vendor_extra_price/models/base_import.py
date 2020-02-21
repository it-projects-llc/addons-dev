from odoo import api, fields, models

class Import(models.TransientModel):
    _inherit = 'base_import.import'

    @api.multi
    def do(self, fields, columns, options, dryrun=False, product_vendor=False, product_pricelist=False):
        """ Actual execution of the import

        :param fields: import mapping: maps each column to a field,
                       ``False`` for the columns to ignore
        :type fields: list(str|bool)
        :param columns: columns label
        :type columns: list(str|bool)
        :param dict options:
        :param bool dryrun: performs all import operations (and
                            validations) but rollbacks writes, allows
                            getting as much errors as possible without
                            the risk of clobbering the database.
        :returns: A list of errors. If the list is empty the import
                  executed fully and correctly. If the list is
                  non-empty it contains dicts with 3 keys ``type`` the
                  type of error (``error|warning``); ``message`` the
                  error message associated with the error (a string)
                  and ``record`` the data which failed to import (or
                  ``false`` if that data isn't available or provided)
        :rtype: dict(ids: list(int), messages: list({type, message, record}))
        """
        import_result = super(Import, self).do(fields, columns, options, dryrun)
        data = {key: options.get(key) for key in ['vendor_id', 'pricelist_id'] if key in options}
        if data:
            product_ids = self.env['product.template'].browse(import_result.get('ids'))
            product_ids.write(data)
            product_ids._compute_list_price()
        # import wdb;wdb.set_trace()
        return import_result
