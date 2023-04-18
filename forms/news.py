import wtforms
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Личное")
    price = StringField('Цена')
    image = wtforms.FileField('Изображение')
    type_k = wtforms.SelectField('Категория товара', choices=("Iphone", "Macbook"))
    submit = SubmitField('Применить')
    is_private = BooleanField("Личное")