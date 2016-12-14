# coding: utf-8
import hashlib
import StringIO
import sys

from flask import Flask, request, render_template, Response, abort, redirect
from flask.views import MethodView
from flask_migrate import Migrate
import xlwt
import xlrd
from sqlalchemy.orm.exc import NoResultFound

import settings
from models import db, Url
import xls

app = Flask(__name__)
app.config.from_object(settings.Config)
db.init_app(app)
migrate = Migrate(app, db)


class UrlShorterView(MethodView):
    KEY_LENGTH = 8

    def get(self):
        return render_template('index.html')

    def post(self):
        file = request.files['file']
        book = xlrd.open_workbook(file_contents=file.read(), formatting_info=True, on_demand=True)
        newbook, _ = xls.copy(book)

        sheet = book.sheet_by_index(1)
        newbook_sheet = newbook.get_sheet(1)
        url_ind = -1
        for j in range(sheet.ncols):
            if sheet.cell(0, j).value == 'URL':
                url_ind = j
        if url_ind == -1:
            return render_template('error.html', message=u'Не найдена колонка со ссылками'), 400
        keys = set()
        urls = {}
        for x in Url.query.all():
            keys.add(x.key)
            urls[x.url] = x.key
        for i in range(sheet.nrows):
            if i == 0:
                newbook_sheet.write(i, url_ind + 1, 'SHORT URL')
                continue
            url = unicode(sheet.cell(i, url_ind).value)
            if not url:
                continue
            if url not in urls:
                key = hashlib.sha224(str(url)).hexdigest()[:self.KEY_LENGTH]
                i = 0
                while key in keys:
                    key = hashlib.sha224(u'%s%s' % (url, i)).hexdigest()[:self.KEY_LENGTH]
                    i += 1
                keys.add(key)
                new_url = Url(url=url, key=key)
                db.session.add(new_url)
            else:
                key = urls[url]
            newbook_sheet.write(i, url_ind + 1, u'%s%s' % (request.base_url, key))

        db.session.flush()
        db.session.commit()

        f = StringIO.StringIO()
        newbook.save(f)
        response = Response(f.getvalue(), mimetype='application/xls')
        response.headers['Content-Disposition'] = 'attachment; filename=file.xls'
        return response


class RedirectView(MethodView):
    def get(self, key):
        try:
            url = Url.query.filter(Url.key == key).one()
        except NoResultFound:
            raise abort(404)
        return redirect(url.url)

app.add_url_rule('/', view_func=UrlShorterView.as_view('url-shorter'))
app.add_url_rule('/<string:key>', view_func=RedirectView.as_view('key-redirect'))


if not app.debug:
    import logging
    handler = logging.FileHandler(app.config['LOG_PATH'])
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5090, debug=True)
