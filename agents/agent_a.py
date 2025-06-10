from agents.agent_base import AgentBase
from ledger.mock_ledger import ledger_instance

# Data Processing Specialist
agent_a = AgentBase(
    name="DataProcessor_A", 
    services={
        "clean_data": 5,
        "validate_data": 3,
        "transform_data": 7
    }, 
    ledger=ledger_instance
)

# Enhance with specialization
agent_a.success_rate = 0.98
agent_a.response_time = 1.5
agent_a.reputation = 4.8