"""
Sistema de autenticação JWT para a Books API
"""

import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
import bcrypt
import os

# Chave secreta para JWT (em produção, use variável de ambiente)
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Usuários hardcoded para demonstração (em produção, use banco de dados)
USERS_DB = {
    'admin': {
        'password_hash': bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()),
        'role': 'admin',
        'permissions': ['read', 'write', 'admin']
    },
    'scientist': {
        'password_hash': bcrypt.hashpw('science123'.encode('utf-8'), bcrypt.gensalt()),
        'role': 'data_scientist',
        'permissions': ['read', 'ml']
    },
    'user': {
        'password_hash': bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()),
        'role': 'user',
        'permissions': ['read']
    }
}

class AuthManager:
    """Gerenciador de autenticação JWT"""
    
    @staticmethod
    def generate_token(username: str, role: str, permissions: list) -> str:
        """Gera um token JWT para o usuário"""
        payload = {
            'username': username,
            'role': role,
            'permissions': permissions,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.datetime.utcnow()
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verifica e decodifica um token JWT"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return {'valid': True, 'payload': payload}
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expirado'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Token inválido'}
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> dict:
        """Autentica usuário com username e senha"""
        if username not in USERS_DB:
            return {'success': False, 'error': 'Usuário não encontrado'}
        
        user = USERS_DB[username]
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            token = AuthManager.generate_token(
                username, 
                user['role'], 
                user['permissions']
            )
            return {
                'success': True,
                'token': token,
                'user': {
                    'username': username,
                    'role': user['role'],
                    'permissions': user['permissions']
                }
            }
        else:
            return {'success': False, 'error': 'Senha incorreta'}
    
    @staticmethod
    def refresh_token(token: str) -> dict:
        """Renova um token JWT válido"""
        verification = AuthManager.verify_token(token)
        
        if not verification['valid']:
            return {'success': False, 'error': verification['error']}
        
        payload = verification['payload']
        new_token = AuthManager.generate_token(
            payload['username'],
            payload['role'],
            payload['permissions']
        )
        
        return {
            'success': True,
            'token': new_token,
            'user': {
                'username': payload['username'],
                'role': payload['role'],
                'permissions': payload['permissions']
            }
        }

def token_required(required_permission=None):
    """Decorator para proteger rotas que requerem autenticação"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verifica se o token está presente
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({
                    'error': 'Token de acesso requerido',
                    'message': 'Inclua o header: Authorization: Bearer <token>'
                }), 401
            
            # Extrai o token do header "Bearer <token>"
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({
                    'error': 'Formato de token inválido',
                    'message': 'Use: Authorization: Bearer <token>'
                }), 401
            
            # Verifica o token
            verification = AuthManager.verify_token(token)
            
            if not verification['valid']:
                return jsonify({
                    'error': 'Token inválido',
                    'message': verification['error']
                }), 401
            
            # Verifica permissões se especificado
            if required_permission:
                user_permissions = verification['payload'].get('permissions', [])
                if required_permission not in user_permissions:
                    return jsonify({
                        'error': 'Permissão insuficiente',
                        'message': f'Requer permissão: {required_permission}',
                        'user_permissions': user_permissions
                    }), 403
            
            # Adiciona informações do usuário ao request
            request.current_user = verification['payload']
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator para rotas que requerem privilégios de admin"""
    return token_required('admin')(f)

def ml_permission_required(f):
    """Decorator para rotas ML que requerem permissão específica"""
    return token_required('ml')(f)