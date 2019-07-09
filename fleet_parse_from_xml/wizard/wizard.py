# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api
from bs4 import BeautifulSoup
import datetime
import base64


class PosCreditInvoices(models.TransientModel):
    _name = 'driving.data.wizard'
    _description = 'Parses XML to Driving Data Record'

    xml_data = fields.Binary(attachment=True, string="Origin", help="XML File")
    # text_data = fields.Text(string="Origin", help="TEXT")

    @api.multi
    def apply(self):

        xml_file = base64.b64decode(self.xml_data)
        xml = BeautifulSoup(xml_file)
        dd = xml.html.body.driverdata

        def p2str(data):
            return data and data.text or ''

        def str2int(data):
            return data and int(float(data)) or False

        def p2int(data):
            return str2int(p2str(data))

        def str2datetime(data):
            return datetime.datetime.strptime(data[0:-1], '%Y-%m-%d %H:%M:%S')

        def get_attr(data, attr):
            return data and data[attr] or ''

        def get_int_attr(data, attr):
            return str2int(get_attr(data, attr))

        def get_bool_attr(data, attr):
            attr = get_attr(data, attr)
            return attr and attr == 'True' or False

        def get_datetime_attr(data, attr):
            return str2datetime(get_attr(data, attr))

        def compose_as_a_new_record(data):
            return [(0, 0, data)]

        def compose_as_a_new_record_set(data):
            res = []
            for r in data:
                res += compose_as_a_new_record(r)
            return res

        def parse_card_icc_identification(data):
            cardextendedserialnumber = data.cardextendedserialnumber
            return {
                'clock_stop': p2int(data.clockstop),

                'card_extended_serial_number': p2int(cardextendedserialnumber),
                'manufacturer_code': get_int_attr(cardextendedserialnumber, 'manufacturercode'),
                'month': get_int_attr(cardextendedserialnumber, 'month'),
                'year': get_int_attr(cardextendedserialnumber, 'year'),

                'card_approval_number': p2str(data.cardapprovalnumber),
                'card_personaliser_id': p2int(data.cardpersonaliserid),
                'embed_deric_assembler_id': p2str(data.embeddericassemblerid),
                'ic_identifier': p2int(data.icidentifier),
            }

        def parse_card_chip_identification(data):
            return {
                'ic_serial_number': get_attr(data.icserialnumber, 'value'),
                'ic_manufacturing_reference': get_attr(data.icmanufacturingreferences, 'value'),
            }

        def parse_driver_card_application_identification(data):
            return {
                'type': p2int(data.type),
                'version': p2int(data.version),
                'no_of_events_per_type': p2int(data.noofeventspertype),
                'no_of_faults_per_type': p2int(data.nooffaultspertype),
                'activity_structure_length': p2int(data.activitystructurelength),
                'no_of_card_vehicle_records': p2int(data.noofcardvehiclerecords),
                'no_of_card_place_records': p2int(data.noofcardplacerecords),
            }

        def parse_card_identification(data):
            cardnumber = data.cardnumber
            return {
                'card_issuing_member_state': p2int(data.cardissuingmemberstate),

                'card_number': p2str(cardnumber),
                'renewal_index': get_int_attr(cardnumber, 'renewalindex'),
                'replacement_index': get_int_attr(cardnumber, 'replacementindex'),

                'card_issuing_authority_name': p2str(data.cardissuingauthorityname),
                'card_issue_date': get_datetime_attr(data.cardissuedate, 'datetime'),
                'card_validity_begin': get_datetime_attr(data.cardvaliditybegin, 'datetime'),
                'card_expiry_date': get_datetime_attr(data.cardexpirydate, 'datetime'),
            }

        def parse_card_collection(data, key):
            result_set = []
            for cerc in data.find_all('card' + key + 'recordcollection'):
                cerc_data = {}
                cer_records = cerc.find_all('card' + key + 'record')
                if not len(cer_records):
                    continue
                if key == 'event':
                    cerc_data['type'] = p2int(cer_records[0].eventtype)
                if key == 'fault':
                    cerc_data['type'] = p2int(cer_records[0].faulttype)
                cerc_data['vehicle_registration_nation'] = p2int(cer_records[0].vehicleregistrationnation)
                cerc_data['vehicle_registration_number'] = p2str(cer_records[0].vehicleregistrationnumber)
                cerc_data['card_' + key + '_record_ids'] = []
                for cer in cer_records:
                    cerc_data['card_' + key + '_record_ids'] += compose_as_a_new_record({
                        'begin_time': get_datetime_attr(key == 'event' and cer.eventbegintime or cer.faultbegintime, 'datetime'),
                        'end_time': get_datetime_attr(key == 'event' and cer.eventendtime or cer.faultendtime, 'datetime'),
                    })
                result_set += compose_as_a_new_record(cerc_data)

            return {
                'card_' + key + '_collection_ids': result_set,
            }

        def parse_driver_activity_data(data):
            result_set = []
            for cdadr in data.find_all('cardactivitydailyrecord'):
                result_set += compose_as_a_new_record({
                    'daily_presence_counter': get_int_attr(cdadr, 'dailypresencecounter'),
                    'datetime': get_datetime_attr(cdadr, 'datetime'),
                    'distance': get_int_attr(cdadr, 'distance'),
                    'activity_change_info_ids': compose_as_a_new_record_set({
                        'file_offset': get_attr(r, 'fileoffset'),
                        'slot': get_int_attr(r, 'slot'),
                        'status': get_int_attr(r, 'status'),
                        'inserted': get_bool_attr(r, 'inserted'),
                        'activity': get_attr(r, 'inserted'),
                        'time': get_attr(r, 'time')
                    } for r in cdadr.find_all('activitychangeinfo'))
                })
            return {
                'activity_daily_ids': result_set,
            }

        def parse_card_vehicle_used(data):
            result_set = []
            for cvr in data.cardvehiclerecords.find_all('cardvehiclerecord'):
                result_set += compose_as_a_new_record({
                    'vehicle_odometer_begin': p2int(cvr.vehicleodometerbegin),
                    'vehicle_odometer_end': p2int(cvr.vehicleodometerend),
                    'vehicle_first_use': get_datetime_attr(cvr.vehiclefirstuse, 'datetime'),
                    'vehicle_last_use': get_datetime_attr(cvr.vehiclelastuse, 'datetime'),
                    'vehicle_registration_nation': p2int(cvr.vehicleregistrationnation),
                    'vehicle_registration_number': p2str(cvr.vehicleregistrationnumber),
                })
            return {
                'vehicle_pointer_newest_record': p2int(data.vehiclepointernewestrecord),
                'vehicle_record_ids': result_set,
            }

        def parse_card_place_daily_work_period(data):
            result_set = []
            for cvr in data.placerecords.find_all('placerecord'):
                result_set += compose_as_a_new_record({
                    'entry_time': get_datetime_attr(cvr.entrytime, 'datetime'),
                    'entry_type': p2int(cvr.entrytype),
                    'daily_work_period_country_name': get_attr(cvr.dailyworkperiodcountryname, 'name'),
                    'daily_work_period_country': p2int(cvr.dailyworkperiodcountry),
                    'daily_work_period_region': p2int(cvr.dailyworkperiodregion),
                    'vehicle_odometer_value': p2int(cvr.vehicleodometervalue),
                })
            return {
                'place_pointer_newest_record': p2int(data.placepointernewestrecord),
                'place_daily_work_ids': result_set,
            }

        def parse_card_control_activity_data_record(data):
            control_card_number = data.controlcardnumber
            return {
                'control_type': p2int(data.controltype),
                'control_time': get_datetime_attr(data.controltime, 'datetime'),
                'control_download_period_begin': get_datetime_attr(data.controldownloadperiodbegin, 'datetime'),
                'control_download_period_end': get_datetime_attr(data.controldownloadperiodend, 'datetime'),

                'control_card_number_type': get_int_attr(control_card_number, 'type'),
                'control_card_number_issuingmemberstate': get_int_attr(control_card_number, 'issuingmemberstate'),
                'control_card_number_replacementindex': get_int_attr(control_card_number, 'replacementindex'),
                'control_card_number_renewalindex': get_int_attr(control_card_number, 'renewalindex'),
                'vehicle_registration_nation': p2int(data.vehicleregistrationnation),
                'vehicle_registration_number': p2str(data.vehicleregistrationnumber),
            }

        def parse_specific_conditions(data):
            result_set = []
            for cvr in data.specificconditionrecords.find_all('specificconditionrecord'):
                result_set += compose_as_a_new_record({
                    'entry_time': get_datetime_attr(cvr.entrytime, 'datetime'),
                    'specific_condition_type': p2int(cvr.specificconditiontype),
                })
            return {
                'specific_condition_ids': result_set,
            }

        def parse_card_certificate(data):
            certification_authority_reference = data.certificationauthorityreference
            return {
                'card_certificate_signature': get_attr(data.signature, 'value'),
                'card_certificate_public_key_remainder': get_attr(data.publickeyremainder, 'value'),
                'card_certificate_authority_nation_name': get_attr(certification_authority_reference.nation, 'name'),
                'card_certificate_authority_nation': p2int(certification_authority_reference.nation),
                'card_certificate_authority_nation_code': p2str(certification_authority_reference.nationcode),
                'card_certificate_authority_serial_number': p2int(certification_authority_reference.serialnumber),
                'card_certificate_authority_additional_info': p2str(certification_authority_reference.additionalinfo),
                'card_certificate_authority_ca_identifier': p2int(certification_authority_reference.caidentifier),
            }

        def parse_ca_certificate(data):
            certification_authority_reference = data.certificationauthorityreference
            return {
                'ca_certificate_signature': get_attr(data.signature, 'value'),
                'ca_certificate_public_key_remainder': get_attr(data.publickeyremainder, 'value'),
                'ca_certificate_authority_nation_name': get_attr(certification_authority_reference.nation, 'name'),
                'ca_certificate_authority_nation': p2int(certification_authority_reference.nation),
                'ca_certificate_authority_nation_code': p2str(certification_authority_reference.nationcode),
                'ca_certificate_authority_serial_number': p2int(certification_authority_reference.serialnumber),
                'ca_certificate_authority_additional_info': p2str(certification_authority_reference.additionalinfo),
                'ca_certificate_authority_ca_identifier': p2int(certification_authority_reference.caidentifier),
            }

        data = {
            'xml_data': self.xml_data,
        }
        card_icc = parse_card_icc_identification(dd.cardiccidentification)
        data.update(card_icc)

        card_chip = parse_card_chip_identification(dd.cardchipidentification)
        data.update(card_chip)

        card_application_identification = parse_driver_card_application_identification(dd.drivercardapplicationidentification)
        data.update(card_application_identification)

        card_identification = dd.identification and dd.identification.cardidentification
        if card_identification:
            card_identification = parse_card_identification(card_identification)
            data.update(card_identification)

        events_data = dd.eventsdata and dd.eventsdata.cardeventrecords
        if events_data:
            events_data = parse_card_collection(events_data, 'event')
            data.update(events_data)

        faults_data = dd.faultsdata and dd.faultsdata.cardfaultrecords
        if faults_data:
            faults_data = parse_card_collection(faults_data, 'fault')
            data.update(faults_data)

        driver_activity_data = dd.driveractivitydata and dd.driveractivitydata.carddriveractivity
        if driver_activity_data:
            driver_activity_data = parse_driver_activity_data(driver_activity_data)
            data.update(driver_activity_data)

        card_vehicles_used = parse_card_vehicle_used(dd.cardvehiclesused)
        data.update(card_vehicles_used)

        card_place_daily_work_period = parse_card_place_daily_work_period(dd.cardplacedailyworkperiod)
        data.update(card_place_daily_work_period)

        card_control_activity_data_record = parse_card_control_activity_data_record(dd.cardcontrolactivitydatarecord)
        data.update(card_control_activity_data_record)

        specific_conditions = parse_specific_conditions(dd.specificconditions)
        data.update(specific_conditions)

        card_certificate = parse_card_certificate(dd.cardcertificate)
        data.update(card_certificate)

        ca_certificate = parse_ca_certificate(dd.cacertificate)
        data.update(ca_certificate)

        driver_data_record = self.env['driving.data'].create(data)
        final_url = "/web/?#id=" + str(driver_data_record.id) + "&view_type=form&model=driving.data"
        return {'type': 'ir.actions.act_url', 'url': final_url, 'target': 'self', }
