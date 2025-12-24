import os
from dotenv import load_dotenv
from api.__init__ import create_app

# Carrega as variáveis do ficheiro .env
load_dotenv()

def setup_security_configs(app):
    """Lê os arquivos físicos e carrega na memória do Flask"""
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Busca os caminhos definidos no .env
    priv_path = os.path.join(base_dir, os.getenv('JWT_PRIVATE_KEY_PATH'))
    pub_path = os.path.join(base_dir, os.getenv('JWT_PUBLIC_KEY_PATH'))
    
    # Carrega o conteúdo das chaves para o config do app
    with open(priv_path, 'r') as f:
        app.config['JWT_PRIVATE_PEM'] = f.read()
    with open(pub_path, 'r') as f:
        app.config['JWT_PUBLIC_PEM'] = f.read()
    
    # Carrega a chave AES
    app.config['AES_SECRET_KEY'] = os.getenv('AES_SECRET_KEY')

if __name__ == '__main__':
    app = create_app()
    setup_security_configs(app)
    app.run(debug=True, host="0.0.0.0")