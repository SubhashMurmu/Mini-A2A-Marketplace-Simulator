import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.agent_a import agent_a
from agents.agent_b import agent_b
from agents.agent_c import agent_c
from ledger.mock_ledger import ledger_instance
from ai.bandit_selection import service_bandit
from ai.rl_negotiation import global_negotiator
from communication.p2p_discovery import p2p_network

# Page configuration
st.set_page_config(
    page_title="A2A Economy Dashboard", 
    page_icon="🤖", 
    layout="wide"
)

# Initialize agents in P2P network
agents = {
    "DataProcessor_A": agent_a,
    "Translator_B": agent_b,
    "Computer_C": agent_c
}

for name, agent in agents.items():
    p2p_network.register(name, agent.list_services(), {
        'reputation': agent.reputation,
        'response_time': agent.response_time
    })

# Dashboard Header
st.title("🤖 A2A Economy Dashboard")
st.markdown("### Real-time Agent-to-Agent Marketplace Analytics")

# Sidebar
st.sidebar.header("📊 Dashboard Controls")
view_mode = st.sidebar.selectbox(
    "Select View", 
    ["Overview", "Agent Details", "Market Analytics", "ML Performance", "Network Stats"]
)

# Main content based on view mode
if view_mode == "Overview":
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Active Agents", 
            len(agents),
            delta=None
        )
    
    with col2:
        total_transactions = len(ledger_instance.get_transaction_history())
        st.metric(
            "Total Transactions", 
            total_transactions,
            delta="+2" if total_transactions > 0 else None
        )
    
    with col3:
        network_stats = p2p_network.get_network_stats()
        st.metric(
            "Services Available", 
            network_stats['unique_services'],
            delta=None
        )
    
    with col4:
        total_volume = sum(
            tx.amount for tx in ledger_instance.get_transaction_history()
        )
        st.metric(
            "Transaction Volume", 
            f"{total_volume} tokens",
            delta=f"+{total_volume//10}" if total_volume > 0 else None
        )
    
    # Agent Balances
    st.subheader("💰 Agent Balances")
    balance_data = []
    for agent_name in agents.keys():
        balance = ledger_instance.get_balance(agent_name)
        balance_data.append({"Agent": agent_name, "Balance": balance})
    
    df_balances = pd.DataFrame(balance_data)
    fig_balance = px.bar(
        df_balances, 
        x="Agent", 
        y="Balance", 
        title="Current Token Balances",
        color="Balance",
        color_continuous_scale="viridis"
    )
    st.plotly_chart(fig_balance, use_container_width=True)
    
    # Service Offerings
    st.subheader("🔧 Available Services")
    service_data = []
    for agent_name, agent in agents.items():
        for service, details in agent.list_services().items():
            service_data.append({
                "Agent": agent_name,
                "Service": service,
                "Price": details['price'],
                "Success Rate": details['success_rate'],
                "Reputation": details['reputation']
            })
    
    df_services = pd.DataFrame(service_data)
    st.dataframe(df_services, use_container_width=True)

elif view_mode == "Agent Details":
    st.subheader("🤖 Agent Performance Details")
    
    selected_agent = st.selectbox("Select Agent", list(agents.keys()))
    agent = agents[selected_agent]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Agent Information**")
        st.write(f"Name: {agent.name}")
        st.write(f"Balance: {ledger_instance.get_balance(agent.name)} tokens")
        st.write(f"Success Rate: {agent.success_rate:.2%}")
        st.write(f"Reputation: {agent.reputation:.1f}/5.0")
        st.write(f"Response Time: {agent.response_time:.1f}s")
        st.write(f"Current Load: {agent.load}")
    
    with col2:
        st.write("**Services Offered**")
        services_df = pd.DataFrame([
            {"Service": service, "Base Price": price}
            for service, price in agent.services.items()
        ])
        st.dataframe(services_df)
    
    # Transaction History
    st.write("**Transaction History**")
    agent_transactions = ledger_instance.get_transaction_history(agent.name)
    if agent_transactions:
        tx_data = []
        for tx in agent_transactions[-10:]:  # Last 10 transactions
            tx_data.append({
                "Transaction ID": tx.tx_id,
                "Type": "Received" if tx.receiver == agent.name else "Sent",
                "Amount": tx.amount,
                "Other Party": tx.sender if tx.receiver == agent.name else tx.receiver,
                "Service": tx.service or "N/A",
                "Timestamp": datetime.fromtimestamp(tx.timestamp).strftime("%Y-%m-%d %H:%M:%S")
            })
        st.dataframe(pd.DataFrame(tx_data))
    else:
        st.info("No transaction history available")

