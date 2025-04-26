from flask import Flask, render_template, redirect
from data import db_session
from flask_restful import reqparse, Api, Resource
from forms.user import RegisterForm
from data.users import User

app = Flask(__name__)
api = Api(app)
app.config.from_pyfile('config.py')


def start_app():
    db_session.global_init('db/Clients.sqlite')
    app.run(host='127.0.0.1', port=5000)


@app.route('/')
def first_page():
    return render_template('base.html')


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



if __name__ == '__main__':
    start_app()
