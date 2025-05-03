from flask import Flask, render_template, redirect
from flask_login import login_user, login_required, logout_user, LoginManager
from flask_restful import Api

from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm
from flask import request

app = Flask(__name__)
api = Api(app)
app.config.from_pyfile('config.py')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def start_app():
    db_session.global_init('db/Clients.sqlite')
    app.run(host='127.0.0.1', port=5000)


@app.route('/')
def first_page():
    return render_template('base.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    return redirect('/contacts')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():

        db_sess = db_session.create_session()

        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message='Пользователь с такой почтой уже зарегестрирован')

        user = User(
            email=form.email.data,
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            phone_number=form.phone_number.data
        )

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')

        return render_template('login.html', message='Неправильный логин или пароль', form=form)

    return render_template('login.html', title='Авторизация', form=form)


if __name__ == '__main__':
    start_app()
