from os import abort

from flask import Flask, render_template, redirect, make_response, request, send_from_directory
from flask_uploads import UploadSet, IMAGES, configure_uploads

from forms.product import ProductForm
from forms.user import RegisterForm, LoginForm

from data import db_session
from data.users import User
from data.news import News
import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = '40d1649f-0493-4b70-98ba-98533de7710b'
app.config['UPLOADED_PHOTOS_DEST'] = '/home/ip3s/.virtualenvs/venv/ip3s/static/img'

DB_PATH = "/home/ip3s/.virtualenvs/venv/ip3s/db/blogs.db"

db_session.global_init(DB_PATH)

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'reqister'

a = 0


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init(DB_PATH)


@app.route("/")
def index():
    db_sess = db_session.create_session()

    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)

    return render_template("index.html", news=news, title='Главная')


@app.route("/shop/<string:filtr>")
def shop(filtr):
    m = filtr.split('.')

    db_sess = db_session.create_session()
    sl = ''
    als = db_sess.query(News).filter()
    for j in als:
        k = 0
        for i in m:
            s, s1 = i.split('_')
            b = eval(f'j.{s}')
            if s1 not in str(b).lower():
                k = 1
        if k == 0:
            sl += f" (News.id == '{j.id}') |"
    try:
        sl = sl[1:-2]
        print(sl, 1)
        news = db_sess.query(News).filter(eval(sl))
    except:
        news = db_sess.query(News).filter(News.id == 'xz')
    href = filtr + '.'
    return render_template("shop.html", news=news, title='Магазин', hr=href)


@app.route('/shop1/<int:movie_id>')
def post(movie_id=None):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        f"""UPDATE users SET cart="{user.cart} {movie_id}" WHERE id={current_user.id}""")
    con.commit()
    return redirect('/shop')


@app.route("/shop")
def shop1():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter()
    try:
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        href = '/shop/'
        is_admin = user.is_admin

        product_type = []
        for i in news:
            if i.type.lower() not in product_type:
                product_type.append(i.type)

        return render_template("shop.html", news=news, title='Магазин', hr=href, product_type=product_type,
                               is_admin=is_admin)
    except:
        product_type = []
        href = '/shop/'
        for i in news:
            if i.type.lower() not in product_type:
                product_type.append(i.type)
        return render_template("shop.html", news=news, title='Магазин', hr=href, product_type=product_type)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if request.method == "POST":
        if form.password.data != form.password_again.data:
            return render_template('registred.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('registred.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            is_admin=0,
            cart='',
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')

    return render_template('registred.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('singin.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('singin.html', form=form)


@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)


@app.route('/product', methods=['GET', 'POST'])
@login_required
def add_product():
    db_sess = db_session.create_session()
    form = ProductForm()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    is_admin = user.is_admin

    if is_admin:
        if request.method == "POST":
            db_sess = db_session.create_session()
            news = News()

            news.title = form.title.data
            news.content = form.content.data
            news.price = form.price.data

            news.color = form.color.data
            news.size = form.size.data

            news.description = form.desc.data
            news.spec = form.spec.data

            news.type = form.type_k.data

            filename_cover = photos.save(form.cover.data)
            news.cover = '../static/img/' + filename_cover

            filename_images = photos.save(form.images.data)
            news.images = '../static/img/' + filename_images

            current_user.news.append(news)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/shop')
        return render_template('product.html', title='Добавление новости',
                               form=form)
    else:
        return redirect('/')


@app.route("/shop_single/<int:id>")
@login_required
def shop_single(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id)

    return render_template("shop-single.html", news=news, title='Продукт')


@app.route("/about")
def contact():
    return render_template('about.html', title='About')


@app.route("/contact")
def cntct():
    return render_template('contact.html', title='Контакты')


@app.route("/cart")
@login_required
def cart():
    db_sess = db_session.create_session()

    user = db_sess.query(User).filter(User.id == current_user.id).first()
    if user.cart:
        user_cart = [int(i) for i in str(user.cart).split(' ')]

        user_product = []
        for i in user_cart:
            user_product.append(db_sess.query(News).filter(News.id == i).first())
    else:
        user_product = False
    suma = 0
    if user.cart:
        for i in user_product:
            suma += i.price
    return render_template('cart.html', news=user_product, title='Корзина', suma=suma)


@app.route('/clear_cart')
def clear_cart():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        f"""UPDATE users SET cart="" WHERE id={current_user.id}""")
    con.commit()
    return redirect('/cart')


@app.route('/delete_item/<int:id>')
def delete_item(id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        f"""DELETE from news where id = {id}""")
    con.commit()
    return redirect('/shop')


@app.route('/profile')
def proflie():
    db_sess = db_session.create_session()

    user = db_sess.query(User).filter(User.id == current_user.id).first()
    return render_template('profile.html', title='Профиль', user=user)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    main()
