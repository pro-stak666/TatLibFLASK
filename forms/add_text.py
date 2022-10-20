from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, StringField, SubmitField


class TextForm(FlaskForm):
    author = StringField("Имя автора")
    title = StringField("Название книги")
    file = FileField("Книга в формате .epab")
    difficult = SelectField(
        "Сложность", choices=[("1", "Легкая"), ("2", "Средняя"), ("3", "Сложная")]
    )
    submit = SubmitField("Добавить")