"""
Rotas de autenticação para a Books API
"""

from flask_restx import Namespace, Resource, fields
from flask import request
from .auth import AuthManager, token_required

# Namespace para autenticação
auth_ns = Namespace('api/v1/auth', description='Autenticação e autorização')

# Modelos para documentação Swagger
login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='Nome de usuário'),
    'password': fields.String(required=True, description='Senha do usuário')
})

token_response_model = auth_ns.model('TokenResponse', {
    'success': fields.Boolean(description='Status da operação'),
    'token': fields.String(description='Token JWT'),
    'user': fields.Raw(description='Informações do usuário'),
    'expires_in': fields.String(description='Tempo de expiração do token')
})

refresh_model = auth_ns.model('RefreshToken', {
    'token': fields.String(required=True, description='Token JWT para renovação')
})

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.marshal_with(token_response_model)
    @auth_ns.doc('user_login')
    def post(self):
        """Autentica usuário e retorna token JWT"""
        try:
            data = request.get_json()
            
            if not data or 'username' not in data or 'password' not in data:
                return {
                    'success': False,
                    'error': 'Username e password são obrigatórios'
                }, 400
            
            result = AuthManager.authenticate_user(
                data['username'], 
                data['password']
            )
            
            if result['success']:
                return {
                    'success': True,
                    'token': result['token'],
                    'user': result['user'],
                    'expires_in': '24 hours',
                    'message': 'Login realizado com sucesso'
                }, 200
            else:
                return {
                    'success': False,
                    'error': result['error']
                }, 401
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }, 500

@auth_ns.route('/refresh')
class RefreshToken(Resource):
    @auth_ns.expect(refresh_model)
    @auth_ns.marshal_with(token_response_model)
    @auth_ns.doc('refresh_token')
    def post(self):
        """Renova um token JWT válido"""
        try:
            data = request.get_json()
            
            if not data or 'token' not in data:
                return {
                    'success': False,
                    'error': 'Token é obrigatório'
                }, 400
            
            result = AuthManager.refresh_token(data['token'])
            
            if result['success']:
                return {
                    'success': True,
                    'token': result['token'],
                    'user': result['user'],
                    'expires_in': '24 hours',
                    'message': 'Token renovado com sucesso'
                }, 200
            else:
                return {
                    'success': False,
                    'error': result['error']
                }, 401
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }, 500

@auth_ns.route('/verify')
class VerifyToken(Resource):
    @auth_ns.doc('verify_token')
    @token_required()
    def get(self):
        """Verifica se o token é válido"""
        return {
            'success': True,
            'message': 'Token válido',
            'user': {
                'username': request.current_user['username'],
                'role': request.current_user['role'],
                'permissions': request.current_user['permissions']
            }
        }, 200

@auth_ns.route('/users')
class ListUsers(Resource):
    @auth_ns.doc('list_users')
    @token_required('admin')
    def get(self):
        """Lista usuários disponíveis (apenas admin)"""
        from .auth import USERS_DB
        
        users = []
        for username, user_data in USERS_DB.items():
            users.append({
                'username': username,
                'role': user_data['role'],
                'permissions': user_data['permissions']
            })
        
        return {
            'success': True,
            'users': users,
            'total': len(users)
        }, 200