# ![Banner CPAS - V2 - Sem Fundo](https://github.com/user-attachments/assets/83d91353-df91-46e6-a551-42cae5c46dc6)
## Índice
1.	Visão Geral
2.	Configuração
3.	Tecnologias Utilizadas  
4.	Contato
## Visão Geral
>O CPAS (Cadastro de Plantões e Atividades) foi desenvolvido para facilitar a atribulada rotina de médicos autônomos.<br>

>Nele, os médicos poderão fazer o cadastro de todos os seus plantões e demais atividades, podendo criar recorrencias diárias, 
semanais, mensais e até mesmo personalizadas, para manter uma agenda customizada onde poderão sempre checar com facilidade seus 
próximos afazeres, sem riscos de se perderem em contratempos e recebendo diariamente, no horário que preferirem, um relatório com todas as atividades
do dia.<br>

>Além disso, o CPAS conta com dois dashboards bem completos, por onde o usuário poderá analisar sua situação financeira e sua rotina, obtendo 
gráficos, totais e médias do que têm a receber e sua ocupação no período selecionado, para que possam se programar e garantir horas adequadas de descanso.<br><br>

## Configurações

**Pré-requisitos:**

-	Git
-	Python 3.x
- SQLite

<br>**Estrutura Inicial:**

1 - Logo após clonar o repositório git, você irá abrir o diretório salvo e criar a máquina virtual por onde irá rodar o servidor da aplicação.<br><br>
2 - Em seguida, você terá acesso a todas as bibliotecas necessárias para o projeto instalando o requirements.txt.<br> <br>
3 - Na sequência é preciso inserir as chaves necessárias para rodar o sistema em seu ambiente. Primeiro, renomeie o arquivo ".env.example" para apenas ".env".<br><br> 
Nele você encontrára o seguinte cenário:<br><br>
![CHAVES Secretas](https://github.com/user-attachments/assets/e6c17c80-0108-413b-bbdc-41fde66901fc) <br><br>
Ou seja, além da chave secreta do Django, você precisará configurar as chaves para a conexão com a núvem de armazenamento de arquivos e um servidor de e-mail para os disparos de mensagens feitas pelo sistema.<br><br>
**Nota:** Note que para o armazenamento em núvem eu usei um bucket S3 na AWS. Caso prefira um outro servidor, não se esqueça de fazer os devidos ajustes no arquivo settings.py do sistema.

<br>**Uso do Sistema:**

Após as configurações de estrutura do sistema você já estará quase apito para usar o CPAS. Mas primeiro, você precisará logar no sistema e fazer o cadastro do usuário.<br> <br>
Por default o sistema vêm configurado com as seguinte credencias<br><br>
**-- Usuário: usuario**<br>
**-- Senha: usuario@123**<br><br>
Após logar, vá até o menu "Configurações" e acesse o botão "Usuário":<br><br>

![cpas_usuario](https://github.com/user-attachments/assets/ce733dbe-1617-40bd-8d2a-d4640a45b0a8)<br><br>

Nele você vai encontrar os dados do usuário padrão do sistema. Basta clicar em editar e inserir os dados do usuário que utilizará o CPAS.<br><br>
**Nota:** Se certifique se colocar um e-mail válido pois será para este endereço que o CPAS enviará as agendas diárias e enventuais pedidos de recuperação de senha.<br><br>

![edit_usuario_cpas](https://github.com/user-attachments/assets/cdb3f90a-25bd-482a-a256-ac6b0d960045) <br><br>

Por fim, ainda no menu "Configuração", basta acessar o botão "Alterar Senha" para cadastrar uma nova senha para o usuário.<br><br>
**O usuário também poderá, na tela de login, solicitar um link de recuperação de senha por email, desde que o email do usuário já esteja devidamente cadastrado.** <br> <br>

![cpas_alterarsenha](https://github.com/user-attachments/assets/59bba432-5eee-488e-9350-d9022bde3caf)

**Pronto! Agora o CPAS já está prontinho para ajudar o médico autonômo a organizar sua rotina e ganhos financeiros.** <br> <br>


## Tecnologias Utilizadas
![Django Version](https://img.shields.io/badge/Django-5.0.7-blue) 
![SQLite Version](https://img.shields.io/badge/SQLite-3.45.3-green) 
![HTML Version](https://img.shields.io/badge/HTML-black) 
![CSS Version](https://img.shields.io/badge/CSS-white) 
![JavaScript Version](https://img.shields.io/badge/JavaScript-red) <br> <br>

## Contato

**Sobre o desenvolvedor:**<br>

![foto](https://github.com/user-attachments/assets/68dce925-7a76-49dd-b9f0-3fac3b5d17f6)


***Leonardo Borges Pereira:***
Depois de mais de 12 anos no mercado da TI, indo de técnico à coordenador de equipe, resolvi ingressar nesse novo desáfio e realizar um antigo sonho de me especializar na área de desenvolvimento de sistemas, ajudando empresas e pessoas a darem vida à brilhantes idéias.

***Email:*** ***leonardobp1987@gmail.com***
