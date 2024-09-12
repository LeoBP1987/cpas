from django.urls import path
from usuarios.views import login, logout, alterar_senha, usuario, editar_usuario
from usuarios.forms import CustomPasswordResetForm, CustomSetPasswordForm
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('usuario/', usuario, name='usuario'),
    path('editar_usuario/', editar_usuario, name='editar_usuario'),
    path('alterar_senha/', alterar_senha, name='alterar_senha'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='usuarios/password_reset_form.html',form_class=CustomPasswordResetForm), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='usuarios/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='usuarios/password_reset_confirm.html',form_class=CustomSetPasswordForm), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='usuarios/password_reset_complete.html'), name='password_reset_complete'),
]