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

    card_extended_serial_number = fields.Integer('Card ExtendedSerial Number')
    manufacturer_code = fields.Integer('Manufacturer Code')
    month = fields.Integer('Month')
    year = fields.Integer('Year')

    card_approval_number = fields.Char('Card Approval Number')
    card_personaliser_id = fields.Integer('Card Personaliser Id')
    embedder_ic_assembler_id = fields.Char('Embedder Ic Assembler Id')
    ic_identifier = fields.Integer('Ic Identifier')

    # cardchipidentification
    ic_serial_number = fields.Char('Ic Serial Number')
    ic_manufacturing_reference = fields.Char('Ic Manufacturing References')

    # card_application_identification
    type = fields.Integer('Type')
    version = fields.Integer('Version')
    no_of_events_per_type = fields.Integer('No Of Events Per Type')
    no_of_faults_per_type = fields.Integer('No Of Faults Per Type')
    activity_structure_length = fields.Integer('Activity Structure Length')
    no_of_card_vehicle_records = fields.Integer('No Of Card Vehicle Records')
    no_of_card_place_records = fields.Integer('No Of Card Place Records')

    # cardidentification
    card_issuing_member_state = fields.Integer('Card Issuing Member State')

    card_number = fields.Char('Card Number')
    renewal_index = fields.Integer('Renewal Index')
    replacement_index = fields.Integer('Replacement Index')

    card_issuing_authority_name = fields.Char('Card Issuing Authority Name')
    card_issue_date = fields.Datetime('Card Issue Date')
    card_validity_begin = fields.Datetime('Card Validity Begin')
    card_expiry_date = fields.Datetime('Card Expiry Date')

    # CardEventCollection
    card_event_collection_ids = fields.One2many('card.event.collection', 'driving_data_id',
                                                string="Card Event Record Collection")
    # CardFaultCollection
    card_fault_collection_ids = fields.One2many('card.fault.collection', 'driving_data_id',
                                                string="Card Fault Record Collection")
    # DriverActivityData
    activity_daily_ids = fields.One2many('activity.daily', 'driving_data_id',
                                         string="Driver Activity Data")
    # CardVehiclesUsed
    vehicle_pointer_newest_record = fields.Integer('VehiclePointerNewestRecord')
    vehicle_record_ids = fields.One2many('vehicle.record', 'driving_data_id',
                                         string="Card Vehicle Records")
    # CardPlaceDailyWorkPeriod
    place_pointer_newest_record = fields.Integer('PlacePointerNewestRecord')
    place_daily_work_ids = fields.One2many('place.record', 'driving_data_id',
                                           string="Place Records")
    # CardControlActivityDataRecord
    control_type = fields.Integer('Control Type')
    control_time = fields.Datetime('Control Time')
    control_card_number_type = fields.Integer('Control Card Number Type')
    control_card_number_issuingmemberstate = fields.Integer('Control Card Number Issuing Member State')
    control_card_number_replacementindex = fields.Integer('Control Card Number Replacement Index')
    control_card_number_renewalindex = fields.Integer('Control Card Number Renewal Index')
    vehicle_registration_nation = fields.Integer('Vehicle Registration Nation')
    vehicle_registration_number = fields.Integer('Vehicle Registration Number')
    control_download_period_begin = fields.Datetime('Control Download Period Begin')
    control_download_period_end = fields.Datetime('Control Download Period End')
    # SpecificConditions
    specific_condition_ids = fields.One2many('specific.condition', 'driving_data_id',
                                             string="Specific Conditions")
    # CardCertificate
    card_certificate_signature = fields.Char('Signature')
    card_certificate_public_key_remainder = fields.Char('Public Key Remainder')
    # CertificationAuthorityReference
    card_certificate_authority_nation = fields.Integer('Nation')
    card_certificate_authority_nation_name = fields.Char('Nation Name')
    card_certificate_authority_nation_code = fields.Char('Nation Code')
    card_certificate_authority_additional_info = fields.Char('Additional Info')
    card_certificate_authority_serial_number = fields.Integer('Serial Number')
    card_certificate_authority_ca_identifier = fields.Integer('Ca Identifier')

    # CaCertificate
    ca_certificate_signature = fields.Char('Signature')
    ca_certificate_public_key_remainder = fields.Char('Public Key Remainder')
    # CertificationAuthorityReference
    ca_certificate_authority_nation = fields.Integer('Nation')
    ca_certificate_authority_nation_name = fields.Char('Nation Name')
    ca_certificate_authority_nation_code = fields.Char('Nation Code')
    ca_certificate_authority_additional_info = fields.Char('Additional Info')
    ca_certificate_authority_serial_number = fields.Integer('Serial Number')
    ca_certificate_authority_ca_identifier = fields.Integer('Ca Identifier')


