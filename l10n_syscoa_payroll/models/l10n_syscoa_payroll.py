# -*- coding:utf-8 -*-
# #############################################################################
#
#    ErgoBIT Payroll Senegal
#    Copyright (C) 2013-TODAY ErgoBIT Consulting (<http://ergobit.org>).
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# #############################################################################

import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import fields, models, api, _
import openerp.addons.decimal_precision as dp
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = 'res.company'

    governmental_org = fields.Boolean('Organisme gouvernemental')
    conv_coll_national = fields.Char('Convention Collective Nationale')
    css_percentage = fields.Selection((('one', '1,0%'), ('three', '3,0%'), ('five', '5,0%')), required=True, default="three", string="CSS - Accident de travail")
    waste_collection_company = fields.Boolean("Entrep. de collecte d'ordure")
    # B    mutual_insurance_employee = fields.Float("Mutuelle - cotisation salariale", digits_compute=dp.get_precision('Account'), help=u"Cotisation salariale à la mutuelle d'assurance par employé.")
    # B    mutual_insurance_company = fields.Float("Mutuelle - cotisation patronale", digits_compute=dp.get_precision('Account'), help="Cotisation patronale à la mutuelle d'assurance par employé.")


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _calculate_social_parts(self):
        parts = 1.00
        for line in self:
            if line.marital == 'married':
                if line.status_spouse == 'non_salaried':
                    parts += 1.00
                else:
                    parts += 0.50
            if line.children:
                parts += float(line.children) / 2
            if parts > 5.00:
                parts = 5.00
            line.parts = parts

    @api.multi
    def _calculate_coefficient(self):
        for line in self:
            if line.marital == 'married':
                coef = 2 if line.status_spouse == 'non_salaried' else 1
            else:
                coef = 1
            line.coef = coef

    @api.multi
    def _user_left_days(self):
        for employee in self:
            legal_leave = employee.company_id.legal_holidays_status_id
            values = legal_leave.get_days(employee.id)
            employee.leaves_taken = values.get('leaves_taken')
            employee.max_leaves = values.get('max_leaves')

    social_parts = fields.Float(compute="_calculate_social_parts", method=True, string="Nombre de parts sociales", store=False)
    ipres_id = fields.Char('N° IPRES')
    css_id = fields.Char('N° Sécurité Sociale')
    status_spouse = fields.Selection((('salaried', 'Salarié(e)'), ('non_salaried', 'Non-salarié(e)')), string='Statut du/de la conjoint(e)', default='salaried')
    coef = fields.Integer(compute="_calculate_coefficient", method=True, string="Coefficient de TRIMF", store=True)
    matricule = fields.Char('Matricule', size=64)
    max_leaves = fields.Float(compute="_user_left_days", string='Acquis', help='This value is given by the sum of all holidays requests with a positive value.',)
    leaves_taken = fields.Float(compute="_user_left_days", string='Pris', help='This value is given by the sum of all holidays requests with a negative value.',)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def _default_governmental_org(self):
        return self.env.user.company_id.governmental_org or False

    @api.model
    def _get_default_journal(self):
        comp_id = 0
        for contract in self:
            comp_id = (contract.company_id and contract.company_id.id)
        if comp_id:
            jrnl = self.env['account.journal'].search([('code', '=', 'PAY'), ('company_id', '=', comp_id)])
        else:
            jrnl = self.env['account.journal'].search([('code', '=', 'PAY')])
        return jrnl and jrnl[0]

    @api.multi
    def _read_governmental_org(self):
        for line in self:
            line.governmental_org = self._default_governmental_org()

    @api.onchange('transport_refund', 'transport_refund_frequence')
    def onchange_transport_refund(self):
        self.ensure_one()
        if self.transport_refund:
            if self.transport_refund_frequence == 'month':
                if self.transport_refund > float(20800.00):
                    self.transport_refund = float(20800.00)
            elif self.transport_refund_frequence == 'day':
                if self.transport_refund > float(950.00):
                    self.transport_refund = float(950.00)

    @api.multi
    def _read_social_parts(self):
        for line in self:
            social_parts = line.employee_id.social_parts or False
            line.niveau = "{:.1f}".format(social_parts)

    @api.multi
    def _read_coefficient(self):
        for line in self:
            line.coef = line.employee_id.coef or False

    @api.multi
    def _get_seniority_date(self):
        for line in self:
            if line.seniority_date_manual:
                line.seniority_date = line.seniority_date_manual_input
            else:
                line.seniority_date = line.date_start

    @api.multi
    def _get_seniority(self):
        for line in self:
            date_1 = datetime.strptime(str(line.seniority_date), '%Y-%m-%d')
            date_2 = datetime.strptime(str(date.today()), '%Y-%m-%d')
            number_of_year = relativedelta.relativedelta(date_2, date_1).years
            number_of_month = relativedelta.relativedelta(date_2, date_1).months
            year_text = "an" if (number_of_year <= 1) else "ans"
            line.seniority = str(number_of_year) + ' ' + year_text + ' et ' + str(number_of_month) + ' mois'

    @api.multi
    def _calculate_seniority_allowance(self):
        for line in self:
            if line.seniority_allowance_manual:
                line.seniority_allowance = float(line.seniority_allowance_manual_input)
            else:
                # Read seniority in years
                date_1 = datetime.strptime(str(line.seniority_date), '%Y-%m-%d')
                date_2 = datetime.strptime(str(date.today()), '%Y-%m-%d')
                seniority = relativedelta.relativedelta(date_2, date_1).years
                if seniority > 25:  # max 25 years
                    seniority = 25
                if seniority >= 2:
                    line.seniority_allowance = float(float(line.wage) * seniority / 100)

    @api.multi
    def _get_mutual_insurance_empl(self):
        for line in self:
            if line.mutual_insurance_empl_manual:
                line.mutual_insurance_employee = float(line.mutual_insurance_empl_manual_input)
            else:
                # Read default mutual_insurance for employee from company data
                # B                res[line.id] = float(self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.mutual_insurance_employee or False)
                line.mutual_insurance_employee = 0.0

    @api.multi
    def _get_mutual_insurance_comp(self):
        for line in self:
            if line.mutual_insurance_comp_manual:
                line.mutual_insurance_comp = float(line.mutual_insurance_comp_manual_input)
            else:
                # Read default mutual_insurance for company from company data
                # B                line. = float(self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.mutual_insurance_company or False)
                line.mutual_insurance_comp = 0.0

    @api.multi
    def _get_gross_invoice(self):
        for line in self:
            if line.gross_invoice_manual:
                line.gross_invoice = float(line.wage)
            else:
                line.gross_invoice = float(line.wage)

    @api.multi
    def _get_leave_days(self):
        for line in self:
            line.leave_days = 0.00
            if line.attribute_leave_days:
                if line.leave_days_manual:
                    line.leave_days = float(line.leave_days_manual_input)
                else:
                    line.leave_days = 2.0

    type_id = fields.Many2one('hr.contract.type', "Type de contrat", required=True)
    struct_id = fields.Many2one('hr.payroll.structure', 'Structure salariale')
    governmental_org = fields.Boolean(compute="_read_governmental_org", method=True, string="Organisme gouvernemental")
    functionary = fields.Boolean(
        "Fonctionnaire de l'état",
        default=_default_governmental_org,
        help="Les fonctionnaires ont droit à une remise de 10% sur l'impôt sur le revenu. Si vous êtes une entreprise publique, alors vous pouvez configurer cette remise pour tous les employés dans les paramètres de la société")

    time_mod = fields.Selection((('fixed', 'Heures de travail fixes'), ('variable', 'Heures de travail variables')), string="Mode de gestion du temps", required=True, default="fixed")
    time_fixed = fields.Float(string="Nombre d'heures fixe prévues", default=173.33, required=True)

    pay_mod = fields.Selection((('Virement', 'Virement'), ('Cheque', 'Chèque'), ('Espece', 'Espèce')), 'Mode de paiement préféré')
    qualif = fields.Char("Qualification")
    niveau = fields.Char(compute="_read_social_parts", method=True, string="Niveau")
    coef = fields.Integer(compute="_read_coefficient", method=True, string="Coefficient")
    indice = fields.Char('Indice')
    category = fields.Char('Catégorie')

    gross_invoice_manual = fields.Boolean("Montant brut facturé")
    gross_invoice = fields.Float(compute="_get_gross_invoice", method=True, string="Montant brut facturé", digits_compute=dp.get_precision('Account'))
    additional_salary = fields.Float('Sursalaire', digits_compute=dp.get_precision('Payroll'))

    union_fee = fields.Float('Cotisation syndicale', digits_compute=dp.get_precision('Payroll'))

    performance_bonus = fields.Float('Prime de rendement', digits_compute=dp.get_precision('Payroll'))
    gratification = fields.Float('Gratification', digits_compute=dp.get_precision('Payroll'))

    seniority_date_manual = fields.Boolean("Date de début", help="La date de début pour le calcul de l'ancienneté est normalement eǵale à la date de début du contrat. Mais vous pouvez la saisir manuellement en activant ce bouton.")
    seniority_date_manual_input = fields.Date("Date de début", digits_compute=dp.get_precision('Payroll'), help="La date de début pour le calcul de l'ancienneté est normalement eǵale à la date de début du contrat. Mais vous pouvez la saisir manuellement en activant le bouton à côté.")
    seniority_date = fields.Date(compute="_get_seniority_date", method=True, string="Date de début", help="La date de début pour le calcul de l'ancienneté est normalement eǵale à la date de début du contrat. Mais vous pouvez la saisir manuellement en activant le bouton à côté.")
    seniority = fields.Char(compute="_get_seniority", method=True, string="Ancienneté")

    seniority_allowance_manual = fields.Boolean("Indemnité d'ancienneté", help="L'indemnité d'ancienneté est normalement calculée automatiquement. Mais vous pouvez le saisir manuellement en activant ce bouton.")
    seniority_allowance_manual_input = fields.Float("Indemnité d'ancienneté", digits_compute=dp.get_precision('Payroll'), help="L'indemnité d'ancienneté est normalement calculée automatiquement. Mais vous pouvez le saisir manuellement en activant le bouton à côté.")
    seniority_allowance = fields.Float(compute="_calculate_seniority_allowance", method=True, string="Indemnité d'ancienneté", digits_compute=dp.get_precision('Account'), help="L'indemnité d'ancienneté est normalement calculée automatiquement. Mais vous pouvez le saisir manuellement en activant le bouton à côté.")

    yearly_max_leaves = fields.Float('Droit de congé par année (en jours)')
    attribute_leave_days = fields.Boolean("Attribuer les congés automatiquement", default=True)
    leave_days_manual = fields.Boolean("Nombre de jours à attribuer par mois", help="Le nombre de jours est normalement eǵale à 2. Mais vous pouvez saisir un autre nombre en cochant le bouton à côté.")
    leave_days_manual_input = fields.Float("Nombre de jours à attribuer par mois", default=2.5, help="Le nombre de jours est normalement eǵale à 2. Mais vous pouvez saisir un autre nombre en cochant le bouton à côté.")
    leave_days = fields.Float(compute="_get_leave_days", method=True, string="Nombre de jours à attribuer par mois", help="Le nombre de jours est normalement eǵale à 2,5. Mais vous pouvez saisir un autre nombre en cochant le bouton à côté.")

    risk_bonus = fields.Float('Prime de risque', digits_compute=dp.get_precision('Payroll'))
    home_bonus = fields.Float('Prime de logement', digits_compute=dp.get_precision('Payroll'))
    cashpoint_bonus = fields.Float('Prime de caisse', digits_compute=dp.get_precision('Payroll'))
    expatriation_bonus = fields.Float("Prime d'expratriation", digits_compute=dp.get_precision('Payroll'))
    basket_bonus = fields.Float('Prime de panier', digits_compute=dp.get_precision('Payroll'))
    responsability_bonus = fields.Float('Prime de responsabilité', digits_compute=dp.get_precision('Payroll'))
    subjection_allowance = fields.Float('Indemnité de sujétion', digits_compute=dp.get_precision('Payroll'))

    food_advantage = fields.Float('Avantage pour nourriture', digits_compute=dp.get_precision('Payroll'))
    domesticity_bonus = fields.Float('Avantage pour logement et domesticité', digits_compute=dp.get_precision('Payroll'))
    family_advantage = fields.Float('Avantages familiaux', digits_compute=dp.get_precision('Payroll'))
    company_car_advantage = fields.Float('Avantage pour véhicule de fonction', digits_compute=dp.get_precision('Payroll'))
    company_phone_advantage = fields.Float('Avantage pour téléphone', digits_compute=dp.get_precision('Payroll'))
    water_electricity_advantage = fields.Float("Avantage pour fourniture d'eau et d'électricité", digits_compute=dp.get_precision('Payroll'))

    kilometer_refund = fields.Float('Indemnité kilométrique', digits_compute=dp.get_precision('Payroll'))
    transport_refund = fields.Float('Indemnité de transport', digits_compute=dp.get_precision('Payroll'))
    transport_refund_frequence = fields.Selection((('day', 'Jour'), ('month', 'Mois')), 'Frequence des indemnités de transport', required=True, default='month')
    meal_voucher = fields.Float('Bons de repas', digits_compute=dp.get_precision('Payroll'))
    meal_voucher_frequence = fields.Selection((('day', 'Jour'), ('month', 'Mois')), 'Frequence des bons de repas', required=True, default='month')

    mutual_insurance_empl_manual = fields.Boolean("Cotisation salariale", help="La cotisation à la mutuelle d'assurance est normalement calculée automatiquement. Mais vous pouvez la saisir manuellement en activant ce bouton.")
    mutual_insurance_empl_manual_input = fields.Float("Cotisation salariale", digits_compute=dp.get_precision('Payroll'), help="La cotisation à la mutuelle d'assurance est normalement calculée automatiquement. Mais vous pouvez la saisir manuellement en activant le bouton à côté.")
    mutual_insurance_empl = fields.Float(compute="_get_mutual_insurance_empl", method=True, string="Cotisation salariale", digits_compute=dp.get_precision('Account'), help="La cotisation à la mutuelle d'assurance est normalement calculée automatiquement. Mais vous pouvez la saisir manuellement en activant le bouton à côté.")

    mutual_insurance_comp_manual = fields.Boolean("Cotisation patronale", help="La cotisation à la mutuelle d'assurance est normalement calculée automatiquement. Mais vous pouvez la saisir manuellement en activant ce bouton.")
    mutual_insurance_comp_manual_input = fields.Float("Cotisation patronale", digits_compute=dp.get_precision('Payroll'), help="La cotisation à la mutuelle d'assurance est normalement calculée automatiquement. Mais vous pouvez la saisir manuellement en activant le bouton à côté.")
    mutual_insurance_comp = fields.Float(compute="_get_mutual_insurance_comp", method=True, string="Cotisation patronale", digits_compute=dp.get_precision('Account'), help="La cotisation à la mutuelle d'assurance est normalement calculée automatiquement. Mais vous pouvez la saisir manuellement en activant le bouton à côté.")

    dirtiness_allowance = fields.Float('Prime de salissure', digits_compute=dp.get_precision('Payroll'))
    journal_id = fields.Many2one(default=_get_default_journal)

    _defaults = {
        'transport_refund_frequence': 'month',
        'transport_refund': 20800.0,
        #        'basket_bonus': 33500.0,
        'meal_voucher_frequence': 'month',
        #        'meal_voucher': 33500.0,
        'functionary': _default_governmental_org,
        'journal_id': _get_default_journal
    }


