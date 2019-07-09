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

    card_extended_serial_number = fields.Integer('CardExtendedSerialNumber')
    manufacturer_code = fields.Integer('ManufacturerCode')
    month = fields.Integer('Month')
    year = fields.Integer('Year')

    card_approval_number = fields.Char('CardApprovalNumber')
    card_personaliser_id = fields.Integer('CardPersonaliserId')
    embedder_ic_assembler_id = fields.Char('EmbedderIcAssemblerId')
    ic_identifier = fields.Integer('Ic Identifier')

    # cardchipidentification
    ic_serial_number = fields.Char('IcSerialNumber')
    ic_manufacturing_reference = fields.Char('IcManufacturingReferences')

    # card_application_identification
    type = fields.Integer('Type')
    version = fields.Integer('Version')
    no_of_events_per_type = fields.Integer('NoOfEventsPerType')
    no_of_faults_per_type = fields.Integer('NoOfFaultsPerType')
    activity_structure_length = fields.Integer('ActivityStructureLength')
    no_of_card_vehicle_records = fields.Integer('NoOfCardVehicleRecords')
    no_of_card_place_records = fields.Integer('NoOfCardPlaceRecords')

    # cardidentification
    card_issuing_member_state = fields.Integer('CardIssuingMemberState')

    card_number = fields.Char('CardNumber')
    renewal_index = fields.Integer('RenewalIndex')
    replacement_index = fields.Integer('ReplacementIndex')

    card_issuing_authority_name = fields.Char('CardIssuingAuthorityName')
    card_issue_date = fields.Datetime('CardIssueDate')
    card_validity_begin = fields.Datetime('CardValidityBegin')
    card_expiry_date = fields.Datetime('CardExpiryDate')

    # CardEventCollection
    card_event_collection_ids = fields.One2many('card.event.collection', 'driving_data_id',
                                                string="card_event_collection_ids")
    # CardFaultCollection
    card_fault_collection_ids = fields.One2many('card.fault.collection', 'driving_data_id',
                                                string="card_fault_collection_ids")
    # DriverActivityData
    activity_daily_ids = fields.One2many('activity.daily', 'driving_data_id',
                                         string="activity.daily")
    # CardVehiclesUsed
    vehicle_pointer_newest_record = fields.Integer('vehicle_pointer_newest_record')
    vehicle_record_ids = fields.One2many('vehicle.record', 'driving_data_id',
                                         string="vehicle.record")
    # CardPlaceDailyWorkPeriod
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
    # SpecificConditions
    specific_condition_ids = fields.One2many('specific.condition', 'driving_data_id',
                                             string="place_daily_work_ids")
    # CardCertificate
    card_certificate_signature = fields.Char('Signature')
    card_certificate_public_key_remainder = fields.Char('public_key_reminder')
    # CertificationAuthorityReference
    card_certificate_authority_nation = fields.Integer('nation')
    card_certificate_authority_nation_name = fields.Char('nation_name')
    card_certificate_authority_nation_code = fields.Char('authority_nation_code')
    card_certificate_authority_additional_info = fields.Char('authority_additional_info')
    card_certificate_authority_serial_number = fields.Integer('authority_serial_number')
    card_certificate_authority_ca_identifier = fields.Integer('authority_ca_identifier')

    # CaCertificate
    ca_certificate_signature = fields.Char('Signature')
    ca_certificate_public_key_remainder = fields.Char('public_key_reminder')
    # CertificationAuthorityReference
    ca_certificate_authority_nation = fields.Integer('nation')
    ca_certificate_authority_nation_name = fields.Char('nation_name')
    ca_certificate_authority_nation_code = fields.Char('authority_nation_code')
    ca_certificate_authority_additional_info = fields.Char('authority_additional_info')
    ca_certificate_authority_serial_number = fields.Integer('authority_serial_number')
    ca_certificate_authority_ca_identifier = fields.Integer('authority_ca_identifier')


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


class SpecificCondition(models.Model):
    _name = "specific.condition"

    entry_time = fields.Datetime('entry_time')
    specific_condition_type = fields.Integer('Specific Condition Type')

    driving_data_id = fields.Many2one('driving.data', string="driving_data")
