import wtforms
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = StringField("Мелкий информационный тест на карточке товара")
    is_private = BooleanField("Личное")
    price = StringField('Цена')

    image = wtforms.FileField('Изображения товара')
    cover = wtforms.FileField('Обложка товара')

    type_k = wtforms.SelectField('Категория товара', choices=("Iphone", "Macbook", "Ipad",
                                                              "AirPods", "Apple Watch", "Mac"))
    color = StringField('Цвет')
    size = StringField('Объем памяти (Писать только через пробел)')

    desc = TextAreaField('Описание продукта')
    spec = TextAreaField('Спецификация продукта (Каждую спецификацию через точку с запятой ";")')

    submit = SubmitField('Применить')
    is_private = BooleanField("Личное")