import streamlit as st
import time
import random
import sys
import os
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.agent_a import agent_a
from agents.agent_b import agent_b
from agents.agent_c import agent_c
from ai.rl_negotiation import global_negotiator
from ai.bandit_selection import service_bandit, contextual_bandit
from communication.message_schema import ServiceRequest
from communication.p2p_discovery import p2p_network
from ledger.mock_ledger import ledger_instance
import numpy as np

# Page configuration
st.set_page_config(
    page_title="A2A Interaction Simulator", 
    page_icon="🔄", 
    layout="centered"
)

# Initialize agents
agents = {
    "DataProcessor_A": agent_a,
    "Translator_B": agent_b,
    "Computer_C": agent_c
}

# Register agents in P2P network
for name, agent in agents.items():
    p2p_network.register(name, agent.list_services())

st.title("🔄 A2A Economy Interaction Simulator")
st.markdown("### Simulate autonomous agent interactions with AI-powered negotiation")

# Simulation Mode Selection
st.sidebar.header("🎮 Simulation Controls")
simulation_mode = st.sidebar.selectbox(
    "Simulation Mode",
    ["Manual Request", "Auto Simulation", "Batch Processing"]
)

if simulation_mode == "Manual Request":
    st.subheader("🎯 Manual Service Request")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sender = st.selectbox("🤖 Requester Agent", options=list(agents.keys()))
        
    with col2:
        # Get available receivers (excluding sender)
        available_receivers = [name for name in agents.keys() if name != sender]
        receiver = st.selectbox("🎯 Provider Agent", options=available_receivers)
    
    # Get services from selected receiver
    if receiver:
        receiver_agent = agents[receiver]
        available_services = list(receiver_agent.services.keys())
        
        col1, col2 = st.columns(2)
        
        with col1:
            service_type = st.selectbox("🔧 Service Type", options=available_services)
            
        with col2:
            base_price = receiver_agent.services.get(service_type, 10)
            offered_price = st.number_input(
                "💰 Offered Price", 
                min_value=1, 
                max_value=base_price * 2,
                value=base_price,
                step=1
            )
    
    # Advanced Options
    with st.expander("⚙️ Advanced Options"):
        use_negotiation = st.checkbox("🤝 Enable AI Negotiation", value=True)
        use_bandit = st.checkbox("🎰 Use Bandit Selection", value=True)
        urgency = st.slider("⏰ Urgency Level", 0.0, 1.0, 0.5, 0.1)
    
    # Submit Request
    if st.button("📤 Submit Request", type="primary"):
        with st.spinner("🔄 Processing request..."):
            # Create service request
            request = ServiceRequest(
                sender=sender,
                receiver=receiver,
                service_type=service_type,
                offered_price=offered_price
            )
            
            st.markdown("## 📋 Processing Steps")
            
            # Step 1: Service Discovery
            st.write("**1. 🔍 Service Discovery**")
            providers = p2p_network.discover(service_type)
            st.success(f"Found {len(providers)} providers for '{service_type}'")
            
            # Initialize context (used for both bandit and reward recording)
            context = contextual_bandit.get_context(
                service_type, urgency, offered_price, 
                time.time() % 24 / 24  # time of day
            )
            
            # Step 2: Agent Selection (if bandit enabled)
            if use_bandit and len(providers) > 1:
                st.write("**2. 🎰 Bandit Agent Selection**")
                
                selected_agent = contextual_bandit.select_agent(context)
                st.info(f"Bandit selected: {selected_agent}")
                
                if selected_agent != receiver:
                    st.warning(f"Redirecting from {receiver} to {selected_agent}")
                    receiver = selected_agent
                    receiver_agent = agents[receiver]
                    request.receiver = receiver
            
            # Step 3: Negotiation Phase
            if use_negotiation:
                st.write("**3. 🤝 AI Negotiation Phase**")
                
                market_price = receiver_agent.services[service_type]
                agent_reputation = receiver_agent.reputation
                
                negotiation_result, final_price = global_negotiator.negotiate(
                    service_type, offered_price, market_price, agent_reputation
                )
                
                st.write(f"Negotiation outcome: **{negotiation_result}** at {final_price} tokens")
                
                if negotiation_result == "accept":
                    request.offered_price = final_price
                else:
                    st.error("Negotiation failed - no agreement reached")
                    st.stop()
            
            # Step 4: Service Execution
            st.write("**4. ⚙️ Service Execution**")
            response = receiver_agent.handle_request(request)
            
            if response.success:
                st.success(f"✅ Service completed! {response.message}")
                st.write(f"Cost: {response.cost} tokens")
                st.write(f"Execution time: {response.execution_time:.1f} seconds")
                
                # Record reward for bandit
                satisfaction = random.uniform(0.7, 1.0)  # Simulated satisfaction
                contextual_bandit.update_weights(
                    receiver, context, satisfaction
                )
                service_bandit.update_reward(receiver, satisfaction)
                
                # Record reward for negotiator
                reward = global_negotiator.calculate_reward(
                    response.cost, market_price, True
                )
                global_negotiator.update_q_value(
                    global_negotiator.get_state(
                        service_type, response.cost, market_price, agent_reputation
                    ),
                    "accept",
                    reward
                )
            else:
                st.error(f"❌ Service failed: {response.message}")
                
                # Record negative reward for bandit
                contextual_bandit.update_weights(
                    receiver, context, -0.5
                )
                service_bandit.update_reward(receiver, -0.5)

