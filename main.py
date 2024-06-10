import csv
import os
from random import randrange

from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, current_user

from data.db_session import create_session, global_init
from data.modules import Module
from data.users import User
from forms.modules_forms import CreateModule, AddWord, ChangeNameDescription, EditWord
from forms.test_forms import TestWord
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


def my_shuffle(line: list) -> str:
    result_line = ''
    while line:
        letter_index = randrange(len(line))
        result_line += line.pop(letter_index)

    return result_line


@app.route('/', methods=['GET', 'POST'])
def index():
    global words_for_test, length, right_answers, have_done
    sess = create_session()
    if current_user.is_authenticated:
        if not current_user.status and current_user.admin:
            users = sess.query(User).all()
            return render_template('index_for_admin.html', users=users, title='Главная')

        if current_user.status:
            sess = create_session()
            students = sess.query(User).filter(User.teacher == current_user.email)
            students = sorted(students, key=lambda student: student.surname)
            return render_template('index_for_teacher.html', students=students, title='Главная')
        if current_user.teacher:
            sess = create_session()
            modules = [i.split(':') for i in current_user.modules.split()]
            modules_for_template = []
            for module_id, result in modules:
                module = sess.query(Module).get(int(module_id))
                modules_for_template.append([module, result])

            have_done = 0
            length = 0
            right_answers = 0
            words_for_test = []

            return render_template('index.html', modules=modules_for_template, title='Главная')

        return render_template('index_for_everybody.html', title='Главная')

    return render_template('index.html', title='Войдите или зарегистрируйтесь')


words_for_test = []
right_answers = 0
length = len(words_for_test)
have_done = 0


def prepare_test(module_id):
    global words_for_test, length
    sess = create_session()
    module: Module = sess.query(Module).get(module_id)

    with open(f'static/words/{module.words}', 'r') as file:
        all_words = [i for i in csv.DictReader(file, delimiter=';', quotechar='"')]
        length = len(all_words)

    for _ in range(len(all_words)):
        random_word = all_words[randrange(len(all_words))]
        word = random_word['word']
        translation = random_word['translation']
        word_id = random_word['id']
        changed_word = my_shuffle(list(word))

        words_for_test.append({'id': word_id, 'word': word, 'translation': translation, 'changed_word': changed_word})
        all_words.remove(random_word)
    return words_for_test


@app.route('/test/<module_id>', methods=['GET', 'POST'])
def test(module_id):
    global words_for_test, length, have_done, right_answers
    if have_done == 0:
        prepare_test(module_id)

    if not words_for_test:
        sess = create_session()
        user: User = sess.query(User).get(current_user.id)
        words = [i.split(':') for i in user.modules.split()]
        for i in words:
            if i[0] == module_id:
                i[1] = str(round(right_answers / length, 2) * 100)

        words = [':'.join(i) for i in words]
        user.modules = ' '.join(words)
        sess.commit()
        return redirect('/')
    word = words_for_test.pop(0)
    have_done += 1
    return redirect(f'/test_word/{word["word"]}_{word["translation"]}_{word["changed_word"]}_{module_id}')


@app.route('/test_word/<arguments>', methods=['GET', 'POST'])
def test_word(arguments):
    global words_for_test, have_done, right_answers, length
    form = TestWord()
    word, translation, changed_word, module_id = arguments.split('_')
    if form.validate_on_submit():
        if form.answer.data == word:
            right_answers += 1
            return render_template('right_not.html', right=1, have_done=have_done, length=length,
                                   module_id=module_id, title='Верно')

        return render_template('right_not.html', have_done=have_done, length=length,
                               module_id=module_id, title='Неверно')

    return render_template('test_word.html', have_done=have_done, length=length, form=form,
                           word={'changed_word': changed_word, 'translation': translation}, title='Тест')


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
    sess = create_session()
    user: User = sess.query(User).get(id)
    user.status = 1
    sess.commit()
    return redirect('/')


