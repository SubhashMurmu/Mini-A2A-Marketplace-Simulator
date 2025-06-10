from agents.agent_base import AgentBase
from ledger.mock_ledger import ledger_instance

# Computation Services Specialist
agent_c = AgentBase(
    name="Computer_C", 
    services={
        "run_analysis": 8,
        "generate_report": 10,
        "optimize_model": 15
    }, 
    ledger=ledger_instance
)

# Enhance with specialization
agent_c.success_rate = 0.92
agent_c.response_time = 3.5
agent_c.reputation = 4.4