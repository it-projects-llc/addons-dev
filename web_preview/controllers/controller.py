from odoo import http
from odoo.http import request
import werkzeug.utils
import werkzeug.wrappers
import base64
from odoo.addons.web.controllers.main import Binary
from odoo.addons.web.controllers.main import binary_content


class Controller(Binary):
    @http.route(['/web/pdf',
        '/web/pdf/<string:xmlid>',
        '/web/pdf/<string:xmlid>/<string:filename>',
        '/web/pdf/<int:id>',
        '/web/pdf/<int:id>/<string:filename>',
        '/web/pdf/<int:id>-<string:unique>',
        '/web/pdf/<int:id>-<string:unique>/<string:filename>',
        '/web/pdf/<string:model>/<int:id>/<string:field>',
        '/web/pdf/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http', auth="public")
    def content_pdf(self, xmlid=None, model='ir.attachment', id=None, field='datas', filename_field='datas_fname', unique=None, filename=None, mimetype=None, download=False):
        status, headers, content = binary_content(xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename, filename_field=filename_field, download=download, mimetype=mimetype, default_mimetype='application/pdf')
        if status == 304:
            response = werkzeug.wrappers.Response(status=status, headers=headers)
        elif status == 301:
            return werkzeug.utils.redirect(content, code=301)
        elif status != 200:
            response = request.not_found()
        else:
            content_base64 = base64.b64decode(content)
            headers.append(('Content-Disposition', 'inline; filename='+str(filename)+'.pdf'))
            response = request.make_response(content_base64, headers)

        response.status_code = status
        return response
