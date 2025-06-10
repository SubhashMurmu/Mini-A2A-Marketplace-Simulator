#!/usr/bin/env python3
"""
A2A Marketplace Simulator - Main Entry Point
This script provides the command-line interface for running simulations
of the agent-to-agent marketplace.
"""
import argparse
import time
import random
from typing import List, Dict, Any
from agents.agent_a import agent_a
from agents.agent_b import agent_b
from agents.agent_c import agent_c
from communication.p2p_discovery import p2p_network
from ledger.mock_ledger import ledger_instance
from ai.rl_negotiation import global_negotiator
from ai.bandit_selection import service_bandit, contextual_bandit
from communication.message_schema import ServiceRequest

def initialize_system():
    """Initialize all system components and register agents"""
    agents = {
        "DataProcessor_A": agent_a,
        "Translator_B": agent_b,
        "Computer_C": agent_c
    }
    
    # Register agents in P2P network
    for name, agent in agents.items():
        p2p_network.register(name, agent.list_services(), {
            'reputation': agent.reputation,
            'response_time': agent.response_time
        })
    
    return agents

def run_simulation(agents: Dict[str, Any], num_rounds: int = 10):
    """Run an automated simulation of the marketplace"""
    print(f"\n🚀 Starting simulation with {num_rounds} rounds...\n")
    
    results = []
    for i in range(num_rounds):
        # Randomly select sender and service
        sender = random.choice(list(agents.keys()))
        receiver_options = [name for name in agents.keys() if name != sender]
        receiver = random.choice(receiver_options)
        receiver_agent = agents[receiver]
        
        # Check if receiver has any services
        if not receiver_agent.services:
            print(f"  ⚠️ {receiver} has no services available")
            continue
            
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
        
        print(f"\n🔹 Round {i+1}: {sender} requesting {service_type} from {receiver}")
        
        # Find agents that can provide this service
        capable_agents = [name for name, agent in agents.items() 
                         if service_type in agent.services and name != sender]
        
        if not capable_agents:
            print(f"  ⚠️ No agents available to provide {service_type}")
            continue
        
        # Use contextual bandit for selection (only from capable agents)
        context = contextual_bandit.get_context(
            service_type, random.random(), offered_price, 
            time.time() % 24 / 24
        )
        
        # Make sure bandit selects from capable agents only
        if hasattr(contextual_bandit, 'select_from_agents'):
            selected_agent = contextual_bandit.select_from_agents(context, capable_agents)
        else:
            selected_agent = contextual_bandit.select_agent(context)
            # Verify the selected agent can provide the service
            if selected_agent not in capable_agents:
                selected_agent = random.choice(capable_agents)
        
        if selected_agent != receiver:
            print(f"  🔄 Bandit redirected to {selected_agent}")
            receiver = selected_agent
            receiver_agent = agents[receiver]
            request.receiver = receiver
        
        # Double-check that the final receiver can provide the service
        if service_type not in receiver_agent.services:
            print(f"  ❌ Error: {receiver} cannot provide {service_type}")
            continue
        
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
                print(f"  ✅ Success! Cost: {response.cost}, Time: {response.execution_time:.1f}s")
                
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
                    "round": i + 1,
                    "sender": sender,
                    "receiver": receiver,
                    "service": service_type,
                    "price": response.cost,
                    "status": "success",
                    "time": response.execution_time
                })
            else:
                print(f"  ❌ Failed: {response.message}")
                
                # Record failed transaction
                contextual_bandit.update_weights(
                    receiver, context, -0.5
                )
                service_bandit.update_reward(receiver, -0.5)
                
                results.append({
                    "round": i + 1,
                    "sender": sender,
                    "receiver": receiver,
                    "service": service_type,
                    "price": final_price,
                    "status": "failed",
                    "time": None
                })
        else:
            print(f"  ❌ Negotiation rejected")
            results.append({
                "round": i + 1,
                "sender": sender,
                "receiver": receiver,
                "service": service_type,
                "price": None,
                "status": "rejected",
                "time": None
            })
        
        time.sleep(0.5)  # Pause between rounds
    
    return results

def display_stats(agents: Dict[str, Any], results: List[Dict]):
    """Display simulation statistics"""
    print("\n📊 Simulation Results:")
    print(f"Total transactions: {len(results)}")
    
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"Successful transactions: {successful} ({successful/len(results)*100:.1f}%)" if results else "No transactions completed")
    
    if successful > 0:
        avg_price = sum(r['price'] for r in results if r['price']) / successful
        avg_time = sum(r['time'] for r in results if r['time']) / successful
        print(f"Average price: {avg_price:.1f} tokens")
        print(f"Average time: {avg_time:.1f}s")
    
    print("\n🤖 Agent Stats:")
    for name, agent in agents.items():
        print(f"{name}:")
        print(f"  Balance: {ledger_instance.get_balance(name)} tokens")
        print(f"  Reputation: {agent.reputation:.1f}/5.0")
        print(f"  Services completed: {len(agent.service_history)}")
    
    print("\n🎰 Bandit Stats:")
    bandit_stats = service_bandit.get_stats()
    for agent, stats in bandit_stats.items():
        print(f"{agent}:")
        print(f"  Selections: {stats['selections']}")
        print(f"  Avg Reward: {stats['avg_reward']:.2f}")
    
    print("\n🤝 Negotiator Stats:")
    negotiator_stats = global_negotiator.get_strategy_stats()
    print(f"States learned: {negotiator_stats.get('states_learned', 0)}")
    if "action_preferences" in negotiator_stats:
        print("Action preferences:")
        for action, count in negotiator_stats["action_preferences"].items():
            print(f"  {action}: {count}")

def main():
    """Main entry point for the A2A Marketplace Simulator"""
    parser = argparse.ArgumentParser(description='A2A Marketplace Simulator')
    parser.add_argument(
        '-r', '--rounds', 
        type=int, 
        default=10,
        help='Number of simulation rounds to run'
    )
    parser.add_argument(
        '--web', 
        action='store_true',
        help='Launch the web interface instead of CLI'
    )
    args = parser.parse_args()
    
    if args.web:
        print("Starting web interface...")
        print("Run: streamlit run ui/streamlit_ui.py")
        return
    
    print("🚀 Initializing A2A Marketplace Simulator...")
    agents = initialize_system()
    
    print("\n🤖 Registered Agents:")
    for name in agents.keys():
        print(f"- {name}")
    
    print("\n🔧 Available Services:")
    services = set()
    for agent in agents.values():
        services.update(agent.services.keys())
    for service in services:
        print(f"- {service}")
    
    results = run_simulation(agents, args.rounds)
    display_stats(agents, results)

if __name__ == "__main__":
    main()