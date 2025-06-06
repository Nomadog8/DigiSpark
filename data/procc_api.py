import flask
import sqlite3

from flask import render_template

blueprint = flask.Blueprint(
    'procc_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/procc')
def get_news():
    cur = sqlite3.connect('db/Clients.sqlite').cursor()

    ans = cur.execute('SELECT * from pc WHERE kind="Процессор"').fetchall()

    name = ans[0][1]

    return render_template('products.html', kind=name, products=ans)