from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField, TextAreaField
from wtforms.validators import DataRequired

class CreateModule(FlaskForm):
    name = StringField('Название модуля', validators=[DataRequired()])
    description = StringField('Описание модуля(пару слов)', validators=[DataRequired()])
    submit = SubmitField('Создать', validators=[DataRequired()])