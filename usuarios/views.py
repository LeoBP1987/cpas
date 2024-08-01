from django.shortcuts import render, redirect
from usuarios.forms import LoginForms, AlterarSenhaForms
from django.contrib import auth, messages

def login(request):
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
    if request.user.is_authenticated:
        auth.logout(request)
        messages.success(request,'Logout Efetuado com Sucesso')
    else:
        auth.logout(request)
    return redirect('login')

def alterar_senha(request):    
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