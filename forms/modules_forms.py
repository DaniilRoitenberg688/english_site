from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField, TextAreaField
from wtforms.validators import DataRequired


class CreateModule(FlaskForm):
    name = StringField('Название модуля', validators=[DataRequired()])
    description = StringField('Описание модуля(пару слов)', validators=[DataRequired()])
    submit = SubmitField('Создать', validators=[DataRequired()])


class AddWord(FlaskForm):
    word1 = StringField('Слово' )
    translation1 = StringField('Перевод')

    word2 = StringField('Слово')
    translation2 = StringField('Перевод')

    word3 = StringField('Слово')
    translation3 = StringField('Перевод')

    word4 = StringField('Слово')
    translation4 = StringField('Перевод')

    word5 = StringField('Слово')
    translation5 = StringField('Перевод')

    word6 = StringField('Слово')
    translation6 = StringField('Перевод')

    word7 = StringField('Слово')
    translation7 = StringField('Перевод')

    word8 = StringField('Слово')
    translation8 = StringField('Перевод')

    word9 = StringField('Слово')
    translation9 = StringField('Перевод')

    word10 = StringField('Слово')
    translation10 = StringField('Перевод')

    save_btn = SubmitField('Сохранить')


