from agents.agent_base import AgentBase
from ledger.mock_ledger import ledger_instance

# Language Services Specialist
agent_b = AgentBase(
    name="Translator_B", 
    services={
        "translate_text": 4,
        "summarize_text": 6,
        "analyze_sentiment": 5
    }, 
    ledger=ledger_instance
)

# Enhance with specialization
agent_b.success_rate = 0.95
agent_b.response_time = 2.0
agent_b.reputation = 4.6