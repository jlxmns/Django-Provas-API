# Django-Provas-API

Desafio para implementar uma Web Service RESTful capaz de se comunicar com aplicações mobile e web.

## Funcionalidade do web service

O web service deve simular uma aplicação para gerenciamento de provas com questões de múltiplas escolhas.
A aplicação deve incluir gerenciamento (CRUD e listagem) de: usuários, provas, questões, escolhas e participantes. Também deve incluir criação e edição de respostas dos candidatos.

Além disso, também deve corrigir automaticamente as respostas dos participantes e calcular e disponibilizar um ranking automaticamente.

## Requisitos

1. A aplicação deve ser Django API-only, usando Django Ninja
2. Possibilitar buscas por string nos endpoints de listagem.
3. Possibilitar ordenação e paginação nos endpoints de listagem.
4. Cada usuário deverá ter um dos seguintes perfis: “Administrador” ou “Participante”.
5. Cada participante poderá estar inscrito em uma ou mais provas.
6. Possuir sistema de autenticação com utilização de JWTs.
7. Possuir sistema controle de acesso, para garantir que participantes apenas possam:
8. Listar as provas que estão participando.
9. Enviar e editar as próprias respostas.
10. A correção das respostas e o cálculos dos rankings das provas deverão ser assíncronos e executados por meio de jobs.
11. Possuir pelo menos um teste para cada operação de cada endpoint criado.
12. Criar documentação de especificação das chamadas ao WebService.
13. Enviar o código para um repositório público do Github.
14. Utilizar Python 3.10, Django 5 e Django Ninja 1.3 (ou versões superiores)
15. Seguir os padrões e convenções do Django.
16. Seguir Normalização do Banco de Dados.
17. Utilizar docker-compose para criar um container da aplicação e suas dependências.
18. Criar README com instruções para executar o projeto localmente e criar um cenário demonstrativo.

## Como rodar o projeto

1. Certifique-se que o [Docker](https://www.docker.com/) está instalado, funcional e aberto em sua máquina
2. Na root do projeto, abra o terminal e digite o comando ``docker-compose up -d``
3. Após isso, o projeto deverá estar funcional e rodando em ``http://localhost:8000``
4. A API e sua documentação estão disponíveis em ``http://localhost:8000/api/`` e ``http://localhost:8000/api/docs``

## Dependências para desenvolvimento

1. Para desenvolvimento, é recomendado o uso de ``pre-commits``. O arquivo de configuração já está disponível no projeto
2. As dependências são gerenciadas pelo ``Poetry``
