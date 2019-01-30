# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models
from odoo.tools import config

try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

config_parser = ConfigParser.ConfigParser()


class OdooToolsConfig(models.AbstractModel):
    _name = 'odoo_backup_sh.odoo_tools_config'

    @classmethod
    def get_values(cls, section, options_list):
        """
        :return dict: option_name: value
        """
        config_parser.read(config.rcfile)
        result = {}
        for option in options_list:
            result[option] = config_parser.get(section, option, fallback=None)
        return result

    @classmethod
    def set_values(cls, section, options_dict):
        for option, value in options_dict.items():
            config_parser.set(section, option, value)
        with open(config.rcfile, 'w') as configfile:
            config_parser.write(configfile)

    @classmethod
    def remove_options(cls, section, options_list):
        config_parser.read(config.rcfile)
        for option in options_list:
            config_parser.remove_option(section, option)
        with open(config.rcfile, 'w') as configfile:
            config_parser.write(configfile)
