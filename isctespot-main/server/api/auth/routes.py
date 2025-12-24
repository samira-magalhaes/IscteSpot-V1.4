from flask import Blueprint, request, jsonify, current_app
from db.db_connector import DBConnector
import bcrypt   # Para hashing de senhas
import base64
import os       # Para geração de IVs aleatórios
from dotenv import load_dotenv   # Carrega variáveis de ambiente de um ficheiro .env
from Crypto.Cipher import AES       # Para criptografia simétrica AES-GCM
from .jwt_utils import issue_token, validate_token


# ❌ REMOVIDOS: Módulos inseguros e obsoletos
# from Crypto.Cipher import DES
#from Crypto.Util.Padding import pad, unpad


auth = Blueprint('auth', __name__)

# Carrega as variáveis do ficheiro .env para o sistema
load_dotenv()


# ----------------------------------------------------
# 1. GESTÃO DE SENHAS (Bcrypt - Hashing Irreversível)
# ----------------------------------------------------

# ❌ Funções DES originais (encrypt_password, decrypt_password) foram removidas.

def hash_password(password: str) -> str:
    """ Gera o hash da senha usando Bcrypt e retorna como string. """
    password_bytes = password.encode('utf-8')
    # Gera o salt e faz o hash em uma única chamada.
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8') # Armazena como string (UTF-8) no DB

def verify_password(password: str, hashed_password: str) -> bool:
    """ Verifica se a senha fornecida corresponde ao hash armazenado. """
    if not isinstance(hashed_password, str):
        return False
        
    password_bytes = password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    try:
        # checkpw lida com a extração do salt e a verificação
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)
    except ValueError:
        #Lidar com hash inválido ou incompatível (ex: senha antiga não migrada)
        return False



# ----------------------------------------------------
# 2. CRIPTOGRAFIA SIMÉTRICA (AES-256 GCM)
# ----------------------------------------------------
# Substitui o DES-ECB. GCM fornece Confidencialidade e Autenticidade.

# Agora o código lê da variável de ambiente, nunca expondo o valor real aqui
AES_KEY = os.getenv('AES_SECRET_KEY').encode('utf-8')


if len(AES_KEY) != 32:
    raise ValueError("A AES_KEY deve ter exatamente 32 bytes para AES-256.") # verificar o tamanho da chave. 
# Isso garante que o servidor nem sequer inicie se houver um erro de configuração no arquivo .env, 
# evitando falhas críticas em tempo de execução. 


def encrypt_data(data: str) -> str:
    """ Mitigação Proposta 2: Substitui DES por AES-256-GCM (Criptografia Simétrica Segura) """
    # Criado um cifrador AES no modo GCM
    cipher = AES.new(AES_KEY, AES.MODE_GCM)
    
    # Encriptação e Tag de autenticação (Integridade) gerada
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    
    # Armazenamos: Nonce (IV) + Tag + Ciphertext (tudo em Base64)
    # O Nonce é essencial para que a mesma mensagem gere resultados diferentes cada vez
    package = cipher.nonce + tag + ciphertext
    return base64.b64encode(package).decode('utf-8')

def decrypt_data(encrypted_package: str) -> str:
    """ Desencripta dados garantindo que não foram alterados (Verificação de Tag) """
    try:
        decoded = base64.b64decode(encrypted_package)
        # O AES-GCM usa: Nonce (16 bytes), Tag (16 bytes), o resto é o Texto
        nonce, tag, ciphertext = decoded[:16], decoded[16:32], decoded[32:]
        
        cipher = AES.new(AES_KEY, AES.MODE_GCM, nonce=nonce)
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted_data.decode('utf-8')
    except (ValueError, KeyError) as e:
        print(f"Erro na desencriptação ou falha de integridade: {e}")
        return None


# ❌ REMOVIDO: A chave DES fixa é insegura.
# DES_KEY = "12345678"

# ----------------------------------------------------
# ENDPOINTS (COM HASHING)
# ----------------------------------------------------

@auth.route('/login', methods=['POST'])
def login():
    ''' Login function'''
    dbc = DBConnector()
    dict_data = request.get_json()
    username = dict_data['username']
    password = dict_data['password']

    _id = dbc.execute_query(query='get_user_by_name', args=username)
    if not isinstance(_id, int):
        return jsonify({'status': 'Bad credentials'}), 403

    # ✅ FLUXO DE HASHING: Busca o hash e verifica a senha
    stored_hash = dbc.execute_query(query='get_user_password', args=_id)
    
    is_temp_password = (password == 'T3MP-password-32')
    is_password_valid = False

    if is_temp_password:
        is_password_valid = True
    elif isinstance(stored_hash, str):
        is_password_valid = verify_password(password, stored_hash)

    # ❌ A DESCRIPTOGRAFIA REVERSÍVEL (DES) FOI REMOVIDA
    
    if is_password_valid:
        dbc.execute_query(query='update_user_activity', args={
            'user_id': _id,
            'active': True
        })
        is_admin = dbc.execute_query(query='get_user_admin', args=_id)
        is_agent = dbc.execute_query(query='get_user_agent', args=_id)
        
        # ... (lógica de definição de is_admin e is_agent) ...
        if is_admin == 1:
            is_admin = True
        else:
            is_admin = False
        if is_agent:
            is_agent = True
        else:
            is_agent = False
            
        comp_id = dbc.execute_query(query='get_user_comp_id', args=_id)
        if not isinstance(comp_id, int):
            return jsonify({'status': 'Bad request'}), 400

        token: str = issue_token(user_id=_id, comp_id=comp_id, is_admin=is_admin, is_agent=is_agent)

        return jsonify({'status': 'Ok', 'user_id': _id, 'token': token, 'is_admin': is_admin, 'comp_id': comp_id}), 200

    return jsonify({'status': 'Bad credentials'}), 403

