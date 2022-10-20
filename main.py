import datetime, os, shutil
import translators as ts
from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
    mixins,
)
from data import db_session
from data.models import *

from forms.login import LoginForm
from forms.register import RegisterForm
from forms.add_text import TextForm
from forms.training1 import TrainingOneForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
login_manager = LoginManager()
login_manager.init_app(app)


users_progress = {}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ["epub"]


def translate_tat_to_rus(word: str):
    return ts.google(word, from_language='tt', to_language='ru')


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


def add_word_to_dict(w):  # принимает татарское слово
    db_sess = db_session.create_session()
    word_id = db_sess.query(Words.id).filter(Words.word_tat == w).first()
    if not word_id:
        new_word = Words()
        new_word.word_tat = w
        new_word.word_ru = translate_tat_to_rus(w)
        db_sess.add(new_word)
        db_sess.commit()
    word_id = db_sess.query(Words.id).filter(Words.word_tat == w).first()[0]
    new_ass = Users_to_words()
    new_ass.word_id = word_id
    new_ass.user_id = current_user.id
    try:
        db_sess.add(new_ass)
        db_sess.commit()
    except sqlalchemy.exc.IntegrityError:
        pass


@app.route('/add_word')
def add_word():
    add_word_to_dict('китап')
    return render_template('index.html')


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    """Получение текущего пользователся"""
    db_sess = db_session.create_session()
    return db_sess.query(Users).get(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Users).filter(Users.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', message='Неправильный логин или пароль', form=form)
    return render_template('login.html', form=form, title='Авторизация')


@app.route("/register", methods=["GET", "POST"])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="Пароли не совпадают",
            )
        db_sess = db_session.create_session()
        if db_sess.query(Users).filter(Users.email == form.email.data).first():
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="Такой пользователь уже есть",
            )
        user = Users()
        user.login = form.login.data
        user.email = form.email.data
        user.tg_username = form.tg_username.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/profile")
@login_required
def profile():
    try:
        word_count = len(current_user.words.split(","))
    except:
        word_count = 0
    items_list = [
        ["Имя", current_user.login],
        ["Почта", current_user.email],
        [
            "Телеграм",
            current_user.tg_username
            if current_user.tg_username is not None
            else "Не указан",
        ],
        ["Дата создания", str(current_user.creation_date)],
        ["Кол-во слов", word_count],
    ]
    return render_template("profile.html", items_list=items_list)


@app.route("/words", methods=["GET", "POST"])
@login_required
def words():  # мои добавленные слова
    try:
        db_sess = db_session.create_session()
        user_words_id = list(map(lambda x: x.word_id,
                                 db_sess.query(Users_to_words).filter(Users_to_words.user_id == current_user.id).all()))
        if request.method == "POST":
            if "search2" in request.form:
                words = db_sess.query(Words).filter(
                    (Words.word_tat.like(f"%{request.form.get('field2')}%")),
                    Words.id.in_(list(map(int, user_words_id))),
                )
                return render_template("words.html", title="мои слова", words=words)
            words = db_sess.query(Words).filter(
                (Words.word_ru.like(f"%{request.form.get('field1')}%")),
                Words.id.in_(list(map(int, user_words_id))),
            )
            return render_template("words.html", title="мои слова", words=words)

        words = db_sess.query(Words).filter(Words.id.in_(list(map(int, user_words_id)))).all()

        return render_template("words.html", title="мои слова", words=words)
    except:
        return render_template("words.html", title="мои слова", words=[])


@app.route("/books", methods=["GET", "POST"])
@login_required
def books():  # мои добавленные книги
    db_sess = db_session.create_session()
    books_id = list(
        map(lambda x: x.book_id, db_sess.query(Users_to_books).filter(Users_to_books.user_id == current_user.id).all()))
    if request.method == "POST":
        books = (
            db_sess.query(Books)
                .filter(
                Books.id.in_(books_id),
                Books.title.like(f"%{request.form.get('field')}%"),
            ).all()
        )
        return render_template("books.html", title="мои слова", books=books)
    books = db_sess.query(Books).filter(Books.id.in_(books_id)).all()
    return render_template("books.html", title="мои слова", books=books)


@app.route("/books_and_texts/<int:val>", methods=["GET", "POST"])
@login_required
def books_and_texts(val):  # ВСЕ КНИГИ (val in [1, 2, 3] то есть сложность где 1 легкое
    db_sess = db_session.create_session()
    if request.method == "POST":
        books = db_sess.query(Books).filter(
            (Books.title.like(f"%{request.form.get('field')}%"))
            | (Books.author.like(f"%{request.form.get('field')}%"))
        )
        return render_template(
            "books_and_texts.html", title="книги и тексты", books=books
        )
    if val == 0:
        books = db_sess.query(Books).all()
    else:
        d = {1: 'easy', 2: 'medium', 3: 'hard'}
        books = db_sess.query(Books).filter(Books.difficult_level == d[val]).all()
    return render_template("books_and_texts.html", title="книги и тексты", books=books)


@app.route("/add_text", methods=["GET", "POST"])
@login_required
def add_text():
    form = TextForm()
    if form.validate_on_submit():
        if form.author.data and form.title.data and form.file.data and form.difficult.data:
            db_sess = db_session.create_session()
            max_id = db_sess.query(Books).order_by(Books.id).all()
            if not max_id:
                max_id = 1
            else:
                max_id = max_id[-1].id + 1
            d = {1: 'easy', 2: 'medium', 3: 'hard'}
            book = Books()
            book.author = form.author.data
            book.title = form.title.data
            book.difficult_level = d[int(form.difficult.data)]
            book.creator_id = current_user.id
            if allowed_file(form.file.data.filename):
                f = request.files["file"]
                path = f"books\{max_id}.epub"
                f.save(path)
                os.mkdir(f"books\{max_id}")
                shutil.move(f"books\{max_id}.epub", f"books\{max_id}\{max_id}.epub")
            db_sess.merge(current_user)
            db_sess.add(book)
            db_sess.commit()
            return redirect("/books_and_texts/0")
        return render_template("add_text.html", message="не все поля заполнены", form=form)
    return render_template("add_text.html", title="добавление текста", form=form)


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


@app.route("/trainings")
@login_required
def trainings():
    return render_template("trainings.html")


@app.route('/training/<int:val>', methods=["GET", "POST"])
@login_required
def training1(val):
    form = TrainingOneForm()
    form.variants.choices = [('1', 'word1'), ('2', 'word2'), ('3', 'word3'), ('4', 'word4')]
    if form.validate_on_submit():
        print(form.variants.data)
    return render_template("training1.html", title="тренировка выбор верного ответа", form=form)


def main():
    db_session.global_init(user_name='postgres', user_password='123', host='localhost', port='5432',
                           db_name='tatlib_db')
    app.run(port=8080, host="127.0.0.1")


if __name__ == "__main__":
    main()