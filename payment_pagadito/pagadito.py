# -*- coding: utf-8 -*-
# Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging
import urllib
import urllib2
import json


_logger = logging.getLogger(__name__)

# from WSPG section of Pagadito docs
# https://dev.pagadito.com/index.php?mod=docs&hac=wspg

WSPG_URL_SANDBOX = "https://sandbox.pagadito.com/comercios/wspg/charges.php"
WSPG_URL = "https://comercios.pagadito.com/wspg/charges.php"


PG_SUCCESS = "PG1001"  #	Connection successful.	X	X	Conexión exitosa del Pagadito Comercio con el WSPG.
# PG_ = "PG1002"  #	Transaction register successful.	X	X	La transacción enviada por el Pagadito Comercio fue registrada correctamente por el WSPG.
# PG_ = "PG1003"  #	Transaction status.	X	X	Ha sido procesada correctamente la petición de estado de transacción.
# PG_ = "PG1004"  #	Exchange Rate.	X	X	Ha sido procesada correctamente la petición de tasa de cambio.
# PG_ = "PG2001"  #	Incomplete data.		X	El Pagadito Comercio no envió todos los parámetros necesarios.
# PG_ = "PG2002"  #	Incorrect format data.		X	El formato de los datos enviados por el Pagadito Comercio no es el correcto.
# PG_ = "PG3001"  #	Connection couldn't be established.		X	Las credenciales de conexión no están registradas.
# PG_ = "PG3002"  #	We're sorry. An error has occurred.		X	Un error no controlado por el WSPG ocurrió y no se ha podido procesar la petición.
# PG_ = "PG3003"  #	Unregistered transaction.		X	La transacción solicitada no ha sido registrada.
# PG_ = "PG3004"  #	Transaction amount doesn't match with calculated amount.		X	La suma de los productos de la cantidad y el precio de los detalles no es igual al monto de la trasacción.
# PG_ = "PG3005"  #	Connection is disabled.		X	El Pagadito Comercio ha sido validado, pero la conexión se encuentra deshabilitada.
# PG_ = "PG3006"  #	Amount has exceeded the maximum.		X	La transacción ha sido denegada debido a que excede el monto máximo por transacción.
# PG_ = "PG3007"  #	Denied access.		X	El acceso ha sido denegado, debido a que el token no es válido.
# PG_ = "PG3008"  #	Currency not supported.		X	La moneda solicitada no es soportada por Pagadito.
# PG_ = "PG3009"  #	Amount is lower than the minimum allowed.		X	La transacción ha sido denegada debido a que el monto es menor al mínimo permitido.

STATUS_REGISTERED = "REGISTERED"  # La transacción ha sido registrada correctamente en Pagadito, pero aún se encuentra en proceso. En este punto, el cobro aún no ha sido realizado.
STATUS_COMPLETED = "COMPLETED"  # X	X	La transacción ha sido procesada correctamente en Pagadito. En este punto el cobro ya ha sido realizado.
STATUS_VERIFYING = "VERIFYING"  # X	X	La transacción ha sido procesada en Pagadito, pero ha quedado en verificación. En este punto el cobro ha quedado en validación administrativa. Posteriormente, la transacción puede marcarse como válida o denegada; por lo que se debe monitorear mediante esta función hasta que su estado cambie a COMPLETED o REVOKED.
STATUS_REVOKED = "REVOKED"  # X	X	La transacción en estado VERIFYING ha sido denegada por Pagadito. En este punto el cobro ya ha sido cancelado.
STATUS_FAILED = "FAILED"  # La transacción ha sido registrada correctamente en Pagadito, pero no pudo ser procesada. En este punto, el cobro aún no ha sido realizado.
STATUS_CANCELED = "CANCELED"  # La transacción ha sido cancelada por el usuario en Pagadito, la transacción tiene este estado cuando el usuario hace click en el enlace de "regresar al comercio" en la pantalla de pago de Pagadito.
STATUS_EXPIRED = "EXPIRED"  # La transacción ha expirado en Pagadito, la transacción tiene este estado cuando se termina el tiempo para completar la transacción por parte del usuario en Pagadito, el tiempo para completar la transacción en Pagadito por parte del usuario es de 10 minutos. Pagadito también se encarga de poner estado EXPIRED a todas las transacciones que no fueron completas, debido a que el usuario salio de manera inesperada del proceso de pago, por ejemplo cerrando la ventana del navegador.

# Don't ask me what the hell is that -- I got it from SDK files in  "Descargas" section of the docs
OP_CONNECT = "f3f191ce3326905ff4403bb05b0de150"
OP_EXEC_TRANS = "41216f8caf94aaa598db137e36d4673e"
OP_GET_STATUS = "0b50820c65b0de71ce78f6221a5cf876"
OP_GET_EXCHANGE_RATE = "da6b597cfcd0daf129287758b3c73b76"


def call(operation, params, sandbox=True):
    url = WSPG_URL_SANDBOX if sandbox else WSPG_URL
    params['operation'] = operation
    params['format_return'] = 'json'

    params_encoded = urllib.urlencode(params)
    _logger.debug('Sending request:\n%s\n%s\n%s', url, params, params_encoded)
    res = urllib2.urlopen(url, params_encoded)
    _logger.debug('Raw response:\n%s', res)

    res_json = json.load(res)
    return res_json
