from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, IntegerField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo


class RegisterForm(FlaskForm):

    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пороль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    age = IntegerField('Возраст', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    phone_number = StringField('Телефон', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class LoginForm(FlaskForm):

    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Отправить')