@app.route('/remove_teacher/<id>', methods=['GET', 'POST'])
def remove_teacher(id):
    sess = create_session()
    user: User = sess.query(User).get(id)
    user.status = 0
    sess.commit()
    return redirect('/')


@app.route('/add_student', methods=['POST', 'GET'])
def add_student():
    form = RegisterStudentForm()
    if form.validate_on_submit():
        email = f'{form.name.data.lower()}@{form.surname.data.lower()}'
        sess = create_session()
        teacher_email = str(current_user.email)
        teachers_modules = sess.query(Module).filter(Module.teacher == current_user.id).all()
        line = []
        for i in teachers_modules:
            line.append(':'.join([str(i.id), '0']))
        user = User(name=form.name.data,
                    surname=form.surname.data,
                    email=email,
                    teacher=teacher_email,
                    modules=' '.join(line))
        user.set_password(form.password.data)
        sess.merge(user)
        sess.commit()
        return redirect('/')
    return render_template('register_student.html', form=form, title='Регистрация ученика')


@app.route('/delete_student/<int:student_id>', methods=['POST', 'GET'])
def delete_student(student_id):
    sess = create_session()
    student = sess.query(User).get(student_id)
    sess.delete(student)
    sess.commit()
    return redirect('/')


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

        all_modules_names = sess.query(Module.name).all()

        if form.name.data in all_modules_names:
            return render_template('new_module.html', form=form,
                                   message='Такой модуль уже есть. Придумайте другое название',
                                   title='Создание модуля')

        module = Module(name=form.name.data,
                        description=form.description.data,
                        words=f'{form.name.data}.csv',
                        teacher=current_user.id)

        sess.add(module)

        with open(f'static/words/{module.words}', 'w', newline='') as file:
            pass

        for student in sess.query(User).filter(User.teacher == current_user.email):
            if student.modules:
                modules = student.modules.split()
                modules.append(f'{module.id}:{0}')
                student.modules = ' '.join(modules)
            else:
                student.modules = f'{module.id}:{0}'

        sess.commit()

        return redirect('/all_modules')

    return render_template('new_module.html', form=form)


@app.route('/add_word/<int:module_id>', methods=['GET', 'POST'])
def add_word(module_id):
    form = AddWord()
    sess = create_session()
    module: Module = sess.query(Module).get(module_id)
    if form.validate_on_submit():
        with open(f'static/words/{module.words}', 'r', newline='') as file:
            data = csv.DictReader(file, delimiter=';', quotechar='"')
            previous_words = [line for line in data]

        with open(f'static/words/{module.words}', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'word', 'translation'], delimiter=';',
                                    quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()

            last_index = 1
            if previous_words:
                last_index = int(previous_words[-1]['id']) + 1

            for line in previous_words:
                writer.writerow(line)

            for i in range(1, 11):
                word = form.data[f'word{i}']
                translation = form.data[f'translation{i}']
                if word and translation:
                    writer.writerow({'id': str(last_index), 'word': word, 'translation': translation})

                    last_index += 1

        return redirect('/all_modules')

    return render_template('add_word.html', form=form, title='Добавление слов', module_name=module.name)


@app.route('/edit_module/<int:module_id>', methods=['GET', 'POST'])
def edit_module(module_id):
    sess = create_session()
    module = sess.query(Module).get(module_id)

    with open(f'static/words/{module.words}', 'r') as file:
        data = csv.DictReader(file, delimiter=';', quotechar='"')
        words_of_module = [i for i in data]

    return render_template('edit_module.html', module=module, title='Изменение модуля', words=words_of_module)


