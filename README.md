
<!-- Improved compatibility of back to top link -->
<a id="readme-top"></a>
<br />
<div align="center">
  <img src="rgb_iscte_pt_horizontal_positive.png" alt="Logo" width="500" height="150">

  <h3 align="center">IscteSpot</h3>

  <p align="center">
    Uma aplicação SaaS deliberadamente vulnerável para ISCTE – Segurança de Software e Aplicações
    <br />
    <br />
  </p>
</div>

## Sobre o Projeto

Este projeto é direcionado aos estudantes do ISCTE inscritos na unidade curricular de **Segurança de Software e Aplicações**.  
Os estudantes irão utilizar este projeto para compreender as implicações da segurança em aplicações web modernas e entender os riscos ao nível do negócio.

## Começar

Existem 2 opções para executar a aplicação: utilizando **Docker** ou instalando e executando localmente.  
Abaixo encontram-se duas secções com os passos de instalação para ambos os casos.

Primeiro, pode clonar este repositório para a localização desejada:
```sh
git clone https://github.com/narfasec/isctespot.git
```

## Docker (Início Rápido)

[Instalar Docker](https://docs.docker.com/engine/install/), caso ainda não esteja instalado no seu sistema.

* Após instalar o Docker, certifique-se de que o daemon do Docker está a correr (abrir a aplicação Docker Desktop é suficiente)
* Mude para o diretório iscte_spot e execute o docker compose para construir e iniciar o projeto
```
cd iscte_spot/
docker-compose up --build
```
* Execute o script de configuração (**setup.ps1** para Windows, **setup.sh** para macOS e Linux) para popular a base de dados com dados de teste.
```
.\setup.ps1
```
* Nesta fase a aplicação deverá estar pronta. Pode executar verificações de estado para confirmar se está tudo correto.  
  Abra o navegador e aceda a **http://localhost:5173** para ver a interface da aplicação.
```
docker exec project-server-1 python /app/tests/health_checks/test_flow_1.py
```

## Configuração Local (Instalação Manual)

_Abaixo encontram-se os passos para configurar o projeto no seu ambiente local. Esta também é a configuração recomendada para desenvolvimento, permitindo alterar código e depurar problemas facilmente._

### Pré-requisitos
* **Python 3.9+** – [Transferir de python.org](https://www.python.org/downloads/)
* **Node.js 18+** – [Transferir de nodejs.org](https://nodejs.org/)
* **MariaDB** – [Transferir de mariadb.com](https://mariadb.com/downloads/)
* **npm** – Normalmente incluído com o Node.js

### Passos de Instalação

1. **Clonar o repositório**
```bash
git clone https://github.com/narfasec/isctespot.git
cd isctespot/
```

2. **Configurar MariaDB**
- Instale o MariaDB no seu sistema

3. **Configurar o ambiente Python**
```bash
cd server/
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

4. **Configurar o Frontend**
```bash
cd frontend/admin-one-vue-tailwind-master/
npm install
```

### Início Rápido para Configuração Local

A forma mais simples de começar, com verificação automática e script de configuração:

```bash
cd isctespot/
python isctespot_setup.py
```

Este script irá:
- ✅ Verificar os requisitos do sistema (Python 3.9, Node.js 18+, npm, MariaDB)
- ✅ Validar o ambiente virtual e dependências
- ✅ Testar a ligação ao MariaDB em localhost:3306
- ✅ Oferecer a instalação de pacotes em falta
- ✅ Disponibilizar opções de configuração da base de dados ("Executar todos os scripts de setup" para primeira execução)
- ✅ Iniciar todos os serviços em modo de desenvolvimento
- ✅ Executar verificações de estado em todos os serviços
- ✅ Opcionalmente executar testes end-to-end (e2e)

### Executar a Aplicação Separadamente (Recomendado para Depuração)

1. **Iniciar MariaDB** (caso ainda não esteja a correr)

2. **Iniciar Backend** (Terminal 1)
```bash
cd server/
source venv/bin/activate  # ou venv\Scripts\activate no Windows
python appserver.py
```

3. **Iniciar Frontend** (Terminal 2)
```bash
cd frontend/admin-one-vue-tailwind-master/
npm run dev
```

4. **Configurar Base de Dados** (Terminal 3)
```bash
cd server/db/setup/
python clean_db.py
python create_db.py
python data_population.py
```

5. **Executar Verificações de Estado**
```bash
cd server/
python tests/health_checks/test_flow_1.py
```

### URLs dos Serviços
- **Frontend**: http://localhost:5173
- **API Backend**: http://localhost:5000
- **Portal de Administração**: http://localhost:5000/ap/login
- **MariaDB**: localhost:3306

### Tecnologias Utilizadas
* Python
* Flask
* Vue
* MariaDB

## ⚠️ AVISO!
Esta é uma aplicação vulnerável. Não a utilize em cenários reais e, especialmente, não a exponha à Internet, pois poderá comprometer os seus sistemas.
