"""
Rotas ML-Ready para pipeline de Machine Learning
"""

from flask_restx import Namespace, Resource, fields
from flask import request
from .models import BookRepository
from .ml_pipeline import MLPipeline
from .auth import ml_permission_required, token_required

# Namespace para ML
ml_ns = Namespace('api/v1/ml', description='Endpoints para Machine Learning')

# Instância global do pipeline (em produção, usar cache ou banco)
ml_pipeline_instance = None

# Modelos para documentação Swagger
prediction_input_model = ml_ns.model('PredictionInput', {
    'data': fields.List(fields.Raw, required=True, description='Lista de dados para predição')
})

prediction_response_model = ml_ns.model('PredictionResponse', {
    'predictions': fields.List(fields.Raw, description='Lista de predições'),
    'model_type': fields.String(description='Tipo do modelo usado'),
    'total_predictions': fields.Integer(description='Número total de predições')
})

features_response_model = ml_ns.model('FeaturesResponse', {
    'features': fields.List(fields.Raw, description='Features processadas'),
    'feature_names': fields.List(fields.String, description='Nomes das features'),
    'shape': fields.List(fields.Integer, description='Dimensões dos dados'),
    'statistics': fields.Raw(description='Estatísticas das features')
})

training_response_model = ml_ns.model('TrainingResponse', {
    'X_train': fields.List(fields.Raw, description='Dados de treino (features)'),
    'X_test': fields.List(fields.Raw, description='Dados de teste (features)'),
    'y_train': fields.List(fields.Raw, description='Labels de treino'),
    'y_test': fields.List(fields.Raw, description='Labels de teste'),
    'feature_names': fields.List(fields.String, description='Nomes das features'),
    'target_column': fields.String(description='Coluna target'),
    'train_size': fields.Integer(description='Tamanho do conjunto de treino'),
    'test_size': fields.Integer(description='Tamanho do conjunto de teste')
})

def get_ml_pipeline():
    """Obtém instância do pipeline ML"""
    global ml_pipeline_instance
    
    if ml_pipeline_instance is None:
        # Carrega dados dos livros
        book_repo = BookRepository()
        books = book_repo.get_all_books()
        books_data = [book.to_dict() for book in books]
        ml_pipeline_instance = MLPipeline(books_data)
    
    return ml_pipeline_instance

@ml_ns.route('/features')
class MLFeatures(Resource):
    @ml_ns.marshal_with(features_response_model)
    @ml_ns.doc('get_ml_features')
    @ml_permission_required
    def get(self):
        """Retorna dados formatados para features de ML"""
        try:
            pipeline = get_ml_pipeline()
            result = pipeline.prepare_features()
            
            if 'error' in result:
                return {'error': result['error']}, 400
            
            return result, 200
            
        except Exception as e:
            return {'error': f'Erro interno: {str(e)}'}, 500

@ml_ns.route('/training-data')
class MLTrainingData(Resource):
    @ml_ns.marshal_with(training_response_model)
    @ml_ns.doc('get_training_data')
    @ml_permission_required
    def get(self):
        """Retorna dataset preparado para treinamento"""
        try:
            target = request.args.get('target', 'rating')
            
            pipeline = get_ml_pipeline()
            result = pipeline.prepare_training_data(target)
            
            if 'error' in result:
                return {'error': result['error']}, 400
            
            return result, 200
            
        except Exception as e:
            return {'error': f'Erro interno: {str(e)}'}, 500

@ml_ns.route('/train')
class MLTrain(Resource):
    @ml_ns.doc('train_model')
    @ml_permission_required
    def post(self):
        """Treina um modelo de exemplo com os dados"""
        try:
            data = request.get_json() or {}
            target = data.get('target', 'rating')
            
            pipeline = get_ml_pipeline()
            result = pipeline.train_model(target)
            
            if 'error' in result:
                return {'error': result['error']}, 400
            
            return result, 200
            
        except Exception as e:
            return {'error': f'Erro interno: {str(e)}'}, 500

@ml_ns.route('/predictions')
class MLPredictions(Resource):
    @ml_ns.expect(prediction_input_model)
    @ml_ns.marshal_with(prediction_response_model)
    @ml_ns.doc('make_predictions')
    @ml_permission_required
    def post(self):
        """Faz predições usando modelo treinado"""
        try:
            data = request.get_json()
            
            if not data or 'data' not in data:
                return {'error': 'Campo "data" é obrigatório'}, 400
            
            input_data = data['data']
            
            if not isinstance(input_data, list):
                return {'error': 'Campo "data" deve ser uma lista'}, 400
            
            pipeline = get_ml_pipeline()
            result = pipeline.predict(input_data)
            
            if 'error' in result:
                return {'error': result['error']}, 400
            
            return result, 200
            
        except Exception as e:
            return {'error': f'Erro interno: {str(e)}'}, 500

@ml_ns.route('/model-info')
class MLModelInfo(Resource):
    @ml_ns.doc('get_model_info')
    @ml_permission_required
    def get(self):
        """Retorna informações sobre o modelo atual"""
        try:
            pipeline = get_ml_pipeline()
            result = pipeline.get_model_info()
            
            return result, 200
            
        except Exception as e:
            return {'error': f'Erro interno: {str(e)}'}, 500

@ml_ns.route('/example-prediction')
class MLExamplePrediction(Resource):
    @ml_ns.doc('example_prediction')
    @token_required()
    def get(self):
        """Exemplo de como usar o endpoint de predições"""
        example_input = {
            "data": [
                {
                    "title": "Example Book",
                    "price": 25.99,
                    "rating": 4,
                    "category": "Fiction",
                    "availability": "In stock"
                },
                {
                    "title": "Another Book",
                    "price": 15.50,
                    "rating": 3,
                    "category": "Science",
                    "availability": "In stock"
                }
            ]
        }
        
        return {
            'message': 'Exemplo de input para /api/v1/ml/predictions',
            'method': 'POST',
            'headers': {
                'Authorization': 'Bearer <your-jwt-token>',
                'Content-Type': 'application/json'
            },
            'body': example_input,
            'note': 'Certifique-se de treinar o modelo primeiro com POST /api/v1/ml/train'
        }, 200

@ml_ns.route('/reset')
class MLReset(Resource):
    @ml_ns.doc('reset_pipeline')
    @ml_permission_required
    def post(self):
        """Reseta o pipeline ML (recarrega dados)"""
        try:
            global ml_pipeline_instance
            ml_pipeline_instance = None
            
            return {
                'success': True,
                'message': 'Pipeline ML resetado com sucesso'
            }, 200
            
        except Exception as e:
            return {'error': f'Erro interno: {str(e)}'}, 500