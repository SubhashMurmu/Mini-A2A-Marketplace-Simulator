from communication.message_schema import ServiceRequest, ServiceResponse
from ledger.mock_ledger import MockLedger
import random
import time

class AgentBase:
    def __init__(self, name, services, ledger: MockLedger):
        self.name = name
        self.services = services  # {service_name: base_price}
        self.ledger = ledger
        self.balance = 100
        self.service_history = []
        self.success_rate = 0.95
        self.response_time = random.uniform(1, 3)  # seconds
        self.load = 0  # current workload
        self.reputation = 5.0  # out of 5
        
    def list_services(self):
        """Return available services with current pricing"""
        return {
            service: {
                'price': price,
                'success_rate': self.success_rate,
                'response_time': self.response_time,
                'reputation': self.reputation
            }
            for service, price in self.services.items()
        }
    
    def get_dynamic_price(self, service_type, base_demand=1.0):
        """Calculate dynamic pricing based on load and demand"""
        base_price = self.services.get(service_type, 0)
        load_multiplier = 1 + (self.load * 0.1)  # 10% increase per load unit
        demand_multiplier = base_demand
        return int(base_price * load_multiplier * demand_multiplier)
    
    def handle_request(self, request: ServiceRequest):
        """Process incoming service request"""
        if request.service_type not in self.services:
            return ServiceResponse(
                success=False,
                message="Service not offered",
                cost=0,
                execution_time=0
            )
        
        # Calculate actual price
        actual_price = self.get_dynamic_price(request.service_type)
        
        # Simulate negotiation acceptance (could be enhanced with RL)
        if request.offered_price >= actual_price * 0.8:  # Accept if >= 80% of asking price
            # Process payment
            if self.ledger.transfer(request.sender, self.name, request.offered_price):
                # Simulate service execution
                execution_time = random.uniform(1, 5)
                time.sleep(0.1)  # Simulate processing
                
                # Update history
                self.service_history.append({
                    'service': request.service_type,
                    'price': request.offered_price,
                    'client': request.sender,
                    'timestamp': time.time()
                })
                
                self.load = max(0, self.load - 1)  # Reduce load after completion
                
                return ServiceResponse(
                    success=True,
                    message=f"{self.name} completed {request.service_type} for {request.sender}",
                    cost=request.offered_price,
                    execution_time=execution_time
                )
            else:
                return ServiceResponse(
                    success=False,
                    message="Payment failed - insufficient funds",
                    cost=0,
                    execution_time=0
                )
        else:
            return ServiceResponse(
                success=False,
                message=f"Price too low. Minimum: {actual_price}",
                cost=actual_price,
                execution_time=0
            )
    
    def update_reputation(self, rating):
        """Update agent reputation based on client feedback"""
        self.reputation = (self.reputation * 0.9) + (rating * 0.1)
        self.reputation = max(1.0, min(5.0, self.reputation))