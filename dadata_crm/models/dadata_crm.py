# -*- coding: utf-8 -*-
import json
import requests
from odoo import api, fields, models, _, exceptions

class Company(models.Model):
    _inherit = 'res.company'

    key_datata = fields.Char(string='API Key')

    def suggest(self, query=None, resource=None):
        API_KEY = self.key_datata
        BASE_URL = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/%s'
        url = BASE_URL % resource
        headers = {
            'Authorization': 'Token %s' % API_KEY,
            'Content-Type': 'application/json',
        }
        data = {
            'query': query
        }
        r = requests.post(url, data=json.dumps(data), headers=headers)
        return r.json()

class Partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def action_dadata_crm(self):
        API_KEY = self.env.user.company_id.key_datata
        inn = self.name
        if not inn:
            raise exceptions.MissingError('Пожалуйста введите ИНН или имя компании в поле имени!')
        if not API_KEY:
            raise exceptions.MissingError('Пожалуйста введите API Key DaData в настройках компании!')
        company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
        #Данные о компании
        dadata = company.suggest(query=inn, resource='party')
        if dadata['suggestions']:
            self.kpp = dadata['suggestions'][0]['data']['kpp']
            self.inn = dadata['suggestions'][0]['data']['inn']
            self.name = dadata['suggestions'][0]['value']

            # Адрес компании по полям
            address = dadata['suggestions'][0]['data']['address']['unrestricted_value']
            dadata_address = company.suggest(query=address, resource='address')

            region = dadata_address['suggestions'][0]['data']['region_with_type']
            region_kladr = dadata_address['suggestions'][0]['data']['region_kladr_id']
            area = dadata_address['suggestions'][0]['data']['area_with_type']
            city = dadata_address['suggestions'][0]['data']['city_with_type']

            state_id = self.env['res.country.state']
            district_id = self.env['res.state.district']
            city_id = self.env['res.city']
            d_id = False

            search_state = state_id.search([('code', '=', region)])
            search_district = district_id.search([('name', '=', area), ('state_id', '=', search_state.id)])
            if not area:
                search_city = city_id.search([('name', '=', city), ('state_id', '=', search_state.id)]).id
            else:
                search_city = city_id.search([('name', '=', city), ('state_id', '=', search_state.id), ('district_id', '=', search_district.id)]).id

            # State
            if search_state:
                self.state_id = search_state.id
            elif region:
                s_id = state_id.create({
                    'name': region,
                    'country_id': self.env['res.country'].search([('code', '=', 'RU')]).id,
                    'code': region,
                })
                self.state_id = s_id.id
            # District
            if search_district:
                self.district_id = search_district.id
            elif area:
                d_id = district_id.create({
                    'name': area,
                    'state_id': search_state.id or s_id.id,
                }).id
                self.district_id = d_id
            # City
            if search_city:
                self.city_id = search_city
            elif city:
                c_id = city_id.create({
                    'name': city,
                    'state_id': search_state.id or s_id.id,
                    'district_id': search_district.id or d_id or False,
                })
                self.city_id = c_id.id
            self.country_id = self.env['res.country'].search([('code', '=', 'RU')]).id
            self.street = dadata_address['suggestions'][0]['data']['street_with_type']
            self.house = dadata_address['suggestions'][0]['data']['house']
            self.zip = dadata_address['suggestions'][0]['data']['postal_code']
            self.office = dadata_address['suggestions'][0]['data']['flat']
        else:
            raise exceptions.MissingError('Данные о компании не найдены!')

class Bank(models.Model):
    _inherit = 'res.bank'

    correspondent_account = fields.Char('Корреспондентский счет')

    @api.multi
    def action_dadata_bank(self):
        API_KEY = self.env.user.company_id.key_datata
        name = self.name
        if not name:
            raise exceptions.MissingError('Пожалуйста введите БИК банка в поле имени!')
        if not API_KEY:
            raise exceptions.MissingError('Пожалуйста введите API Key DaData в настройках компании!')
        company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
        #Данные о банке
        dadata = company.suggest(query=name, resource='bank')
        if dadata['suggestions']:
            self.name = dadata['suggestions'][0]['data']['name']['payment']
            self.bic = dadata['suggestions'][0]['data']['bic']
            self.correspondent_account = dadata['suggestions'][0]['data']['correspondent_account']
            address = dadata['suggestions'][0]['data']['address']['value']
            dadata_address = company.suggest(query=address, resource='address')

            region = dadata_address['suggestions'][0]['data']['region_with_type']

            state_id = self.env['res.country.state']

            search_state = state_id.search([('code', '=', region)])
            # State
            if search_state:
                self.state = search_state.id
            elif region:
                s_id = state_id.create({
                    'name': region,
                    'country_id': self.env['res.country'].search([('code', '=', 'RU')]).id,
                    'code': region,
                })
                self.state = s_id.id
            self.country = self.env['res.country'].search([('code', '=', 'RU')]).id
            self.city = dadata_address['suggestions'][0]['data']['city_with_type']
            self.zip = dadata_address['suggestions'][0]['data']['postal_code']
            street = dadata_address['suggestions'][0]['data']['street_with_type']
            house = dadata_address['suggestions'][0]['data']['house']
            if street and house:
                self.street = street + ', д. ' + house
        else:
            raise exceptions.MissingError('Данные о банке не найдены!')