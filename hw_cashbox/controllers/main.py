# -*- coding: utf-8 -*-
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from openerp import http
import time
import logging

try:
    from openerp.addons.hw_escpos.escpos.escpos import Escpos
    from openerp.addons.hw_escpos.escpos import escpos
    from openerp.addons.hw_escpos.escpos.printer import *
    from openerp.addons.hw_escpos.escpos.exceptions import NoDeviceError, HandleDeviceError, TicketNotPrinted, NoStatusError
    from openerp.addons.hw_escpos.controllers.main import EscposProxy
    from openerp.addons.hw_escpos.controllers.main import EscposDriver
    from openerp.addons.hw_escpos.escpos.printer import Network
    import openerp.addons.hw_proxy.controllers.main as hw_proxy
except ImportError:
    EscposProxy = object
    EscposDriver = object
    Escpos = object

_logger = logging.getLogger(__name__)


class EscposCashboxProxy(EscposProxy):

    @http.route('/hw_proxy/open_cashbox_pin2', type='json', auth='none', cors='*')
    def open_cashbox_pin2(self):
        driver = EscposCashboxDriver()
        driver.push_task('cashbox2')

    @http.route('/hw_proxy/open_cashbox_pin5', type='json', auth='none', cors='*')
    def open_cashbox_pin5(self):
        driver = EscposCashboxDriver()
        driver.push_task('cashbox5')


class EscposCashboxDriver(EscposDriver):

    def run(self):
        printer = None
        try:
            escpos
        except Exception as e:
            _logger.error("----------{}".format(str(e)))
            return
        if not escpos:
            _logger.error('ESC/POS cannot initialize, please verify system dependencies.')
            return
        while True:
            try:
                error = True
                timestamp, task, data = self.queue.get(True)

                printer = self.get_escpos_printer()
                if printer is None:
                    if task != 'status':
                        self.queue.put((timestamp, task, data))
                    error = False
                    time.sleep(5)
                    continue
                elif task == 'receipt':
                    if timestamp >= time.time() - 1 * 60 * 60:
                        self.print_receipt_body(printer, data)
                        printer.cut()
                elif task == 'xml_receipt':
                    if timestamp >= time.time() - 1 * 60 * 60:
                        printer.receipt(data)
                elif task == 'cashbox2':
                    if timestamp >= time.time() - 12:
                        self.open_cashbox2(printer)
                elif task == 'cashbox5':
                    if timestamp >= time.time() - 12:
                        self.open_cashbox5(printer)
                elif task == 'cashbox':
                    if timestamp >= time.time() - 12:
                        self.open_cashbox(printer)
                elif task == 'printstatus':
                    self.print_status(printer)
                elif task == 'status':
                    pass
                error = False

            except NoDeviceError as e:
                print("No device found %s" % e)
            except HandleDeviceError as e:
                print("Impossible to handle the device due to previous error %s" % e)
            except TicketNotPrinted as e:
                print("The ticket does not seems to have been fully printed %s" % e)
            except NoStatusError as e:
                print("Impossible to get the status of the printer %s" % e)
            except Exception as e:
                self.set_status('error', e)
                _logger.exception()
            finally:
                if error:
                    self.queue.put((timestamp, task, data))
                if printer:
                    printer.close()

    def open_cashbox2(self, printer):
        printer.cashdraw(2)

    def open_cashbox5(self, printer):
        printer.cashdraw(5)
