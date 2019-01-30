# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging

try:
    import boto3
    import botocore
except ImportError as err:
    logging.getLogger(__name__).debug(err)

from odoo import exceptions, models
from odoo.tools.translate import _
from .config import OdooToolsConfig


_logger = logging.getLogger(__name__)


def access_control(origin_method):
    def wrapped(self, *args, **kwargs):
        try:
            return origin_method(self, *args, **kwargs)
        except botocore.exceptions.ClientError as client_error:
            if client_error.response['Error']['Code'] == 'InvalidAccessKeyId':
                OdooToolsConfig.remove_options('options', ['amazon_access_key_id', 'amazon_secret_access_key'])
                return {'reload_page': True}
            else:
                raise exceptions.ValidationError(_(
                    "Amazon Web Services error: " + client_error.response['Error']['Message']))
    return wrapped


class CloudStorage(models.AbstractModel):
    _name = 'odoo_backup_sh.cloud_storage'

    def get_amazon_s3_client(self, cloud_params):
        s3_client = boto3.client('s3', aws_access_key_id=cloud_params['amazon_access_key_id'],
                                 aws_secret_access_key=cloud_params['amazon_secret_access_key'])
        return s3_client

    @access_control
    def get_backup_list(self, cloud_params):
        amazon_s3_client = self.get_amazon_s3_client(cloud_params)
        user_dir_name = '%s/' % cloud_params['odoo_oauth_uid']
        list_objects = amazon_s3_client.list_objects_v2(
            Bucket=cloud_params['amazon_bucket_name'], Prefix=user_dir_name, Delimiter='/')
        return {'backup_list': [
            obj['Key'][len(user_dir_name):] for obj in list_objects.get('Contents', {}) if obj.get('Size')]}

    @access_control
    def get_object(self, cloud_params, obj_name):
        amazon_s3_client = self.get_amazon_s3_client(cloud_params)
        object_path = '%s/%s' % (cloud_params['odoo_oauth_uid'], obj_name)
        return amazon_s3_client.get_object(Bucket=cloud_params['amazon_bucket_name'], Key=object_path)

    @access_control
    def put_object(self, cloud_params, obj, obj_path):
        amazon_s3_client = self.get_amazon_s3_client(cloud_params)
        amazon_s3_client.put_object(Body=obj, Bucket=cloud_params['amazon_bucket_name'], Key=obj_path)
        _logger.info('Following backup object have been put in the remote storage: %s' % obj_path)

    @access_control
    def delete_objects(self, cloud_params, objs):
        amazon_s3_client = self.get_amazon_s3_client(cloud_params)
        amazon_s3_client.delete_objects(
            Bucket=cloud_params['amazon_bucket_name'], Delete={'Objects': objs})
        objects_names = [obj['Key'] for obj in objs]
        _logger.info(
            'Following backup objects have been deleted from the remote storage: %s' % ', '.join(objects_names))
