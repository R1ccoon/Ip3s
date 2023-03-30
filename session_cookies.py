from flask import Flask, request, make_response, session

app = Flask(__name__)
app.config['SECRET_KEY'] = '40d1649f-0493-4b70-98ba-98533de7710b'


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")

app.run()