from flask import Flask, render_template
from data.db_session import global_init, create_session

app = Flask(__name__)
app.config.from_pyfile('config.py')


def start_app():
    global_init('db/Clients.db')
    app.run(host='127.0.0.1', port=5000)


@app.route('/')
def first_page():
    return render_template('base.html')


if __name__ == '__main__':
    start_app()