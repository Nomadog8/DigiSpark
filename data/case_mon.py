import flask
import sqlite3

from flask import render_template

blueprint = flask.Blueprint(
    'case_mon_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/case_mon')
def get_news():
    cur = sqlite3.connect('db/Clients.sqlite').cursor()

    ans = cur.execute('SELECT * from pc WHERE kind="Мониторы" or kind="Корпуса"').fetchall()

    name = ans[0][1] + ' и ' + ans[-1][1]

    return render_template('products.html', kind=name, products=ans)