@app.route('/delete_word/<ids>/', methods=['GET', 'POST'])
def delete_word(ids):
    sess = create_session()
    module_id, word_id = ids.split('_')
    module_id, word_id = int(module_id), int(word_id)
    module: Module = sess.query(Module).get(module_id)
    with open(f'static/words/{module.words}', 'r') as file:
        words = [i for i in csv.DictReader(file, delimiter=';', quotechar='"') if int(i['id']) != word_id]

    with open(f'static/words/{module.words}', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'word', 'translation'], delimiter=';', quotechar='"')
        writer.writeheader()
        for i in words:
            writer.writerow(i)

    return redirect(f'/edit_module/{module_id}')


@app.route('/change_name_description/<arguments>', methods=['GET', 'POST'])
def change_name_description(arguments):
    module_id, name_description = arguments.split('_')
    module_id, name_description = int(module_id), int(name_description)
    form = ChangeNameDescription()
    if form.validate_on_submit():
        sess = create_session()
        module: Module = sess.query(Module).get(module_id)

        if name_description:
            previous_file_name = module.words
            module.name = form.new_line.data
            module.words = f'{form.new_line.data}.csv'
            os.rename(f'static/words/{previous_file_name}', f'static/words/{form.new_line.data}.csv')
        else:
            module.description = form.new_line.data

        sess.commit()
        return redirect(f'/edit_module/{module_id}')

    return render_template('change_name_description.html',
                           name=name_description, form=form, title='Изменение модуля', id=module_id)


@app.route('/edit_word/<arguments>', methods=['GET', 'POST'])
def edit_word(arguments):
    form = EditWord()
    module_id, word_id = arguments.split('_')
    module_id, word_id = int(module_id), int(word_id)
    if form.validate_on_submit():

        sess = create_session()
        module: Module = sess.query(Module).get(module_id)

        with open(f'static/words/{module.words}', 'r') as file:
            all_words = [i for i in csv.DictReader(file, delimiter=';', quotechar='"')]

            for word in all_words:
                if int(word['id']) == word_id:
                    if form.word.data:
                        word['word'] = form.word.data

                    if form.translation.data:
                        word['translation'] = form.translation.data

        with open(f'static/words/{module.words}', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'word', 'translation'], delimiter=';', quotechar='"')
            writer.writeheader()
            for line in all_words:
                writer.writerow(line)

        return redirect(f'/edit_module/{module_id}')

    return render_template('edit_word.html', form=form, title='Изменение слова', id=module_id)


@app.route('/delete_module/<int:module_id>', methods=['GET', 'POST'])
def delete_module(module_id):
    sess = create_session()
    module_for_delete: Module = sess.query(Module).get(module_id)
    all_students = sess.query(User).filter(User.teacher == current_user.email).all()
    student: User

    for student in all_students:
        students_modules = list(filter(lambda x: int(x.split(':')[0]) != module_id, student.modules.split()))
        student.modules = ' '.join(students_modules)

    os.remove(f'static/words/{module_for_delete.words}')

    sess.delete(module_for_delete)

    sess.commit()

    return redirect('/all_modules')


@app.route('/student_info/<int:student_id>', methods=['GET', 'POST'])
def student_info(student_id):
    sess = create_session()
    student: User = sess.query(User).get(student_id)
    student_modules = student.modules.split()
    for_template = []
    for module in student_modules:
        module_id, result = module.split(':')
        module: Module = sess.query(Module).get(module_id)
        for_template.append([module, result])
    return render_template('student_info.html', title='Информация об ученике', student=student,
                           student_modules=for_template)


@app.route('/make_need/<arguments>', methods=['GET', 'POST'])
def make_need(arguments):
    module_id, student_id = arguments.split('_')

    sess = create_session()

    student: User = sess.query(User).get(int(student_id))

    student_modules = [i.split(':') for i in student.modules.split()]
    for i in student_modules:
        if i[0] == module_id:
            i[1] = '0'

    new_student_modules = [':'.join(i) for i in student_modules]
    student.modules = ' '.join(new_student_modules)
    sess.commit()
    return redirect(f'/student_info/{student_id}')


def main():
    global_init('db/users_modules.db')
    app.run('127.0.0.1', 5000)


if __name__ == '__main__':
    main()
