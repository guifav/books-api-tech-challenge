"""
Pipeline ML-Ready para preparação de dados e integração com modelos
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class MLPipeline:
    """Pipeline para preparação de dados e treinamento de modelos ML"""
    
    def __init__(self, books_data: List[Dict]):
        self.books_data = books_data
        self.df = pd.DataFrame(books_data) if books_data else pd.DataFrame()
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.model = None
        self.model_trained = False
        
    def prepare_features(self) -> Dict[str, Any]:
        """Prepara features para ML"""
        if self.df.empty:
            return {'error': 'Nenhum dado disponível'}
        
        try:
            # Cria uma cópia para não modificar os dados originais
            ml_df = self.df.copy()
            
            # Features numéricas
            numerical_features = ['price', 'rating']
            
            # Features categóricas
            categorical_features = ['category', 'availability']
            
            # Engenharia de features
            ml_df['title_length'] = ml_df['title'].str.len()
            ml_df['title_word_count'] = ml_df['title'].str.split().str.len()
            ml_df['price_per_rating'] = ml_df['price'] / (ml_df['rating'] + 1)  # +1 para evitar divisão por zero
            ml_df['is_expensive'] = (ml_df['price'] > ml_df['price'].quantile(0.75)).astype(int)
            ml_df['is_high_rated'] = (ml_df['rating'] >= 4).astype(int)
            
            # Encoding de variáveis categóricas
            for col in categorical_features:
                if col in ml_df.columns:
                    le = LabelEncoder()
                    ml_df[f'{col}_encoded'] = le.fit_transform(ml_df[col].astype(str))
                    self.label_encoders[col] = le
            
            # Features finais
            feature_columns = (
                numerical_features + 
                ['title_length', 'title_word_count', 'price_per_rating', 'is_expensive', 'is_high_rated'] +
                [f'{col}_encoded' for col in categorical_features if col in ml_df.columns]
            )
            
            features_df = ml_df[feature_columns].fillna(0)
            
            return {
                'features': features_df.to_dict('records'),
                'feature_names': feature_columns,
                'shape': features_df.shape,
                'statistics': {
                    'mean': features_df.mean().to_dict(),
                    'std': features_df.std().to_dict(),
                    'min': features_df.min().to_dict(),
                    'max': features_df.max().to_dict()
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao preparar features: {e}")
            return {'error': f'Erro ao preparar features: {str(e)}'}
    
    def prepare_training_data(self, target_column: str = 'rating') -> Dict[str, Any]:
        """Prepara dados para treinamento de modelo"""
        if self.df.empty:
            return {'error': 'Nenhum dado disponível'}
        
        try:
            features_result = self.prepare_features()
            if 'error' in features_result:
                return features_result
            
            features_df = pd.DataFrame(features_result['features'])
            
            # Target
            if target_column not in self.df.columns:
                return {'error': f'Coluna target {target_column} não encontrada'}
            
            target = self.df[target_column].fillna(0)
            
            # Split train/test
            X_train, X_test, y_train, y_test = train_test_split(
                features_df, target, test_size=0.2, random_state=42
            )
            
            # Normalização
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            return {
                'X_train': X_train_scaled.tolist(),
                'X_test': X_test_scaled.tolist(),
                'y_train': y_train.tolist(),
                'y_test': y_test.tolist(),
                'feature_names': features_result['feature_names'],
                'target_column': target_column,
                'train_size': len(X_train),
                'test_size': len(X_test),
                'target_statistics': {
                    'mean': float(target.mean()),
                    'std': float(target.std()),
                    'min': float(target.min()),
                    'max': float(target.max())
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao preparar dados de treinamento: {e}")
            return {'error': f'Erro ao preparar dados de treinamento: {str(e)}'}
    
    def train_model(self, target_column: str = 'rating') -> Dict[str, Any]:
        """Treina um modelo de exemplo (Random Forest)"""
        try:
            training_data = self.prepare_training_data(target_column)
            if 'error' in training_data:
                return training_data
            
            X_train = np.array(training_data['X_train'])
            y_train = np.array(training_data['y_train'])
            X_test = np.array(training_data['X_test'])
            y_test = np.array(training_data['y_test'])
            
            # Treina modelo Random Forest
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Predições
            y_pred_train = self.model.predict(X_train)
            y_pred_test = self.model.predict(X_test)
            
            # Métricas
            train_mse = mean_squared_error(y_train, y_pred_train)
            test_mse = mean_squared_error(y_test, y_pred_test)
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            
            # Feature importance
            feature_importance = dict(zip(
                training_data['feature_names'],
                self.model.feature_importances_
            ))
            
            self.model_trained = True
            
            return {
                'model_trained': True,
                'target_column': target_column,
                'metrics': {
                    'train_mse': float(train_mse),
                    'test_mse': float(test_mse),
                    'train_r2': float(train_r2),
                    'test_r2': float(test_r2)
                },
                'feature_importance': feature_importance,
                'model_type': 'RandomForestRegressor',
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo: {e}")
            return {'error': f'Erro ao treinar modelo: {str(e)}'}
    
    def predict(self, input_data: List[Dict]) -> Dict[str, Any]:
        """Faz predições usando o modelo treinado"""
        if not self.model_trained or self.model is None:
            return {'error': 'Modelo não foi treinado. Execute /api/v1/ml/train primeiro'}
        
        try:
            # Converte input para DataFrame
            input_df = pd.DataFrame(input_data)
            
            # Prepara features da mesma forma que no treinamento
            # Engenharia de features
            input_df['title_length'] = input_df['title'].str.len()
            input_df['title_word_count'] = input_df['title'].str.split().str.len()
            input_df['price_per_rating'] = input_df['price'] / (input_df['rating'] + 1)
            input_df['is_expensive'] = (input_df['price'] > input_df['price'].quantile(0.75)).astype(int)
            input_df['is_high_rated'] = (input_df['rating'] >= 4).astype(int)
            
            # Encoding categórico
            categorical_features = ['category', 'availability']
            for col in categorical_features:
                if col in input_df.columns and col in self.label_encoders:
                    try:
                        input_df[f'{col}_encoded'] = self.label_encoders[col].transform(input_df[col].astype(str))
                    except ValueError:
                        # Valor não visto durante treinamento - usa valor padrão
                        input_df[f'{col}_encoded'] = 0
            
            # Features finais
            numerical_features = ['price', 'rating']
            feature_columns = (
                numerical_features + 
                ['title_length', 'title_word_count', 'price_per_rating', 'is_expensive', 'is_high_rated'] +
                [f'{col}_encoded' for col in categorical_features if col in input_df.columns]
            )
            
            features_df = input_df[feature_columns].fillna(0)
            
            # Normalização
            features_scaled = self.scaler.transform(features_df)
            
            # Predição
            predictions = self.model.predict(features_scaled)
            
            # Confiança (baseada na variância das árvores)
            if hasattr(self.model, 'estimators_'):
                tree_predictions = np.array([tree.predict(features_scaled) for tree in self.model.estimators_])
                confidence = 1 / (1 + np.std(tree_predictions, axis=0))
            else:
                confidence = [0.5] * len(predictions)
            
            results = []
            for i, pred in enumerate(predictions):
                results.append({
                    'prediction': float(pred),
                    'confidence': float(confidence[i]),
                    'input_data': input_data[i] if i < len(input_data) else None
                })
            
            return {
                'predictions': results,
                'model_type': 'RandomForestRegressor',
                'total_predictions': len(results)
            }
            
        except Exception as e:
            logger.error(f"Erro ao fazer predições: {e}")
            return {'error': f'Erro ao fazer predições: {str(e)}'}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo"""
        return {
            'model_trained': self.model_trained,
            'model_type': 'RandomForestRegressor' if self.model else None,
            'data_available': not self.df.empty,
            'total_samples': len(self.df) if not self.df.empty else 0,
            'features_available': list(self.df.columns) if not self.df.empty else [],
            'label_encoders': list(self.label_encoders.keys())
        }