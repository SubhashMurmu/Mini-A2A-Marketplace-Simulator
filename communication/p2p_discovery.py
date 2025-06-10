from typing import Dict, List, Optional
import random

class P2PNetwork:
    def __init__(self):
        self.registry = {}  # {agent_name: {services, metadata}}
        self.network_graph = {}  # Simple peer connections
        
    def register(self, agent_name: str, services: dict, metadata: dict = None):
        """Register an agent with its services"""
        self.registry[agent_name] = {
            'services': services,
            'metadata': metadata or {},
            'online': True,
            'last_seen': None
        }
        
    def discover(self, service_type: str) -> List[dict]:
        """Find all agents offering a specific service"""
        providers = []
        for agent_name, info in self.registry.items():
            if info['online'] and service_type in info['services']:
                providers.append({
                    'agent': agent_name,
                    'price': info['services'][service_type]['price'],
                    'reputation': info['services'][service_type].get('reputation', 3.0),
                    'success_rate': info['services'][service_type].get('success_rate', 0.9),
                    'response_time': info['services'][service_type].get('response_time', 2.0)
                })
        return sorted(providers, key=lambda x: x['reputation'], reverse=True)
    
    def find_best_provider(self, service_type: str, criteria: str = 'reputation') -> Optional[str]:
        """Find the best provider based on specified criteria"""
        providers = self.discover(service_type)
        if not providers:
            return None
            
        if criteria == 'reputation':
            return max(providers, key=lambda x: x['reputation'])['agent']
        elif criteria == 'price':
            return min(providers, key=lambda x: x['price'])['agent']
        elif criteria == 'speed':
            return min(providers, key=lambda x: x['response_time'])['agent']
        else:
            return random.choice(providers)['agent']
    
    def get_network_stats(self):
        """Get network statistics"""
        total_agents = len(self.registry)
        online_agents = sum(1 for info in self.registry.values() if info['online'])
        all_services = set()
        for info in self.registry.values():
            all_services.update(info['services'].keys())
            
        return {
            'total_agents': total_agents,
            'online_agents': online_agents,
            'unique_services': len(all_services),
            'services': list(all_services)
        }

# Global network instance
p2p_network = P2PNetwork()