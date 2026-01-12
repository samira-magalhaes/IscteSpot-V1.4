import os                                      # <-- ADICIONADO
from flask_cors import CORS
from flask import Flask
from api.auth.routes import auth
from api.company.routes import company
from api.sales.routes import sales
from api.clients.routes import clients
from api.admin.routes import admin


def create_app():                              # <-- ALTERADO (removido settings.py)
    ''' Create and configure the Flask application '''
    app = Flask(__name__)

    # --- Configuração opcional via settings.py (se existir) ---
    settings_path = os.path.join(              # <-- ADICIONADO
        os.path.dirname(__file__),
        'settings.py'
    )

    if os.path.exists(settings_path):          # <-- ADICIONADO
        app.config.from_pyfile(settings_path)

    # --- CORS ---
    CORS(auth, origins=["*"])
    CORS(clients, origins=["*"])
    CORS(sales, origins=["*"])
    CORS(company, origins=["*"])
    CORS(admin, origins=["*"])

    # --- Blueprints ---
    app.register_blueprint(auth)
    app.register_blueprint(company)
    app.register_blueprint(sales)
    app.register_blueprint(clients)
    app.register_blueprint(admin)

    # --- Health check ---
    @app.route('/health', methods=['GET'])
    def health_check():
        return {
            'status': 'healthy',
            'message': 'ISCTE Spot API is running',
        }, 200

    return app
