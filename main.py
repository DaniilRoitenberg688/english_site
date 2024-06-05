import csv

from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, current_user

from data.db_session import create_session, global_init
from data.modules import Module
from data.users import User
from forms.modules_forms import CreateModule
from forms.user_form import LoginForm, RegisterForm, RegisterStudentForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    """Загрузка пользователя"""
    db_sess = create_session()
    user = db_sess.query(User).get(user_id)

    return user


@app.route('/', methods=['GET', 'POST'])
def index():
    sess = create_session()
    if current_user.is_authenticated:
        if not current_user.status and current_user.admin:
            users = sess.query(User).all()
            print(users)
            return render_template('index_for_admin.html', users=users)
        if current_user.status:
            sess = create_session()
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

        sess = create_session()
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
        sess = create_session()
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
    sess = create_session()
    user: User = sess.query(User).get(id)
    print(user.id)
    user.status = 1
    sess.commit()
    return redirect('/')


@app.route('/remove_teacher/<id>', methods=['GET', 'POST'])
def remove_teacher(id):
    sess = create_session()
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
        sess = create_session()
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


@app.route('/all_modules', methods=['GET', 'POST'])
def see_all_modules():
    sess = create_session()
    modules = sess.query(Module).filter(Module.teacher == current_user.id).all()
    return render_template('see_all_modules.html', title='Все модули', modules=modules)


@app.route('/add_module', methods=['GET', 'POST'])
def add_module():
    form = CreateModule()
    if form.validate_on_submit():
        sess = create_session()
        module = Module(name=form.name.data,
                        description=form.description.data,
                        words=f'{form.name.data}.csv',
                        teacher=current_user.id)
        sess.add(module)


        with open(f'static/words/{module.words}', 'w') as file:
            writer = csv.DictWriter(file, fieldnames=['word', 'translation'], delimiter=';',
                                    quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()

        for student in sess.query(User).filter(User.teacher == current_user.email):
            if student.modules:
                modules = student.modules.split()
                modules.append(f'{module.id}: {0}')
                student.modules = ' '.join(modules)
            else:
                student.modules = f'{module.id}: {0}'


        sess.commit()

        return redirect('/all_modules')

    return render_template('new_module.html', form=form)


def main():
    global_init('db/users.db')
    app.run('127.0.0.1', 8000)


if __name__ == '__main__':
    main()
