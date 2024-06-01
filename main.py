from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data.db_session_users import create_session_users, global_init_users
from data.db_session_words import create_session_words, global_init_words

from data.users import User

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

@login_manager.user_loader
def load_user(user_id):
    """Загрузка пользователя"""
    db_sess = create_session_users()
    return db_sess.query(User).get(user_id)

@app.route('/', methods=['GET', 'POST'])
def index():
    sess = create_session_users()


    return render_template('index.html')


def main():
    # global_init_words('db/words.db')
    global_init_users('db/users.db')
    app.run('127.0.0.1', 8000)


if __name__ == '__main__':
    main()