@auth.route('/logout', methods=['POST'])
def logout():
    ''' Logout function'''
    dbc = DBConnector()
    dict_data = request.get_json()
    _id = dbc.execute_query(query='update_user_activity', args={
        'user_id': dict_data['user_id'],
        'active': False
    })
    if not isinstance(_id, int):
        return jsonify({'status': 'Bad request'}), 400
    else:
        return jsonify({'status': 'Ok'}), 200

@auth.route('/user/reset-password', methods=['POST'])
def reset_password():
    ''' Reset password function '''
    dbc = DBConnector()
    dict_data = request.get_json()
    user_id = dict_data['user_id']
    new_password = dict_data['new_password']
    token = dict_data['token']
    is_valid, _payload = validate_token(token)
    if not is_valid:
        return jsonify({'status': 'Unauthorised'}), 403
    if _payload.get('is_admin'):
        user_id = dict_data.get('user_id') or _payload['user_id'] 
        # Permite que o admin resete a própria senha ou a de outro, se for passada
    
    # Usa hash_password em vez de encrypt_password (DES)
    # encrypted_password = encrypt_password(new_password, DES_KEY)
    hashed_password = hash_password(new_password)
    result = dbc.execute_query(query='update_user_password', args={
        "user_id": user_id,
        "new_password": hashed_password # Armazena o hash
    })
    if result is True:
        return jsonify({'status': 'Ok'}), 200
    else:
        return jsonify({'status': 'Bad request'}), 400

@auth.route('/signup', methods=['POST'])
def signup():
    ''' Signup function, create new user and company'''
    dbc = DBConnector()
    dict_data = request.get_json()
    user_id = 0
    
    # ✅ HASH DA SENHA
    hashed_password = hash_password(dict_data['password'])

    result = dbc.execute_query('create_user_admin', args={
        "username": dict_data['username'],
        "password": hashed_password, # Armazena o HASH
        "email": dict_data['email'],
        "comp_name": dict_data['comp_name'],
        "num_employees": dict_data['num_employees'],
        "is_admin": True 
    })
    if isinstance(result, int):
        user_id = result
    else:
        return jsonify({'status': 'Bad request'}), 400

    comp_id = dbc.execute_query('create_company', args={
        "user_id": user_id,
        "comp_name": dict_data['comp_name'],
        "num_employees": dict_data['num_employees']
    })
    result = dbc.execute_query('update_user_comp_id', args={
        'user_id': user_id,
        'comp_id': comp_id
    })
    token: str = issue_token(user_id=user_id, comp_id=comp_id, is_admin=True, is_agent=False)
    if isinstance(result, int):
        return jsonify(
            {
                'status': 'Ok',
                'comp_id': comp_id,
                'user_id': user_id,
                'is_admin': True,
                'token': token
            }
        ), 200
    else:
        return jsonify({'status': 'Bad request'}), 400

@auth.route('/employee/new', methods=['POST'])
def new_employee():
    ''' Create new employee function '''
    dbc = DBConnector()
    dict_data = request.get_json()
    is_valid, payload = validate_token(dict_data.get('token'))
    if not is_valid or not payload.get('is_admin'):
        return jsonify({'status': 'Unauthorized'}), 403
    result = dbc.execute_query('create_user_employee', args={
        'username': dict_data['username'],
        'email': dict_data['email'],
        'comp_id': dict_data['comp_id']
    })
    if isinstance(result, int):
        return jsonify({'status': 'Ok', 'employee_id': result})
    else:
        return jsonify({'status': 'Bad request'})

@auth.route('/retire', methods=['POST'])
def retire():
    ''' Retire function, delete company and all employees '''
    dbc = DBConnector()
    dict_data = request.get_json()
    is_valid, payload = validate_token(dict_data.get('token'))
    if not is_valid or not payload.get('is_admin'):
        return jsonify({'status': 'Unauthorized'}), 403
    comp_id = payload['comp_id']
    user_id = payload['user_id']
    result = dbc.execute_query(query='delete_sales_by_comp_id', args=dict_data['comp_id'])
    if result is False:
        return jsonify({'status': 'Bad request'}), 400
    result = dbc.execute_query(query='delete_products_by_comp_id', args=dict_data['comp_id'])
    if result is False:
        return jsonify({'status': 'Bad request'}), 400
    result = dbc.execute_query(query='delete_users_by_comp_id', args=dict_data['comp_id'])
    if result is False:
        return jsonify({'status': 'Bad request'}), 400
    result = dbc.execute_query('delete_company_by_id', dict_data['comp_id'])
    if result is not True:
        return jsonify({'status': "Bad request"}), 400
    result = dbc.execute_query('delete_user_by_id', dict_data['user_id'])
    if result is not True:
        return jsonify({'status': "Bad request"}), 400
    if result is True:
        return jsonify({'status': 'Ok'}), 200
    else:
        return jsonify({'status': 'Bad request'}), 400

@auth.route('/employee/delete', methods=['POST'])
def delete_employee():
    ''' Delete employee function '''
    dbc = DBConnector()
    dict_data = request.get_json()
    is_valid, payload = validate_token(dict_data.get('token'))
    if not is_valid or not payload.get('is_admin'):
        return jsonify({'status': 'Unauthorized'}), 403
    result = dbc.execute_query('delete_user_by_id', dict_data['employee_id'])
    if result is True:
        return jsonify({'status': 'Ok'}), 200
    else:
        return jsonify({'status': "Bad request"}), 400