class CardEvent(models.Model):
    _name = "card.event"

    begin_time = fields.Datetime('Event Begin Time')
    end_time = fields.Datetime('Event End Time')
    collection_id = fields.Many2one('card.event.collection', string="Card Event Record Collection")


class CardEventCollection(models.Model):
    _name = "card.event.collection"

    # probably it should be selection field
    type = fields.Integer('Type')
    vehicle_registration_nation = fields.Integer('Vehicle Registration Nation')
    vehicle_registration_number = fields.Char('Vehicle Registration Number')

    card_event_record_ids = fields.One2many('card.event', 'collection_id', string="Card Event Records")
    driving_data_id = fields.Many2one('driving.data', string="Driver Data")


class CardFault(models.Model):
    _name = "card.fault"

    begin_time = fields.Datetime('Event Begin Time')
    end_time = fields.Datetime('Event EndT ime')

    collection_id = fields.Many2one('card.fault.collection', string="Card Fault Record Collection")


class CardFaultCollection(models.Model):
    _name = "card.fault.collection"

    # probably it should be selection field
    type = fields.Integer('Type')
    vehicle_registration_nation = fields.Integer('Vehicle Registration Nation')
    vehicle_registration_number = fields.Char('Vehicle Registration Number')

    card_fault_record_ids = fields.One2many('card.fault', 'collection_id', string="Card Fault Records")
    driving_data_id = fields.Many2one('driving.data', string="Driver Data")


class ActivityChangeInfo(models.Model):
    _name = "activity.change.info"

    file_offset = fields.Char('File Offset')
    slot = fields.Integer('Slot')
    status = fields.Integer('Status')
    inserted = fields.Boolean('Inserted')
    activity = fields.Char('Activity')
    time = fields.Char('Time')

    collection_id = fields.Many2one('activity.daily', string="Card Activity Daily Record")


class CardActivityDailyRecord(models.Model):
    _name = "activity.daily"

    daily_presence_counter = fields.Integer('Daily Presence Counter')
    datetime = fields.Datetime('Datetime')
    distance = fields.Integer('Distance')

    activity_change_info_ids = fields.One2many('activity.change.info', 'collection_id', string="Activity Change Info")
    driving_data_id = fields.Many2one('driving.data', string="Driver Data")


class VehicleRecord(models.Model):
    _name = "vehicle.record"

    vehicle_odometer_begin = fields.Integer('Vehicle Odometer Begin')
    vehicle_odometer_end = fields.Integer('Vehicle Odometer End')

    vehicle_first_use = fields.Datetime('Vehicle First Use')
    vehicle_last_use = fields.Datetime('Vehicle Last Use')

    vehicle_registration_nation = fields.Integer('Vehicle Registration Nation')
    vehicle_registration_number = fields.Char('Vehicle Registration Number')

    driving_data_id = fields.Many2one('driving.data', string="Driver Data")


class PlaceRecord(models.Model):
    _name = "place.record"

    entry_time = fields.Datetime('Entry Time')
    entry_type = fields.Integer('Entry Type')

    daily_work_period_country_name = fields.Char('Daily Work Period Country Name')
    daily_work_period_country = fields.Integer('Daily Work Period Country')
    daily_work_period_region = fields.Integer('Daily Work Period Region')
    vehicle_odometer_value = fields.Integer('Vehicle Odometer Value')

    driving_data_id = fields.Many2one('driving.data', string="Driver Data")


class SpecificCondition(models.Model):
    _name = "specific.condition"

    entry_time = fields.Datetime('Entry Time')
    specific_condition_type = fields.Integer('Specific Condition Type')

    driving_data_id = fields.Many2one('driving.data', string="Driver Data")