class HrPayslip(models.Model):
    '''
    Pay Slip
    '''
    _inherit = 'hr.payslip'
    _order = 'id desc'

    @api.onchange('contract_id')
    def onchange_contract(self):
        super(HrPayslip, self).onchange_contract()
        pay_mod = self.contract_id and self.contract_id.pay_mod or False
        leave_days = self.contract_id and self.contract_id.leave_days or 0
        self.pay_mod = pay_mod
        self.leave_days_won = leave_days

    @api.multi
    def action_payslip_done(self):
        for payslip in self:
            if not payslip.employee_id.address_home_id:
                raise UserError(_("L'employé '%s' n'a pas d'adresse personnelle. \nVeuillez renseigner son adresse personnelle dans la fiche de l'employé, \nonglet 'Information personnelle'") % (payslip.employee_id.name,))
        res = super(HrPayslip, self).action_payslip_done()
        # Set additional leaves
        for payslip in self:
            if payslip.leave_days_won > 0:
                if payslip.state == 'verify':
                    if payslip.credit_note:
                        pass
                        # Here we should have a info mesage w/o cancelling process
                        # raise Warning("Veuillez vérifier le congé.")
                    else:
                        payslip.employee_id.remaining_leaves = payslip.remaining_leaves + payslip.leave_days_won

        self.write({'pay_date': date.today()})
        return res

    @api.multi
    def _calculate_rendement(self):
        for line in self:
            if line.is_waste_collector:
                date_1 = datetime.strptime(str(line.date_from), '%Y-%m-%d')
                date_1 = datetime.strptime(str(str(date_1.year) + '-' + str(date_1.month) + '-' + str(26)), '%Y-%m-%d') + relativedelta.relativedelta(months=-1)
                date_1 = date_1.strftime('%Y-%m-%d')
                date_2 = datetime.strptime(str(line.date_to), '%Y-%m-%d')
                date_2 = datetime.strptime(str(str(date_2.year) + '-' + str(date_2.month) + '-' + str(25)), '%Y-%m-%d')
                date_2 = date_2.strftime('%Y-%m-%d')
                analytic_account = self.env['account.analytic.account'].search([('code', '=', line.employee_id.matricule)])
                if analytic_account == []:
                    line.update({'quantity_delivred': 0.00, 'amount_invoiced': 0.00})
                else:
                    cr = self.env.cr
                    cr.execute("""SELECT COALESCE(SUM(amount), 0.0) as amount, COALESCE(SUM(unit_amount), 0.0) as unit_amount \
                        FROM account_analytic_line \
                        WHERE account_id = %s AND date >= %s AND date <= %s""",
                               [analytic_account[0], date_1, date_2])
                    result = dict(cr.dictfetchone())
                    line.update({'quantity_delivred': result['unit_amount'], 'amount_invoiced': result['amount']})
                    # line. = result['unit_amount']
            else:
                line.update({'quantity_delivred': 0.00, 'amount_invoiced': 0.00})

    @api.multi
    def _get_waste_collector(self):
        for line in self:
            line.is_waste_collector = line.company_id.waste_collection_company

    @api.multi
    def _get_holiday_allowance(self):
        for line in self:
            line.holiday_allowance = 0.0
            if line.type in ['leaves', 'mix']:
                if line.holiday_allowance_manual:
                    line.holiday_allowance = float(line.holiday_allowance_manual_input)
                else:
                    # calculate the current month from contract
                    if line.contract_id:
                        gross_of_current_month = line.contract_id.wage \
                            + line.contract_id.additional_salary
                        # amount_of_current_month = float(gross_of_current_month / 12)
