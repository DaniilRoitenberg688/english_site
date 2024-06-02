from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data.db_session_users import create_session_users, global_init_users
from data.db_session_words import create_session_words, global_init_words
from forms.user_form import LoginForm, RegisterForm


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
    if current_user.is_authenticated:
        if current_user.admin:
            users = sess.query(User).all()
            return render_template('index_for_admin.html', users=users)

    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', message='Пароли не совпадают', title='Регистрация',
                                   form=form)

        sess = create_session_users()
        user = User(name=form.name.data,
                    surname=form.surname.data,
                    email=form.email.data)
        user.set_password(form.password.data)
        sess.merge(user)
        sess.commit()
        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        sess = create_session_users()
        user = sess.query(User).filter(User.email == form.email.data).first()
        if not user:
            return render_template('login.html', message='Такого пользователя нет', title='Вход',
                                   form=form)
        if not user.check_password(form.password.data):
            return render_template('login.html', message='Неверный пароль', title='Вход',
                                   form=form)

        login_user(user, remember=form.remember_me.data)
        return redirect('/')

    return render_template('login.html', title='Вход', form=form)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect('/')


@app.route('/new_teacher/<id>', methods=['GET', 'POST'])
def new_teacher(id):
    sess = create_session_users()
    user = sess.query(User).get(id)
    user.teacher = True
    sess.commit()
    return redirect('/')


@app.route('/remove_teacher/<id>', methods=['GET', 'POST'])
def remove_teacher(id):
    sess = create_session_users()
    user = sess.query(User).get(id)
    user.teacher = False
    sess.commit()
    return redirect('/')


def main():
    # global_init_words('db/words.db')
    global_init_users('db/users.db')
    app.run('127.0.0.1', 8000)


if __name__ == '__main__':
    main()