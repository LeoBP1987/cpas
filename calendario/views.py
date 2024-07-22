from django.shortcuts import render, redirect

def configuracoes(request):

    return render(request, 'calendario/configuracoes.html')
