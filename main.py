from os import abort

from flask import Flask, render_template, redirect, make_response, request, url_for

from forms.news import ProductForm
from forms.user import RegisterForm, LoginForm

from data import db_session
from data.users import User
from data.news import News
import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '40d1649f-0493-4b70-98ba-98533de7710b'

login_manager = LoginManager()
login_manager.init_app(app)


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
    db_session.global_init("db/blogs.db")
    app.run()


@app.route("/")
def index():
    db_sess = db_session.create_session()

    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)

    return render_template("index.html", news=news, title='Home')


@app.route("/shop/<string:filtr>")
def shop(filtr):
    m = filtr.split('.')
    db_sess = db_session.create_session()
    sl = ''

    for i in m:
        print(i)
        s, s1 = i.split('_')
        sl += f" (News.{s} == '{s1}') &"
    sl = sl[1:-2]

    news = db_sess.query(News).filter(eval(sl))
    href = filtr + '.'
    return render_template("shop.html", news=news, title='Shop', hr=href)


@app.route("/shop")
def shop1():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter()
    href = '/shop/'

    product_type = []
    for i in news:
        if i.type.lower() not in product_type:
            product_type.append(i.type)

    return render_template("shop.html", news=news, title='Shop', hr=href, product_type=product_type)


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
        USER_ID = user.id
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('singin.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('singin.html', form=form)


@app.route('/product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()

    if request.method == "POST":
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.price = form.price.data

        news.type = form.type_k.data

        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('product.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = ProductForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('product.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route("/shop_single/<int:id>")
def shop_single(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id)

    return render_template("shop-single.html", news=news)


@app.route("/about")
@login_required
def contact():
    return render_template('about.html', title='About')


@app.route("/contact")
@login_required
def cntct():
    return render_template('contact.html', title='Contact')


@app.route("/cart")
@login_required
def cart():
    db_sess = db_session.create_session()

    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)

    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user_cart = [int(i) for i in user.cart.split(' ')]

    user_product = []
    for i in user_cart:
        user_product.append(db_sess.query(News).filter(News.id == i).first())

    return render_template('cart.html', news=user_product, title='cart')


if __name__ == '__main__':
    main()
