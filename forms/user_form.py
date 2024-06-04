from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField('Ваше имя', validators=[DataRequired()])
    surname = StringField('Ваше фамилия', validators=[DataRequired()])
    email = EmailField('Ваша почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Пароль еще раз', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться', validators=[DataRequired()])


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти', validators=[DataRequired()])


class RegisterStudentForm(FlaskForm):
    name = StringField('Ваше имя', validators=[DataRequired()])
    surname = StringField('Ваше фамилия', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрировать', validators=[DataRequired()])