#                    # calculate the previous months validated payslips
#                    date_to = line.date_from
#                    date_from = date_to-367
#                    payslip_ids = self.pool.get('hr.payslip').search(cr, uid, \
#                                    [('employee_id', '=', line.employee_id), ('state', '=', 'done'), \
#                                     ('date_from', '>',  date_from), ('date_to', '<',  date_to)])
#                    for idx in range(len(lines_ids)):
# #                    date_from = datetime.strptime(str(line.date_from), '%Y-%m-%d')
# #                    date_from = datetime.strptime(str(str(date_to.year-1) + '-' + str(date_to.month+1) + '-' + str(01)), '%Y-%m-%d')
# #                    date_from = date_to.strftime('%Y-%m-%d')
# #                    mt = line.date_from-1
# if mt in [1, 3, 5, 7, 8, 10, 12]:
# #                        last_day_of_month = 31
# else:
# if mt == 2:
# #                            last_day_of_month = 28
# else:
# #                            last_day_of_month = 30
# #                    date_to = datetime.strptime(str(line.date_from), '%Y-%m-%d')
# #                    date_to = datetime.strptime(str(str(date_to.year) + '-' + str(date_to.month-1) + '-' + str(28)), '%Y-%m-%d')
# #                    date_to = date_to.strftime('%Y-%m-%d')
# #                    payslip_ids = self.pool.get('hr.payslip').search(cr, uid, [('date_from', '>=',  date_from), ('date_from', '<=',  date_to)])

                    gross_of_previous_month = 0.0
                    line.holiday_allowance = float(gross_of_current_month + gross_of_previous_month)

    @api.multi
    def _compute_leave_days(self):

        for record in self:
            employee_id = record.employee_id
            hr_holidays_status_pooler = self.env['hr.holidays.status']
            if employee_id:
                #                res[record.id] = {'leaves_taken': employee_id.leaves_taken, 'remaining_leaves': employee_id.remaining_leaves, 'max_leaves': employee_id.max_leaves}
                hr_holidays_status = hr_holidays_status_pooler.search([('id', 'in', [employee_id.company_id.legal_holidays_status_id.id,
                                                                                     employee_id.company_id.legal_holidays_status_id_n1.id,
                                                                                     employee_id.company_id.legal_holidays_status_id_n2.id])])
                leave_days = hr_holidays_status_pooler.get_days(hr_holidays_status, employee_id.id)
                record.update({
                    'leaves_taken': leave_days[employee_id.company_id.legal_holidays_status_id.id]['leaves_taken'] if employee_id.company_id.legal_holidays_status_id else 0.0,
                    'remaining_leaves': leave_days[employee_id.company_id.legal_holidays_status_id.id]['remaining_leaves'] if employee_id.company_id.legal_holidays_status_id else 0.0,
                    'max_leaves': leave_days[employee_id.company_id.legal_holidays_status_id.id]['max_leaves'] if employee_id.company_id.legal_holidays_status_id else 0.0,
                    'leaves_taken_n1': leave_days[employee_id.company_id.legal_holidays_status_id_n1.id]['leaves_taken'] if employee_id.company_id.legal_holidays_status_id_n1 else 0.0,
                    'remaining_leaves_n1': leave_days[employee_id.company_id.legal_holidays_status_id_n1.id]['remaining_leaves'] if employee_id.company_id.legal_holidays_status_id_n1 else 0.0,
                    'max_leaves_n1': leave_days[employee_id.company_id.legal_holidays_status_id_n1.id]['max_leaves'] if employee_id.company_id.legal_holidays_status_id_n1 else 0.0,
                    'leaves_taken_n2': leave_days[employee_id.company_id.legal_holidays_status_id_n2.id]['leaves_taken'] if employee_id.company_id.legal_holidays_status_id_n2 else 0.0,
                    'remaining_leaves_n2': leave_days[employee_id.company_id.legal_holidays_status_id_n2.id]['remaining_leaves'] if employee_id.company_id.legal_holidays_status_id_n2 else 0.0,
                    'max_leaves_n2': leave_days[employee_id.company_id.legal_holidays_status_id_n2.id]['max_leaves'] if employee_id.company_id.legal_holidays_status_id_n2 else 0.0,
                })
            else:
                #                res[record.id] = {'leaves_taken': 0, 'remaining_leaves': 0, 'max_leaves': 0}
                record.update({
                    'leaves_taken': 0,
                    'remaining_leaves': 0,
                    'max_leaves': 0,
                    'leaves_taken_n1': 0,
                    'remaining_leaves_n1': 0,
                    'max_leaves_n1': 0,
                    'leaves_taken_n2': 0,
                    'remaining_leaves_n2': 0,
                    'max_leaves_n2': 0
                })

    type = fields.Selection((('salary', 'Salaire'), ('leaves', 'Congé'), ('mix', 'Salaire et Congé')), readonly=True, states={'draft': [('readonly', False)]}, required=True, default="salary", string="Type de bulletin")
    pay_date = fields.Date('Date de Paiement', default=lambda *a: time.strftime("%Y-%m-%d"))
    pay_mod = fields.Selection((('Virement', 'Virement'), ('Cheque', 'Chèque'), ('Espece', 'Espèce')), 'Mode de Paiement')
    is_waste_collector = fields.Boolean(compute="_get_waste_collector", method=True, store=False)
    quantity_delivred = fields.Float(compute="_calculate_rendement", method=True, digits_compute=dp.get_precision('Product UoS'), store=True,)
    amount_invoiced = fields.Float(compute="_calculate_rendement", method=True, digits_compute=dp.get_precision('Payroll'), store=True,)
    leave_days_won = fields.Float(string="À ajouter", readonly=True, states={'draft': [('readonly', False)]}, help="Le nombre de jours de congés acquis par l'emploi dans le mois payé.")
    max_leaves = fields.Float(compute="_compute_leave_days", string='Acquis', store=True, help='This value is given by the sum of all holidays requests with a positive value.',)
    leaves_taken = fields.Float(compute="_compute_leave_days", string='Pris', store=True, help='This value is given by the sum of all holidays requests with a negative value.',)
    remaining_leaves = fields.Float(compute="_compute_leave_days", string='Restant', store=True, help='Maximum Leaves Allowed - Leaves Already Taken',)
    max_leaves_n1 = fields.Float(compute="_compute_leave_days", string='Acquis N-1', store=True, help='This value is given by the sum of all holidays requests with a positive value.',)
    leaves_taken_n1 = fields.Float(compute="_compute_leave_days", string='Pris N-1', store=True, help='This value is given by the sum of all holidays requests with a negative value.',)
    remaining_leaves_n1 = fields.Float(compute="_compute_leave_days", string='Restant N-1', store=True, help='Maximum Leaves Allowed - Leaves Already Taken',)
    max_leaves_n2 = fields.Float(compute="_compute_leave_days", string='Acquis N-2', store=True, help='This value is given by the sum of all holidays requests with a positive value.',)
    leaves_taken_n2 = fields.Float(compute="_compute_leave_days", string='Pris N-2', store=True, help='This value is given by the sum of all holidays requests with a negative value.',)
    remaining_leaves_n2 = fields.Float(compute="_compute_leave_days", string='Restant N-2', store=True, help='Maximum Leaves Allowed - Leaves Already Taken',)
    holiday_allowance_manual = fields.Boolean("Montant brut de l'indemnité", readonly=True, states={'draft': [('readonly', False)]}, help="Le montant du droit de congé est normalement calculé automatiquement. Mais vous pouvez le saisir manuellement en activant le bouton à côté.")
    holiday_allowance_manual_input = fields.Float("Montant brut de l'indemnité", readonly=True, states={'draft': [('readonly', False)]}, digits_compute=dp.get_precision('Payroll'), help="Le montant du droit de congé est normalement calculé automatiquement. Mais vous pouvez le saisir manuellement en activant le bouton à côté.")
    holiday_allowance = fields.Float(compute="_get_holiday_allowance", method=True, string="Montant brut de l'indemnité", store=True, digits_compute=dp.get_precision('Payroll'), help="Le montant du droit de congé est normalement calculé automatiquement. Mais vous pouvez le saisir manuellement en activant le bouton à côté.")

    @api.multi
    def get_worked_hours(self, code):
        """
        @return: the workday hours in the payslip by worked_days_line code.
        Mainly called from payslip report
        """
        result = 0.00
        for payslip in self:
            for wdline in payslip.worked_days_line_ids:
                if wdline.code == code:
                    result += wdline.number_of_hours
        return result

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def was_on_leave(employee_id, datetime_day):
            day = fields.Date.to_string(datetime_day)
            return self.env['hr.holidays'].search([
                ('state', '=', 'validate'),
                ('employee_id', '=', employee_id),
                ('type', '=', 'remove'),
                ('date_from', '<=', day),
                ('date_to', '>=', day)
            ], limit=1).holiday_status_id.name

        res = []
        # fill only if the contract as a working schedule linked
        for contract in self.env['hr.contract'].browse(contract_ids):  # .filtered(lambda contract: contract.working_hours):
            attendances = {
                'name': _("Temps de travail contractuel"),
                # 'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            leaves = {}
            day_from = fields.Datetime.from_string(date_from)
            day_to = fields.Datetime.from_string(date_to)
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
                working_hours_on_day = contract.working_hours.working_hours_on_day(day_from + timedelta(days=day))
                if working_hours_on_day:
                    # the employee had to work
                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day))
                    if leave_type:
                        # if he was on leave, fill the leaves dict
                        if leave_type in leaves:
                            leaves[leave_type]['number_of_days'] += 1.0
                            leaves[leave_type]['number_of_hours'] += working_hours_on_day
                        else:
                            leaves[leave_type] = {
                                'name': leave_type,
                                'sequence': 5,
                                'code': leave_type,
                                'number_of_days': 1.0,
                                'number_of_hours': working_hours_on_day,
                                'contract_id': contract.id,
                            }
                    else:
                        # add the input vals to tmp (increment if existing)
                        attendances['number_of_days'] += 1.0
                        # attendances['number_of_hours'] += working_hours_on_day  # B replaced by the next 4 lines
                        if contract.time_mod == 'fixed':
                            attendances['number_of_hours'] = contract.time_fixed
                        else:
                            attendances['number_of_hours'] += working_hours_on_day

            if attendances['number_of_hours'] == 0.0:
                attendances['number_of_hours'] = contract.time_fixed

            leaves = [value for key, value in leaves.items()]

# B          add a placeholder for actually worked days/hours (to be entered by user if needed)
            actually_worked = {
                'name': _("Temps de travail effectif"),
                'sequence': 2,
                'code': 'WORKED',
                'number_of_days': attendances['number_of_days'],
                'number_of_hours': contract.time_fixed,
                'contract_id': contract.id,
            }

            res += [attendances] + [actually_worked] + leaves
        return res


class HrPayslipLine(models.Model):
    '''
    Payslip Line
    '''
    _name = 'hr.payslip.line'
    _inherit = 'hr.payslip.line'

    @api.multi
    def _calculate_total2(self):
        for line in self:
            line.total2 = float(line.quantity2) * line.amount2 * line.rate2 / 100

    rate2 = fields.Float('Rate2 (%)', digits_compute=dp.get_precision('Payroll Rate'), default=100.0)
    amount2 = fields.Float('Amount2', digits_compute=dp.get_precision('Payroll'))
    quantity2 = fields.Float('Quantity2', digits_compute=dp.get_precision('Payroll'), default=1.0)
    total2 = fields.Float(compute="_calculate_total2", method=True, string='Total2', digits_compute=dp.get_precision('Payroll'), store=True)


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    _order = 'id desc'
