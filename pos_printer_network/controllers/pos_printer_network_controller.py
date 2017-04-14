# -*- coding: utf-8 -*-
import logging
import time
from odoo import http


_logger = logging.getLogger(__name__)


try:
    from odoo.addons.hw_escpos.escpos import *
    from odoo.addons.hw_escpos.controllers.main import EscposProxy
    from odoo.addons.hw_escpos.controllers.main import EscposDriver
    from odoo.addons.hw_escpos.escpos.printer import Network
except ImportError:
    EscposProxy = object


class EscposDriver(EscposDriver):
    def run(self):
        timestamp, task, data = self.queue.get(True)
        if len(task) ==2:
            if task[0] == 'network_xml_receipt':
                if timestamp >= time.time() - 1 * 60 * 60:
                    network_printer_proxy = task[1]
                    # print in network printer
                    p = Network(network_printer_proxy)
                    p.receipt(data)
                    self.set_status('connected', 'Connected')
        else:
            driver.push_task(task, data)
            super(EscposDriver, self).run()

driver = EscposDriver()

class EscposProxy(EscposProxy):
    @http.route('/hw_proxy/print_xml_receipt', type='json', auth='none', cors='*')
    def print_xml_receipt(self, receipt, proxy=None):
        if proxy:
            _logger.info('ESC/POS: PRINT XML RECEIPT')
            driver.push_task(['network_xml_receipt', proxy], receipt)
        else:
            super(EscposProxy, self).print_xml_receipt(receipt, proxy)
