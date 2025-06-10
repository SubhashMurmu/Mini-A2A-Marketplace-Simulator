import numpy as np
import random
from typing import List, Dict, Any
import time

class MultiArmedBandit:
    def __init__(self, agents: List[str], initial_confidence: float = 1.0):
        self.agents = agents
        self.rewards = {agent: [] for agent in agents}
        self.selection_count = {agent: 0 for agent in agents}
        self.cumulative_reward = {agent: 0.0 for agent in agents}
        self.confidence_interval = {agent: initial_confidence for agent in agents}
        self.total_selections = 0
        
    def select_epsilon_greedy(self, epsilon: float = 0.1) -> str:
        """Epsilon-greedy selection strategy"""
        if random.random() < epsilon or self.total_selections == 0:
            # Explore: random selection
            return random.choice(self.agents)
        else:
            # Exploit: choose agent with highest average reward
            avg_rewards = {
                agent: self.cumulative_reward[agent] / max(self.selection_count[agent], 1)
                for agent in self.agents
            }
            return max(avg_rewards, key=avg_rewards.get)
    
    def select_ucb1(self, c: float = 2.0) -> str:
        """Upper Confidence Bound selection strategy"""
        if self.total_selections == 0:
            return random.choice(self.agents)
        
        ucb_values = {}
        for agent in self.agents:
            if self.selection_count[agent] == 0:
                ucb_values[agent] = float('inf')  # Select unplayed agents first
            else:
                avg_reward = self.cumulative_reward[agent] / self.selection_count[agent]
                confidence = c * np.sqrt(np.log(self.total_selections) / self.selection_count[agent])
                ucb_values[agent] = avg_reward + confidence
        
        return max(ucb_values, key=ucb_values.get)
    
    def select_thompson_sampling(self) -> str:
        """Thompson Sampling selection strategy"""
        samples = {}
        for agent in self.agents:
            # Use Beta distribution for reward sampling
            successes = max(1, sum(1 for r in self.rewards[agent] if r > 0.5))
            failures = max(1, len(self.rewards[agent]) - successes + 1)
            samples[agent] = np.random.beta(successes, failures)
        
        return max(samples, key=samples.get)
    
    def update_reward(self, agent: str, reward: float):
        """Update reward for selected agent"""
        self.rewards[agent].append(reward)
        self.cumulative_reward[agent] += reward
        self.selection_count[agent] += 1
        self.total_selections += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bandit statistics"""
        stats = {}
        for agent in self.agents:
            count = self.selection_count[agent]
            if count > 0:
                avg_reward = self.cumulative_reward[agent] / count
                recent_rewards = self.rewards[agent][-10:]  # Last 10 rewards
                recent_avg = np.mean(recent_rewards) if recent_rewards else 0
            else:
                avg_reward = 0
                recent_avg = 0
            
            stats[agent] = {
                'selections': count,
                'avg_reward': round(avg_reward, 3),
                'recent_avg': round(recent_avg, 3),
                'total_reward': round(self.cumulative_reward[agent], 2)
            }
        
        return stats

class ContextualBandit:
    def __init__(self, agents: List[str], context_dimensions: int = 4):
        self.agents = agents
        self.context_dim = context_dimensions
        # Simple linear model: reward = context * weights
        self.weights = {agent: np.random.normal(0, 0.1, context_dimensions) 
                      for agent in agents}
        self.history = []
        
    def get_context(self, service_type: str, urgency: float, budget: int, 
                   time_of_day: float) -> np.ndarray:
        """Convert situational factors to context vector"""
        service_complexity = {
            'clean_data': 0.3, 'translate_text': 0.5, 'analyze_sentiment': 0.6,
            'run_analysis': 0.8, 'generate_report': 0.9, 'optimize_model': 1.0
        }.get(service_type, 0.5)
        
        return np.array([service_complexity, urgency, budget/100.0, time_of_day])
    
    def predict_reward(self, agent: str, context: np.ndarray) -> float:
        """Predict reward for agent given context"""
        return np.dot(self.weights[agent], context)
    
    def select_agent(self, context: np.ndarray, exploration: float = 0.1) -> str:
        """Select agent based on predicted rewards"""
        if random.random() < exploration:
            return random.choice(self.agents)
        
        predictions = {agent: self.predict_reward(agent, context) 
                      for agent in self.agents}
        return max(predictions, key=predictions.get)
    
    def update_weights(self, agent: str, context: np.ndarray, reward: float, 
                      learning_rate: float = 0.01):
        """Update agent weights based on observed reward"""
        predicted = self.predict_reward(agent, context)
        error = reward - predicted
        self.weights[agent] += learning_rate * error * context
        
        self.history.append({
            'agent': agent,
            'context': context.tolist(),
            'reward': reward,
            'error': error,
            'timestamp': time.time()
        })

# Global bandit instances
service_bandit = MultiArmedBandit(['DataProcessor_A', 'Translator_B', 'Computer_C'])
contextual_bandit = ContextualBandit(['DataProcessor_A', 'Translator_B', 'Computer_C'])