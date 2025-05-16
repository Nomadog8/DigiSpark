from flask import Flask, render_template, redirect
from flask import request
from flask_login import login_user, login_required, logout_user, LoginManager, current_user
import sqlite3

from data import db_session, cards_api, procc_api, bp_api, disk_api, culler_api, ram_api, board_api, keyboards, \
    case_mon, solids_api
from data.contacts import Contacts
from data.users import User
from data.orders import Order
from forms.user import RegisterForm, LoginForm

app = Flask(__name__)
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
    app.register_blueprint(cards_api.blueprint)
    app.register_blueprint(culler_api.blueprint)
    app.register_blueprint(procc_api.blueprint)
    app.register_blueprint(bp_api.blueprint)
    app.register_blueprint(ram_api.blueprint)
    app.register_blueprint(disk_api.blueprint)
    app.register_blueprint(board_api.blueprint)
    app.register_blueprint(case_mon.blueprint)
    app.register_blueprint(keyboards.blueprint)
    app.register_blueprint(solids_api.blueprint)
    app.run(host='127.0.0.1', port=5000)


def check_telephone_number(number):
    return sum(1 for k in number if k in '0123456789')


@app.route('/')
def first_page():
    return render_template('home_first.html')


@app.route('/radio')
def second_page():
    return render_template('home_second.html')


@app.route('/info')
def info():
    return render_template('info.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.errorhandler(401)
def error_401(error):
    return render_template('error401.html')


@app.route('/empty')
def empty():
    return render_template('empty.html')


@app.route('/add/<product_id>')
@login_required
def add_to_basket(product_id):
    db_sess = db_session.create_session()

    user = db_sess.query(User).filter(User.id == current_user.id).first()

    if not user.basket:
        user.basket = str(product_id)
    else:
        user.basket += f', {product_id}'

    db_sess.commit()

    return redirect('/')



@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    db_sess = db_session.create_session()
    contact = Contacts(
        name=name,
        email=email,
        subject=subject,
        message=message,
    )
    db_sess.add(contact)
    db_sess.commit()
    return redirect('/contacts')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():

        db_sess = db_session.create_session()

        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message='Пользователь с такой почтой уже зарегестрирован')

        if check_telephone_number(form.phone_number.data) != 11:
            return render_template('register.html', title='Регистрация', form=form,
                                   message='Неправильно набранный номер')

        if len(form.password.data.strip()) < 9:
            return render_template('register.html', title='Регистрация', form=form,
                                   message='Пароль должен содержать не менее 9 символов')

        if form.password.data.strip().isdigit():
            return render_template('register.html', title='Регистрация', form=form,
                                   message='Пароль должен содержать буквы')

        if form.password.data.strip().isalpha():
            return render_template('register.html', title='Регистрация', form=form,
                                   message='Пароль должен содержать цифры')

        if not (100 >= form.age.data >= 7):
            return render_template('register.html', title='Регистрация', form=form,
                                   message='Неверно указан возраст')

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


@app.route('/basket')
def basket():
    db_sess = db_session.create_session()

    user = db_sess.query(User).filter(User.id == current_user.id).first().basket

    if user:

        cur = sqlite3.connect('db/Clients.sqlite').cursor()

        current_basket = []

        for k in list(map(int, user.split(', '))):
            prod = list(cur.execute('SELECT * FROM pc WHERE id = ?', (k,)).fetchone())

            prod.append(user.split(', ').count(str(k)))

            current_basket.append(prod)

        total_price = sum(k[-2] for k in current_basket)

        current_basket = [tuple(k) for k in current_basket]

        return render_template('basket.html', total=total_price, basket=set(current_basket))

    else:
        return render_template('empty_basket.html')


@app.route('/delete/<product_id>')
def delete_from_basket(product_id):
    db_sess = db_session.create_session()

    user = db_sess.query(User).filter(User.id == current_user.id).first()
    basket_r = user.basket.split(', ')
    print(product_id)

    basket_r.remove(str(product_id))

    user.basket = ', '.join(basket_r)

    db_sess.commit()

    return redirect('/basket')


@app.route('/order')
def make_order():
    db_sess = db_session.create_session()

    user = db_sess.query(User).filter(User.id == current_user.id).first().basket

    cur = sqlite3.connect('db/Clients.sqlite').cursor()

    current_basket = []

    for k in list(map(int, user.split(', '))):
        prod = cur.execute('SELECT * FROM pc WHERE id = ?', (k,)).fetchone()

        current_basket.append(prod[2])

    current_basket = ', '.join(current_basket)

    order = Order(
        order=current_basket,
        user_id=current_user.id,
    )

    db_sess.add(order)
    db_sess.commit()

    return redirect('/basket')


if __name__ == '__main__':
    start_app()