from flask import current_app
import jwt
import datetime
import traceback

# ----------------------------------------------------
# 3. CRIPTOGRAFIA ASSIMÉTRICA (JWT - RS256)
# ----------------------------------------------------

def issue_token(user_id: int, comp_id: int, is_admin: bool, is_agent: bool) -> str:
    """ Create a new token with user information """
    payload = {
        'user_id': user_id,
        'comp_id': comp_id,
        'is_admin': is_admin,
        'is_agent': is_agent,
        # ✅ ADICIONADO: Expiração para evitar Replay Attacks (Mitigação de segurança)
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    
    # Busca a string da chave privada carregada no appserver.py a partir do ficheiro .pem
    private_key = current_app.config.get('JWT_PRIVATE_PEM')
    
    if private_key:
        try:
            # ✅ RS256: Assinatura com a chave privada
            token = jwt.encode(payload, key=private_key, algorithm='RS256')
            # Compatibilidade de versão (PyJWT >= 2.0 retorna str, < 2.0 retorna bytes)
            str_token = token.decode('utf-8') if isinstance(token, (bytes, bytearray)) else token
            return str_token
        except Exception as e:
            raise Exception('Issue RS256 token failed', e) from e

def validate_token(token: str):
    """ Validate JWT token using RSA Public Key """
    if not token:
        return False, None
        
    try:
        # Verifica se o header está íntegro
        jwt.get_unverified_header(token)
    except Exception as e:
        print("Error decoding header", e)
        return False, None

    try:
        # Busca a string da chave pública carregada no appserver.py a partir do ficheiro .pem
        public_key_pem = current_app.config.get('JWT_PUBLIC_PEM', '')
        
        if public_key_pem:
            # ✅ IMPORTANTE: algorithms=['RS256'] força o uso de criptografia assimétrica
            # Isso impede o ataque de "Algorithm Confusion"
            payload = jwt.decode(
                token,
                key=public_key_pem,
                algorithms=['RS256'] 
            )
            return True, payload
    except jwt.ExpiredSignatureError:
        print("Token has expired")
    except Exception as e:
        print("Error decoding RS256 with public key", e)
    
    return False, None
