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
        file = request.files.get('file')
        if file is None or not file.filename:
            return render_template('index.html', message=u'Найден пустой файл'), 400
        try:
            book = xlrd.open_workbook(file_contents=file.read(), formatting_info=True, on_demand=True)
        except Exception:
            return render_template('index.html', message=u'Ошибка чтения файла. Файл должен быть формата Excel 97-2003 (xls)'), 400
        newbook, _ = xls.copy(book)

        try:
            sheet = book.sheet_by_index(0)
            newbook_sheet = newbook.get_sheet(0)
        except:
            return render_template('index.html', message=u'Ошибка чтения данных со второго листа'), 400
        url_ind = -1
        for j in range(sheet.ncols):
            if sheet.cell(0, j).value == 'URL':
                url_ind = j
        if url_ind == -1:
            return render_template('index.html', message=u'Не найдена колонка со ссылками'), 400
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
                d = 0
                while key in keys:
                    key = hashlib.sha224(u'%s%s' % (url, d)).hexdigest()[:self.KEY_LENGTH]
                    i += d
                keys.add(key)
                new_url = Url(url=url, key=key)
                db.session.add(new_url)
            else:
                key = urls[url]
            newbook_sheet.write(i, url_ind + 1, u'www.%s/%s' % (request.host, key))

        db.session.flush()
        db.session.commit()

        f = StringIO.StringIO()
        newbook.save(f)
        response = Response(f.getvalue(), mimetype='application/xls')
        response.headers['Content-Disposition'] = u'attachment; filename=%s' % file.filename
        return response


class RedirectView(MethodView):
    def get(self, key):
        try:
            url = Url.query.filter(Url.key == key).one().url
            if -1 < url.find('?') < len(url) - 1 and not request.args:
                return redirect('?'.join([request.url, url.split('?')[-1]]))
        except NoResultFound:
            url = 'https://pmclub.ru/login'
        return render_template('redirect-page.html', url=url)

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
