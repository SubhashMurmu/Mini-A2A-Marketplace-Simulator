from dataclasses import dataclass
from typing import Optional
import time

@dataclass
class ServiceRequest:
    sender: str
    receiver: str
    service_type: str
    offered_price: int
    deadline: Optional[float] = None
    requirements: Optional[dict] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class ServiceResponse:
    success: bool
    message: str
    cost: int
    execution_time: float
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class NegotiationOffer:
    sender: str
    receiver: str
    service_type: str
    proposed_price: int
    counter_offer: bool = False
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()