from django.shortcuts import render, redirect
from usuarios.forms import LoginForms, AlterarSenhaForms, UsuarioForms
from django.contrib import auth, messages

def login(request):

    """
    Formulário de login do sistema.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Se o método for GET: Retorna uma resposta HTTP que renderiza o template 'usuarios/login.html' com o formulário LoginForms.
        Se o método for POST: Checa a autenticidade das informações enviadas pelos parâmetros 'nome_login' e 'senha':
            - Caso seja autenticado: Loga o usuario usando auth.login e o redireciona para a path 'index'.
            - Caso contrário: Exibe mensagem de erro 'Nome de usuário ou senha não conferem.'.

    """

    form = LoginForms()

    if request.method == 'POST':
        form = LoginForms(request.POST)

        if form.is_valid():

            nome = form['nome_login'].value()
            senha = form['senha'].value()

            usuario = auth.authenticate(
                request,
                username=nome,
                password=senha,
            )

            if usuario is not None:
                auth.login(request, usuario)
                return redirect('index')
            else:
                messages.error(request, 'Nome de usuário ou senha não conferem.')
                return redirect('login')

    return render(request, 'usuarios/login.html', {'form':form})

def logout(request):
    
    """
    View para efetuar logout do usuário logado no momento da requisição.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    None
        A Função não tem retorno, apenas realiza o logout usando auth.logout e redireciona o usuário para a path 'login'.            
    """

    if request.user.is_authenticated:
        auth.logout(request)
        messages.success(request,'Logout Efetuado com Sucesso')
    else:
        auth.logout(request)
    return redirect('login')

def alterar_senha(request):

    """
    Formulário de alteração de senha do sistema.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Se o método for GET: Retorna uma resposta HTTP que renderiza o template 'usuarios/alterar_senha.html' com o formulário AlterarSenhaForms.
        Se o método for POST: Salva o parâmetro 'senha' através do 'request.user.set_password' e salva a alteração realizada.

    Tratamento de erros:
    --------
    - Se o formulário for inválido exibe a mensagem de erro 'Erro ao realizar troca de senha.'.  

    """

    form = AlterarSenhaForms()

    if request.method == 'POST':
        form = AlterarSenhaForms(request.POST)

        if form.is_valid():

            senha = form['senha'].value()
            request.user.set_password(senha)
            request.user.save() 
    
            messages.success(request, 'Senha alterada com sucesso')
            return redirect('index')
        else:
            messages.error(request, 'Erro ao realizar troca de senha.')


    return render(request, 'usuarios/alterar_senha.html', {'form':form})

def usuario(request):

    """
    View que retorna os dados cadastrados do usuário logado no momento da requisição.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Retorna uma resposta HTTP que renderiza o template 'usuarios/editar_usuario.html' com a variável 'user' que contém a instância do usuário logado no momento da requisição.

    """
    usuario = request.user

    return render(request, 'usuarios/usuario.html', {'usuario':usuario})

def editar_usuario(request):

    """
    Formulário de alteração de dados do usuario.

    Parâmetros:
    -----------
    request : HttpRequest
        Objeto da requisição HTTP que contém os dados do cliente (como o método, cabeçalhos e corpo).

    Retorno:
    --------
    HttpResponse
        Se o método for GET: Retorna uma resposta HTTP que renderiza o template 'usuarios/editar_usuario.html' com o formulário UsuarioForms povoado com suas respectivas informações da tabela auth.user.
        Se o método for POST: Salva as informações provenientes do parâmentros em seus campos correspondentes na tabela auth.user.

    Tratamento de erros:
    --------
    - Se o formulário for inválido exibe a mensagem de erro 'Erro atualizar dados.'.  

    Notas:
    --------
    - Como UsuarioForms não é um model.forms e sim um forms.Form, o pré-preenchimento de informações precisa ser feita de maneira manual.

    """

    user = request.user

    if request.method == 'POST':
        form = UsuarioForms(request.POST)

        if form.is_valid():

            nome_completo = form['nome_completo'].value()
            login = form['login'].value()
            email = form['email'].value()

            request.user.first_name = nome_completo
            request.user.username = login
            request.user.email = email
            request.user.save()
    
            messages.success(request, 'Dados atualizados com sucesso')
            return redirect('usuario')
        else:
            messages.error(request, 'Erro atualizar dados.')
    else:
        form = UsuarioForms(initial={
            'nome_completo': user.first_name,
            'login': user.username,
            'email': user.email,
        })
        
    return render(request, 'usuarios/editar_usuario.html', {'form':form})