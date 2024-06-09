from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class TestWord(FlaskForm):
    answer = StringField('Введите ваш ответ', validators=[DataRequired()])
    submit = SubmitField('Проверить', validators=[DataRequired()])