elif view_mode == "Market Analytics":
    st.subheader("📈 Market Analytics")
    
    # Price Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Service Price Comparison**")
        all_services = set()
        for agent in agents.values():
            all_services.update(agent.services.keys())
        
        price_comparison = []
        for service in all_services:
            for agent_name, agent in agents.items():
                if service in agent.services:
                    price_comparison.append({
                        "Service": service,
                        "Agent": agent_name,
                        "Price": agent.services[service]
                    })
        
        if price_comparison:
            df_prices = pd.DataFrame(price_comparison)
            fig_prices = px.bar(
                df_prices, 
                x="Service", 
                y="Price", 
                color="Agent",
                title="Service Pricing by Agent",
                barmode="group"
            )
            st.plotly_chart(fig_prices, use_container_width=True)
    
    with col2:
        st.write("**Transaction Volume Over Time**")
        transactions = ledger_instance.get_transaction_history()
        if transactions:
            # Group transactions by hour
            tx_by_time = {}
            for tx in transactions:
                hour = datetime.fromtimestamp(tx.timestamp).strftime("%H:00")
                tx_by_time[hour] = tx_by_time.get(hour, 0) + tx.amount
            
            df_volume = pd.DataFrame([
                {"Time": time, "Volume": volume} 
                for time, volume in tx_by_time.items()
            ])
            
            fig_volume = px.line(
                df_volume, 
                x="Time", 
                y="Volume",
                title="Transaction Volume by Time"
            )
            st.plotly_chart(fig_volume, use_container_width=True)
        else:
            st.info("No transaction data available")

elif view_mode == "ML Performance":
    st.subheader("🧠 Machine Learning Performance")
    
    # Bandit Performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Multi-Armed Bandit Stats**")
        bandit_stats = service_bandit.get_stats()
        df_bandit = pd.DataFrame([
            {
                "Agent": agent,
                "Selections": stats["selections"],
                "Avg Reward": stats["avg_reward"],
                "Total Reward": stats["total_reward"]
            }
            for agent, stats in bandit_stats.items()
        ])
        st.dataframe(df_bandit)
        
        if not df_bandit.empty:
            fig_bandit = px.bar(
                df_bandit,
                x="Agent",
                y="Avg Reward",
                title="Average Reward by Agent"
            )
            st.plotly_chart(fig_bandit, use_container_width=True)
    
    with col2:
        st.write("**RL Negotiation Performance**")
        negotiation_stats = global_negotiator.get_strategy_stats()
        
        if "action_preferences" in negotiation_stats:
            df_actions = pd.DataFrame([
                {"Action": action, "Frequency": freq}
                for action, freq in negotiation_stats["action_preferences"].items()
            ])
            
            fig_actions = px.pie(
                df_actions,
                values="Frequency",
                names="Action",
                title="Negotiation Action Preferences"
            )
            st.plotly_chart(fig_actions, use_container_width=True)
        
        st.write(f"**States Learned:** {negotiation_stats.get('states_learned', 0)}")
        st.write(f"**Exploration Rate:** {negotiation_stats.get('exploration_rate', 0):.2%}")

elif view_mode == "Network Stats":
    st.subheader("🌐 Network Statistics")
    
    # Network Overview
    network_stats = p2p_network.get_network_stats()
    ledger_stats = ledger_instance.get_ledger_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**P2P Network**")
        st.write(f"Total Agents: {network_stats['total_agents']}")
        st.write(f"Online Agents: {network_stats['online_agents']}")
        st.write(f"Unique Services: {network_stats['unique_services']}")
    
    with col2:
        st.write("**Ledger Statistics**")
        st.write(f"Total Accounts: {ledger_stats['total_accounts']}")
        st.write(f"Total Supply: {ledger_stats['total_supply']} tokens")
        st.write(f"Total Transactions: {ledger_stats['total_transactions']}")
    
    with col3:
        st.write("**System Health**")
        st.write("🟢 All Systems Operational")
        st.write(f"📊 {len(agents)} Agents Active")
        st.write(f"💰 {ledger_stats['locked_funds']} Escrow Transactions")
    
    # Service Distribution
    st.write("**Service Distribution**")
    service_count = {}
    for agent in agents.values():
        for service in agent.services:
            service_count[service] = service_count.get(service, 0) + 1
    
    df_service_dist = pd.DataFrame([
        {"Service": service, "Providers": count}
        for service, count in service_count.items()
    ])
    
    fig_service_dist = px.bar(
        df_service_dist,
        x="Service",
        y="Providers",
        title="Number of Providers per Service"
    )
    st.plotly_chart(fig_service_dist, use_container_width=True)

# Real-time updates
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

# Footer
st.markdown("---")
st.markdown("🤖 A2A Marketplace Simulator - Built with Streamlit")