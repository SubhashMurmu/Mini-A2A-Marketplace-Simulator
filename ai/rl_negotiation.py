import numpy as np
import random
from typing import Dict, Tuple, Optional

class RLNegotiator:
    def __init__(self, learning_rate=0.1, discount_factor=0.9, epsilon=0.1):
        self.q_table = {}  # {state: {action: q_value}}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon  # exploration rate
        self.actions = ["accept", "reject", "counter_low", "counter_high"]
        self.negotiation_history = []
        
    def get_state(self, service_type: str, offered_price: int, market_price: int, 
                  agent_reputation: float, urgency: float = 0.5) -> str:
        """Convert negotiation context to state string"""
        price_ratio = offered_price / max(market_price, 1)
        price_category = "low" if price_ratio < 0.8 else "fair" if price_ratio < 1.2 else "high"
        reputation_category = "low" if agent_reputation < 3.0 else "medium" if agent_reputation < 4.5 else "high"
        urgency_category = "low" if urgency < 0.3 else "medium" if urgency < 0.7 else "high"
        
        return f"{service_type}_{price_category}_{reputation_category}_{urgency_category}"
    
    def get_action(self, state: str, explore: bool = True) -> str:
        """Get action based on current state using epsilon-greedy policy"""
        if state not in self.q_table:
            self.q_table[state] = {action: 0.0 for action in self.actions}
        
        if explore and random.random() < self.epsilon:
            return random.choice(self.actions)
        
        # Choose action with highest Q-value
        return max(self.q_table[state], key=self.q_table[state].get)
    
    def update_q_value(self, state: str, action: str, reward: float, next_state: str = None):
        """Update Q-value using Q-learning algorithm"""
        if state not in self.q_table:
            self.q_table[state] = {action: 0.0 for action in self.actions}
        
        if next_state and next_state not in self.q_table:
            self.q_table[next_state] = {action: 0.0 for action in self.actions}
        
        # Q-learning update
        current_q = self.q_table[state][action]
        max_next_q = max(self.q_table[next_state].values()) if next_state else 0
        
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state][action] = new_q
    
    def negotiate(self, service_type: str, initial_offer: int, market_price: int,
                  agent_reputation: float, max_rounds: int = 3) -> Tuple[str, int]:
        """Conduct a negotiation session"""
        current_offer = initial_offer
        for round_num in range(max_rounds):
            state = self.get_state(service_type, current_offer, market_price, 
                                 agent_reputation, urgency=round_num/max_rounds)
            
            action = self.get_action(state)
            
            if action == "accept":
                reward = self.calculate_reward(current_offer, market_price, True)
                self.update_q_value(state, action, reward)
                return "accept", current_offer
            
            elif action == "reject":
                reward = self.calculate_reward(current_offer, market_price, False)
                self.update_q_value(state, action, reward)
                return "reject", 0
            
            elif action == "counter_low":
                current_offer = max(1, int(current_offer * 0.8))
                reward = -0.1  # Small penalty for prolonging negotiation
                self.update_q_value(state, action, reward)
                
            elif action == "counter_high":
                current_offer = int(current_offer * 1.2)
                reward = -0.1
                self.update_q_value(state, action, reward)
        
        # If max rounds reached, accept current offer
        final_state = self.get_state(service_type, current_offer, market_price, 
                                   agent_reputation, urgency=1.0)
        reward = self.calculate_reward(current_offer, market_price, True)
        self.update_q_value(final_state, "accept", reward)
        
        return "accept", current_offer
    
    def calculate_reward(self, final_price: int, market_price: int, deal_made: bool) -> float:
        """Calculate reward for negotiation outcome"""
        if not deal_made:
            return -1.0  # Penalty for failed negotiation
        
        # Reward based on how good the deal is compared to market price
        price_ratio = final_price / market_price
        if price_ratio > 1.2:
            return 1.0  # Great deal
        elif price_ratio > 1.0:
            return 0.5  # Good deal
        elif price_ratio > 0.8:
            return 0.0  # Fair deal
        else:
            return -0.5  # Poor deal
    
    def get_strategy_stats(self):
        """Get statistics about learned strategies"""
        if not self.q_table:
            return {"message": "No learning data available"}
        
        action_preferences = {action: 0 for action in self.actions}
        for state_actions in self.q_table.values():
            best_action = max(state_actions, key=state_actions.get)
            action_preferences[best_action] += 1
        
        return {
            "states_learned": len(self.q_table),
            "action_preferences": action_preferences,
            "exploration_rate": self.epsilon
        }

# Global negotiator instance
global_negotiator = RLNegotiator()