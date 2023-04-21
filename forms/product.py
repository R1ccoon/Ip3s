import wtforms
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_uploads import UploadSet, IMAGES


class ProductForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = StringField("Мелкий информационный тест на карточке товара")
    is_private = BooleanField("Личное")
    price = StringField('Цена')

    cover = FileField(
        'Обложка товара (Для корректного отображения товара рекомендуется '
        'использовать изображение формата 4:3 и размером 600x450)',
        validators=[
            FileAllowed(UploadSet('photos', IMAGES), 'Only image'),
            FileRequired('Not empty'),
        ]
    )
    images = wtforms.FileField(
        'Изобрадения товара',
        validators=[
            FileAllowed(UploadSet('photos', IMAGES), 'Only image'),
            FileRequired('Not empty'),
        ])

    type_k = wtforms.SelectField('Категория товара', choices=("Iphone", "Macbook", "Ipad",
                                                              "AirPods", "Apple Watch", "Mac"))
    color = StringField('Цвет')
    size = StringField('Объем памяти (Писать только через пробел)')

    desc = TextAreaField('Описание продукта')
    spec = TextAreaField('Спецификация продукта (Каждую спецификацию через точку с запятой ";")')

    submit = SubmitField('Применить')
    is_private = BooleanField("Личное")
