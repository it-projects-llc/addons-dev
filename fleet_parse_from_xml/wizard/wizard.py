# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api
from bs4 import BeautifulSoup
import datetime


class PosCreditInvoices(models.TransientModel):
    _name = 'driving.data.wizard'
    _description = 'Parses XML to Driving Data Record'

    xml_data = fields.Binary(attachment=True, string="Origin", help="XML File")
    text_data = fields.Text(string="Origin", help="TEXT")

    @api.multi
    def apply(self):
        xml = BeautifulSoup(self.text_data)
        dd = xml.driverdata

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

        def parse_card_icc_identification(text):
            cardextendedserialnumber = text.cardextendedserialnumber
            return {
                'clock_stop': p2int(text.clockstop),

                'card_extended_serial_number': p2int(cardextendedserialnumber),
                'manufacturer_code': get_int_attr(cardextendedserialnumber, 'manufacturercode'),
                'month': get_int_attr(cardextendedserialnumber, 'month'),
                'year': get_int_attr(cardextendedserialnumber, 'year'),

                'card_approval_number': p2str(text.cardapprovalnumber),
                'card_personaliser_id': p2int(text.cardpersonaliserid),
                'embed_deric_assembler_id': p2str(text.embeddericassemblerid),
                'ic_identifier': p2int(text.icidentifier),
            }

        def parse_card_chip_identification(text):
            return {
                'ic_serial_number': get_attr(text.icserialnumber, 'value'),
                'ic_manufacturing_reference': get_attr(text.icmanufacturingreferences, 'value'),
            }

        def parse_driver_card_application_identification(text):
            return {
                'type': p2int(text.type),
                'version': p2int(text.version),
                'no_of_events_per_type': p2int(text.noofeventspertype),
                'no_of_faults_per_type': p2int(text.nooffaultspertype),
                'activity_structure_length': p2int(text.activitystructurelength),
                'no_of_card_vehicle_records': p2int(text.noofcardvehiclerecords),
                'no_of_card_place_records': p2int(text.noofcardplacerecords),
            }

        def parse_card_identification(text):
            cardnumber = text.cardnumber
            return {
                'card_issuing_member_state': p2int(text.cardissuingmemberstate),

                'card_number': p2str(cardnumber),
                'renewal_index': get_int_attr(cardnumber, 'renewalindex'),
                'replacement_index': get_int_attr(cardnumber, 'replacementindex'),

                'card_issuing_authority_name': p2str(text.cardissuingauthorityname),
                'card_issue_date': get_datetime_attr(text.cardissuedate, 'datetime'),
                'card_validity_begin': get_datetime_attr(text.cardvaliditybegin, 'datetime'),
                'card_expiry_date': get_datetime_attr(text.cardexpirydate, 'datetime'),
            }

        def parse_card_collection(text, key):
            result_set = []
            for cerc in text.find_all('card' + key + 'recordcollection'):
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
                'controldownloadperiodbegin': get_datetime_attr(data.controldownloadperiodbegin, 'datetime'),
                'controldownloadperiodend': get_datetime_attr(data.controldownloadperiodend, 'datetime'),

                'control_card_number_type': get_int_attr(control_card_number, 'type'),
                'control_card_number_issuingmemberstate': get_int_attr(control_card_number, 'issuingmemberstate'),
                'control_card_number_replacementindex': get_int_attr(control_card_number, 'replacementindex'),
                'control_card_number_renewalindex': get_int_attr(control_card_number, 'renewalindex'),
                'vehicle_registration_nation': p2int(data.vehicleregistrationnation),
                'vehicle_registration_number': p2str(data.vehicleregistrationnumber),
            }

        data = {
            'text_data': self.text_data,
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

        import wdb
        wdb.set_trace()

        self.env['driving.data'].create(data)

        return {'type': 'ir.actions.client', 'tag': 'reload'}
