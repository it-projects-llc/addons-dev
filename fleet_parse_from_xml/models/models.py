# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class DrivingData(models.Model):
    _name = "driving.data"

    # common fields
    date_created = fields.Datetime(string='Date Created', readonly=True, default=fields.Datetime.now)
    xml_data = fields.Binary(attachment=True, string="Origin", help="XML File")
    text_data = fields.Text(string="Origin", help="TXT")
    # cardiccidentification
    clock_stop = fields.Integer('Clock Stop', default=0)

    card_extended_serial_number = fields.Integer('card_extended_serial_number')
    manufacturer_code = fields.Integer('manufacturer_code')
    month = fields.Integer('month')
    year = fields.Integer('year')

    card_approval_number = fields.Char('card_approval_number')
    card_personaliser_id = fields.Integer('card_personaliser_id')
    embed_deric_assembler_id = fields.Char('embed_deric_assembler_id')
    ic_identifier = fields.Integer('Ic Identifier')

    # cardchipidentification
    ic_serial_number = fields.Char('ic_serial_number')
    ic_manufacturing_reference = fields.Char('ic_manufacturing_reference')

    # card_application_identification
    type = fields.Integer('type')
    version = fields.Integer('version')
    no_of_events_per_type = fields.Integer('no_of_events_per_type')
    no_of_faults_per_type = fields.Integer('no_of_faults_per_type')
    activity_structure_length = fields.Integer('activity_structure_length')
    no_of_card_vehicle_records = fields.Integer('no_of_card_vehicle_records')
    no_of_card_place_records = fields.Integer('no_of_card_place_records')

    # cardidentification
    card_issuing_member_state = fields.Integer('card_issuing_member_state')

    card_number = fields.Char('card_number')
    renewal_index = fields.Integer('renewal_index')
    replacement_index = fields.Integer('replacement_index')

    card_issuing_authority_name = fields.Char('card_issuing_authority_name')
    card_issue_date = fields.Datetime('card_issue_date')
    card_validity_begin = fields.Datetime('card_validity_begin')
    card_expiry_date = fields.Datetime('card_expiry_date')

    # CardEventCollection
    card_event_collection_ids = fields.One2many('card.event.collection', 'driving_data_id',
                                                string="card_event_collection_ids")
    card_fault_collection_ids = fields.One2many('card.fault.collection', 'driving_data_id',
                                                string="card_fault_collection_ids")
    activity_daily_ids = fields.One2many('activity.daily', 'driving_data_id',
                                         string="activity.daily")

    vehicle_pointer_newest_record = fields.Integer('vehicle_pointer_newest_record')
    vehicle_record_ids = fields.One2many('vehicle.record', 'driving_data_id',
                                         string="vehicle.record")

    place_pointer_newest_record = fields.Integer('place_pointer_newest_record')
    place_daily_work_ids = fields.One2many('place.record', 'driving_data_id',
                                           string="place_daily_work_ids")
    # CardControlActivityDataRecord
    control_type = fields.Integer('control_type')
    control_time = fields.Datetime('control_time')
    control_card_number_type = fields.Integer('control_card_number_type')
    control_card_number_issuingmemberstate = fields.Integer('control_card_number_issuingmemberstate')
    control_card_number_replacementindex = fields.Integer('control_card_number_replacementindex')
    control_card_number_renewalindex = fields.Integer('control_card_number_renewalindex')
    vehicle_registration_nation = fields.Integer('vehicle_registration_nation')
    vehicle_registration_number = fields.Integer('vehicle_registration_number')
    controldownloadperiodbegin = fields.Datetime('controldownloadperiodbegin')
    controldownloadperiodend = fields.Datetime('controldownloadperiodend')


class CardEvent(models.Model):
    _name = "card.event"

    begin_time = fields.Datetime('EventBeginTime')
    end_time = fields.Datetime('EventEndTime')
    collection_id = fields.Many2one('card.event.collection', string="card.event.collection")


class CardEventCollection(models.Model):
    _name = "card.event.collection"

    # probably it should be selection field
    type = fields.Integer('Type')
    vehicle_registration_nation = fields.Integer('VehicleRegistrationNation')
    vehicle_registration_number = fields.Char('VehicleRegistrationNumber')

    card_event_record_ids = fields.One2many('card.event', 'collection_id', string="card_event_ids")
    driving_data_id = fields.Many2one('driving.data', string="driving_data")


class CardFault(models.Model):
    _name = "card.fault"

    begin_time = fields.Datetime('EventBeginTime')
    end_time = fields.Datetime('EventEndTime')

    collection_id = fields.Many2one('card.event.collection', string="card.event.collection")


class CardFaultCollection(models.Model):
    _name = "card.fault.collection"

    # probably it should be selection field
    type = fields.Integer('Type')
    vehicle_registration_nation = fields.Integer('VehicleRegistrationNation')
    vehicle_registration_number = fields.Char('VehicleRegistrationNumber')

    card_fault_record_ids = fields.One2many('card.fault', 'collection_id', string="card_event_ids")
    driving_data_id = fields.Many2one('driving.data', string="driving_data")


class ActivityChangeInfo(models.Model):
    _name = "activity.change.info"

    file_offset = fields.Char('file_offset')
    slot = fields.Integer('slot')
    status = fields.Integer('status')
    inserted = fields.Boolean('inserted')
    activity = fields.Char('activity')
    time = fields.Char('time')

    collection_id = fields.Many2one('activity.daily', string="activity.daily")


class CardActivityDailyRecord(models.Model):
    _name = "activity.daily"

    daily_presence_counter = fields.Integer('daily_presence_counter')
    datetime = fields.Datetime('datetime')
    distance = fields.Integer('distance')

    activity_change_info_ids = fields.One2many('activity.change.info', 'collection_id', string="card_event_ids")
    driving_data_id = fields.Many2one('driving.data', string="driving_data")


class VehicleRecord(models.Model):
    _name = "vehicle.record"

    vehicle_odometer_begin = fields.Integer('vehicle_odometer_begin')
    vehicle_odometer_end = fields.Integer('vehicle_odometer_end')

    vehicle_first_use = fields.Datetime('vehicle_first_use')
    vehicle_last_use = fields.Datetime('vehicle_last_use')

    vehicle_registration_nation = fields.Integer('VehicleRegistrationNation')
    vehicle_registration_number = fields.Char('VehicleRegistrationNumber')

    driving_data_id = fields.Many2one('driving.data', string="driving_data")


class PlaceRecord(models.Model):
    _name = "place.record"

    entry_time = fields.Datetime('entry_time')
    entry_type = fields.Integer('entry_type')

    daily_work_period_country_name = fields.Char('daily_work_period_country_name')
    daily_work_period_country = fields.Integer('daily_work_period_country')
    daily_work_period_region = fields.Integer('daily_work_period_region')
    vehicle_odometer_value = fields.Integer('vehicle_odometer_value')

    driving_data_id = fields.Many2one('driving.data', string="driving_data")
