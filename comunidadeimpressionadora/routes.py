from flask import render_template, url_for, request, flash, redirect, abort
from comunidadeimpressionadora import app, database, bcrypt
from comunidadeimpressionadora.forms import FormLogin, FormCriarConta, EditarPerfil, FormPost
from comunidadeimpressionadora.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image

lista_usuarios = ['Beatriz', 'Fernando', 'Alice']


@app.route('/')
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('home.html', posts=posts)


@app.route('/contato')
def contato():
    return render_template('contato.html')


@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()

    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()

    if 'botao_submit_login' in request.form and form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()

        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f"Login feito com successo no e-mail {form_login.email.data}", "alert-success")
            par_next = request.args.get('next')

            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))

        else:
            flash('Login e/ou senha incorretos.', 'alert-danger')

    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        #criptografar a senha
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data).decode('utf-8')
        #criar usuario
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_cript)
        #adicionar usuario ao banco de dados
        database.session.add(usuario)
        database.session.commit()

        # criou conta com successo
        # exbir mensagem
        flash(f"Conta criado com successo no e-mail {form_criarconta.email.data}", "alert-success")
        return redirect(url_for('home'))
    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)

@app.route('/sair')
def sair():
    logout_user()
    flash('Logout realizado com successo!', 'alert-success')
    return redirect(url_for('home'))

@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')

    return render_template('perfil.html', foto_perfil=foto_perfil)


def salvar_imagem(imagem):
    # adicionar um código aleatorio no nome da imagem
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao

    # reduzir o tamanho da imagem
    tamanho = (200, 200)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)

    # salvar a imagem na pasta fotos_perfil
    caminho = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    imagem_reduzida.save(caminho)

    return nome_arquivo


def atualizar_cursos(form):
    cursos_selecionados = []
    for campo in form:
        if 'curso_' in campo.name and campo.data:
            cursos_selecionados.append(campo.label.text)

    cursos = ';'.join(cursos_selecionados)
    return cursos


@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    form = EditarPerfil()

    if form.validate_on_submit():
        # editando dados do perfil
        current_user.email = form.email.data
        current_user.username = form.username.data

        # trocando foto do perfil
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem

        # adicionar cursos no banco de dados
        current_user.cursos = atualizar_cursos(form)

        database.session.commit()

        flash('Perfil atualizado com successo', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == "GET":
        form.email.data = current_user.email
        form.username.data = current_user.username

    return render_template('editar_perfil.html', foto_perfil=foto_perfil, form=form)


@app.route('/post/criar', methods=["GET", "POST"])
@login_required
def criar_post():
    form = FormPost()

    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post criado com Sucesso', 'alert-success')
        return redirect(url_for('criar_post'))
    return render_template('criar_post.html', form=form)


@app.route('/post/<post_id>', methods=["GET", "POST"])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)

    if current_user == post.autor:
        form = FormPost()

        if form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post atulizado com Sucesso', 'alert-success')
            return redirect(url_for('home'))

        elif request.method == "GET":
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
    else:
        form = None
    return render_template('post.html', post=post, form=form)

@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)

    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post excluido com Sucesso', 'alert-danger')
        return redirect(url_for('home'))

    else:
        abort(403)
