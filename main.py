from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data.db_session_users import create_session_users, global_init_users
from data.db_session_words import create_session_words, global_init_words
from forms.user_form import LoginForm, RegisterForm, RegisterStudentForm


from data.users import User


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

@login_manager.user_loader
def load_user(user_id):
    """Загрузка пользователя"""
    db_sess = create_session_users()
    user = db_sess.query(User).get(user_id)

    return user


@app.route('/', methods=['GET', 'POST'])
def index():
    sess = create_session_users()
    if current_user.is_authenticated:
        if not current_user.status and current_user.admin:
            users = sess.query(User).all()
            print(users)
            return render_template('index_for_admin.html', users=users)
        if current_user.status:
            sess = create_session_users()
            students = sess.query(User).filter(User.teacher == current_user.email)
            students = sorted(students, key=lambda student: student.surname)
            print(students)
            return render_template('index_for_teacher.html', students=students)


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
        if user.email == 'daniilroitenberg@yandex.ru':
            user.admin = True
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
        if user and user.check_password(form.password.data):
            if user.email == 'daniilroitenberg@yandex.ru':
                user.admin = True
                sess.commit()
            login_user(user, remember=form.remember_me.data)
            return redirect('/')

        return render_template('login.html', form=form, message='Не правильный логин или пароль', title='Вход')

    return render_template('login.html', title='Вход', form=form)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect('/')


@app.route('/new_teacher/<id>', methods=['GET', 'POST'])
def new_teacher(id):
    print(id)
    sess = create_session_users()
    user: User = sess.query(User).get(id)
    print(user.id)
    user.status = 1
    sess.commit()
    return redirect('/')


@app.route('/remove_teacher/<id>', methods=['GET', 'POST'])
def remove_teacher(id):
    sess = create_session_users()
    user: User = sess.query(User).get(id)
    print(user.id)
    user.status = 0
    sess.commit()
    return redirect('/')




@app.route('/add_student', methods=['POST', 'GET'])
def add_student():
    form = RegisterStudentForm()
    if form.validate_on_submit():
        email = f'{form.name.data}@{form.surname.data}'
        sess = create_session_users()
        teacher_email = str(current_user.email)
        user = User(name=form.name.data,
                    surname=form.surname.data,
                    email=email,
                    teacher=teacher_email,
                    modules='')
        user.set_password(form.password.data)
        sess.merge(user)
        sess.commit()
        return redirect('/')
    return render_template('register_student.html', form=form, title='Student registration')


def main():
    # global_init_words('db/words.db')
    global_init_users('db/users.db')
    app.run('127.0.0.1', 8000)


if __name__ == '__main__':
    main()