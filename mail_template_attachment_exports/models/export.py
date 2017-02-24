# -*- coding: utf-8 -*-
import itertools
import operator

import odoo
from odoo import models
from odoo.tools.misc import xlwt


class Export(models.AbstractModel):
    """Copy-paste from web/controllers/main.py
    with following updates:
    * http.Controller replaced with models.AbstractModel
    * request replaced with self
    * @http.route are removed
    * lint warnings are fixed
    """
    _name = 'mail_template_attachment_exports.abstract_export'

    def formats(self):
        """ Returns all valid export formats

        :returns: for each export format, a pair of identifier and printable name
        :rtype: [(str, str)]
        """
        return [
            {'tag': 'csv', 'label': 'CSV'},
            {'tag': 'xls', 'label': 'Excel', 'error': None if xlwt else "XLWT required"},
        ]

    def fields_get(self, model):
        Model = self.env[model]
        fields = Model.fields_get()
        return fields

    def get_fields(self, model, prefix='', parent_name='',
                   import_compat=True, parent_field_type=None,
                   exclude=None):

        if import_compat and parent_field_type == "many2one":
            fields = {}
        else:
            fields = self.fields_get(model)

        if import_compat:
            fields.pop('id', None)
        else:
            fields['.id'] = fields.pop('id', {'string': 'ID'})

        fields_sequence = sorted(
            fields.iteritems(),
            key=lambda field: odoo.tools.ustr(field[1].get('string', '')))

        records = []
        for field_name, field in fields_sequence:
            if import_compat:
                if exclude and field_name in exclude:
                    continue
                if field.get('readonly'):
                    # If none of the field's states unsets readonly, skip the field
                    if all(dict(attrs).get('readonly', True)
                           for attrs in field.get('states', {}).values()):
                        continue
            if not field.get('exportable', True):
                continue

            id = prefix + (prefix and '/'or '') + field_name
            name = parent_name + (parent_name and '/' or '') + field['string']
            record = {'id': id, 'string': name,
                      'value': id, 'children': False,
                      'field_type': field.get('type'),
                      'required': field.get('required'),
                      'relation_field': field.get('relation_field')}
            records.append(record)

            if len(name.split('/')) < 3 and 'relation' in field:
                ref = field.pop('relation')
                record['value'] += '/id'
                record['params'] = {'model': ref, 'prefix': id, 'name': name}

                if not import_compat or field['type'] == 'one2many':
                    # m2m field in import_compat is childless
                    record['children'] = True

        return records

    def namelist(self, model, export_id):
        # TODO: namelist really has no reason to be in Python (although itertools.groupby helps)
        export = self.env['ir.exports'].browse([export_id]).read()[0]
        export_fields_list = self.env['ir.exports.line'].browse(export['export_fields']).read()

        fields_data = self.fields_info(
            model, map(operator.itemgetter('name'), export_fields_list))

        return [
            {'name': field['name'], 'label': fields_data[field['name']]}
            for field in export_fields_list
        ]

    def fields_info(self, model, export_fields):
        info = {}
        fields = self.fields_get(model)
        if ".id" in export_fields:
            fields['.id'] = fields.pop('id', {'string': 'ID'})

        # To make fields retrieval more efficient, fetch all sub-fields of a
        # given field at the same time. Because the order in the export list is
        # arbitrary, this requires ordering all sub-fields of a given field
        # together so they can be fetched at the same time
        #
        # Works the following way:
        # * sort the list of fields to export, the default sorting order will
        #   put the field itself (if present, for xmlid) and all of its
        #   sub-fields right after it
        # * then, group on: the first field of the path (which is the same for
        #   a field and for its subfields and the length of splitting on the
        #   first '/', which basically means grouping the field on one side and
        #   all of the subfields on the other. This way, we have the field (for
        #   the xmlid) with length 1, and all of the subfields with the same
        #   base but a length "flag" of 2
        # * if we have a normal field (length 1), just add it to the info
        #   mapping (with its string) as-is
        # * otherwise, recursively call fields_info via graft_subfields.
        #   all graft_subfields does is take the result of fields_info (on the
        #   field's model) and prepend the current base (current field), which
        #   rebuilds the whole sub-tree for the field
        #
        # result: because we're not fetching the fields_get for half the
        # database models, fetching a namelist with a dozen fields (including
        # relational data) falls from ~6s to ~300ms (on the leads model).
        # export lists with no sub-fields (e.g. import_compatible lists with
        # no o2m) are even more efficient (from the same 6s to ~170ms, as
        # there's a single fields_get to execute)
        for (base, length), subfields in itertools.groupby(
                sorted(export_fields),
                lambda field: (field.split('/', 1)[0], len(field.split('/', 1)))):
            subfields = list(subfields)
            if length == 2:
                # subfields is a seq of $base/*rest, and not loaded yet
                info.update(self.graft_subfields(
                    fields[base]['relation'], base, fields[base]['string'],
                    subfields
                ))
            elif base in fields:
                info[base] = fields[base]['string']

        return info

    def graft_subfields(self, model, prefix, prefix_string, fields):
        export_fields = [field.split('/', 1)[1] for field in fields]
        return (
            (prefix + '/' + k, prefix_string + '/' + v)
            for k, v in self.fields_info(model, export_fields).iteritems())