elif simulation_mode == "Auto Simulation":
    st.subheader("🤖 Autonomous Simulation")
    
    num_rounds = st.slider("Number of Rounds", 1, 100, 10)
    speed = st.slider("Simulation Speed", 0.1, 2.0, 1.0, 0.1)
    
    if st.button("▶️ Start Simulation"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        results = []
        
        for i in range(num_rounds):
            progress_bar.progress((i + 1) / num_rounds)
            status_text.text(f"Round {i + 1}/{num_rounds} - Running...")
            
            # Randomly select sender and service
            sender = random.choice(list(agents.keys()))
            receiver_options = [name for name in agents.keys() if name != sender]
            receiver = random.choice(receiver_options)
            receiver_agent = agents[receiver]
            
            service_type = random.choice(list(receiver_agent.services.keys()))
            base_price = receiver_agent.services[service_type]
            offered_price = random.randint(
                int(base_price * 0.5), 
                int(base_price * 1.5)
            )
            
            # Create request
            request = ServiceRequest(
                sender=sender,
                receiver=receiver,
                service_type=service_type,
                offered_price=offered_price
            )
            
            # Initialize context
            context = contextual_bandit.get_context(
                service_type, random.random(), offered_price, 
                time.time() % 24 / 24
            )
            
            # Use contextual bandit for selection
            selected_agent = contextual_bandit.select_agent(context)
            
            if selected_agent != receiver:
                receiver = selected_agent
                receiver_agent = agents[receiver]
                request.receiver = receiver
            
            # Negotiation
            market_price = receiver_agent.services[service_type]
            agent_reputation = receiver_agent.reputation
            negotiation_result, final_price = global_negotiator.negotiate(
                service_type, offered_price, market_price, agent_reputation
            )
            
            if negotiation_result == "accept":
                request.offered_price = final_price
                response = receiver_agent.handle_request(request)
                
                if response.success:
                    # Record successful transaction
                    satisfaction = random.uniform(0.7, 1.0)
                    contextual_bandit.update_weights(
                        receiver, context, satisfaction
                    )
                    service_bandit.update_reward(receiver, satisfaction)
                    
                    reward = global_negotiator.calculate_reward(
                        response.cost, market_price, True
                    )
                    global_negotiator.update_q_value(
                        global_negotiator.get_state(
                            service_type, response.cost, market_price, agent_reputation
                        ),
                        "accept",
                        reward
                    )
                    
                    results.append({
                        "Round": i + 1,
                        "Sender": sender,
                        "Receiver": receiver,
                        "Service": service_type,
                        "Price": response.cost,
                        "Status": "Success",
                        "Time": f"{response.execution_time:.1f}s"
                    })
                else:
                    # Record failed transaction
                    contextual_bandit.update_weights(
                        receiver, context, -0.5
                    )
                    service_bandit.update_reward(receiver, -0.5)
                    
                    results.append({
                        "Round": i + 1,
                        "Sender": sender,
                        "Receiver": receiver,
                        "Service": service_type,
                        "Price": final_price,
                        "Status": "Failed",
                        "Time": "N/A"
                    })
            else:
                results.append({
                    "Round": i + 1,
                    "Sender": sender,
                    "Receiver": receiver,
                    "Service": service_type,
                    "Price": "N/A",
                    "Status": "Rejected",
                    "Time": "N/A"
                })
            
            time.sleep(1.0 / speed)  # Control simulation speed
        
        status_text.text("✅ Simulation complete!")
        st.dataframe(pd.DataFrame(results))

elif simulation_mode == "Batch Processing":
    st.subheader("📦 Batch Processing")
    
    st.warning("Batch processing mode is not yet implemented in this demo.")
    st.info("In a full implementation, this would allow you to:")
    st.write("- Upload a CSV of tasks to process")
    st.write("- Define multi-step workflows")
    st.write("- Monitor progress of batch jobs")
    st.write("- Download results and transaction logs")

# Display system stats
st.sidebar.markdown("---")
st.sidebar.subheader("System Stats")

# Bandit stats
bandit_stats = service_bandit.get_stats()
st.sidebar.write("**Bandit Selections**")
for agent, stats in bandit_stats.items():
    st.sidebar.write(f"{agent}: {stats['selections']}")

# Negotiator stats
negotiator_stats = global_negotiator.get_strategy_stats()
st.sidebar.write("**Negotiation Actions**")
if "action_preferences" in negotiator_stats:
    for action, count in negotiator_stats["action_preferences"].items():
        st.sidebar.write(f"{action}: {count}")

# Ledger stats
ledger_stats = ledger_instance.get_ledger_stats()
st.sidebar.write(f"**Total Transactions:** {ledger_stats['total_transactions']}")