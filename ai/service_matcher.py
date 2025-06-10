import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from typing import List, Dict, Tuple, Optional
import pandas as pd

class ServiceMatcher:
    def __init__(self):
        self.agent_features = {}  # Store agent performance features
        self.service_history = []
        self.models = {}  # ML models for different services
        self.is_trained = False
        
    def add_agent_features(self, agent_name: str, features: Dict):
        """Add/update agent features for matching"""
        self.agent_features[agent_name] = {
            'success_rate': features.get('success_rate', 0.9),
            'avg_response_time': features.get('response_time', 2.0),
            'reputation': features.get('reputation', 3.0),
            'price_competitiveness': features.get('price_competitiveness', 0.5),
            'specialization_score': features.get('specialization_score', 0.5),
            'availability': features.get('availability', 0.8)
        }
    
    def record_service_outcome(self, agent_name: str, service_type: str, 
                             client_satisfaction: float, completion_time: float,
                             price_paid: int, market_price: int):
        """Record service outcome for training"""
        if agent_name in self.agent_features:
            features = self.agent_features[agent_name].copy()
            features.update({
                'service_type': service_type,
                'price_ratio': price_paid / max(market_price, 1),
                'completion_time': completion_time,
                'satisfaction': client_satisfaction
            })
            self.service_history.append(features)
    
    def train_models(self):
        """Train ML models for service matching"""
        if len(self.service_history) < 10:  # Need minimum data
            return False
        
        df = pd.DataFrame(self.service_history)
        
        # Prepare features and targets
        feature_cols = ['success_rate', 'avg_response_time', 'reputation', 
                       'price_competitiveness', 'specialization_score', 
                       'availability', 'price_ratio']
        
        X = df[feature_cols].fillna(0)
        
        # Train different models for different criteria
        # 1. Overall satisfaction prediction
        y_satisfaction = (df['satisfaction'] > 0.7).astype(int)
        self.models['satisfaction'] = RandomForestClassifier(n_estimators=50, random_state=42)
        self.models['satisfaction'].fit(X, y_satisfaction)
        
        # 2. Fast completion prediction
        y_fast = (df['completion_time'] < df['completion_time'].median()).astype(int)
        self.models['speed'] = LogisticRegression(random_state=42)
        self.models['speed'].fit(X, y_fast)
        
        # 3. Value for money prediction
        df['value_score'] = df['satisfaction'] / (df['price_ratio'] + 0.1)
        y_value = (df['value_score'] > df['value_score'].median()).astype(int)
        self.models['value'] = RandomForestClassifier(n_estimators=30, random_state=42)
        self.models['value'].fit(X, y_value)
        
        self.is_trained = True
        return True
    
    def rank_agents(self, available_agents: List[str], service_type: str, 
                   criteria: str = 'satisfaction', market_price: int = 10) -> List[Tuple[str, float]]:
        """Rank agents based on criteria using ML predictions"""
        if not self.is_trained or criteria not in self.models:
            # Fallback to simple ranking
            return self._simple_ranking(available_agents, criteria)
        
        agent_scores = []
        for agent in available_agents:
            if agent in self.agent_features:
                features = self.agent_features[agent].copy()
                # Add contextual features
                features['price_ratio'] = features.get('base_price', market_price) / market_price
                
                feature_vector = np.array([[
                    features['success_rate'],
                    features['avg_response_time'],
                    features['reputation'],
                    features['price_competitiveness'],
                    features['specialization_score'],
                    features['availability'],
                    features['price_ratio']
                ]])
                
                # Get prediction probability
                score = self.models[criteria].predict_proba(feature_vector)[0][1]
                agent_scores.append((agent, score))
        
        return sorted(agent_scores, key=lambda x: x[1], reverse=True)
    
    def _simple_ranking(self, available_agents: List[str], criteria: str) -> List[Tuple[str, float]]:
        """Simple fallback ranking when ML models aren't available"""
        agent_scores = []
        for agent in available_agents:
            if agent in self.agent_features:
                features = self.agent_features[agent]
                if criteria == 'satisfaction':
                    score = (features['success_rate'] * 0.4 + 
                            features['reputation'] / 5.0 * 0.6)
                elif criteria == 'speed':
                    score = 1.0 / (features['avg_response_time'] + 0.1)
                elif criteria == 'value':
                    score = (features['success_rate'] * features['price_competitiveness'])
                else:
                    score = features['reputation'] / 5.0
                
                agent_scores.append((agent, score))
        
        return sorted(agent_scores, key=lambda x: x[1], reverse=True)
    
    def get_recommendation(self, service_type: str, criteria: str = 'satisfaction') -> Optional[str]:
        """Get single best agent recommendation"""
        available_agents = list(self.agent_features.keys())
        if not available_agents:
            return None
        
        rankings = self.rank_agents(available_agents, service_type, criteria)
        return rankings[0][0] if rankings else None
    
    def get_matching_stats(self):
        """Get service matching statistics"""
        return {
            'agents_tracked': len(self.agent_features),
            'service_records': len(self.service_history),
            'models_trained': len(self.models),
            'is_trained': self.is_trained
        }

# Global matcher instance
service_matcher = ServiceMatcher()