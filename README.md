## A2A Marketplace Simulator Documentation

### Overview

The A2A (Agent-to-Agent) Marketplace Simulator is a comprehensive simulation environment for autonomous economic interactions between AI agents. It features service discovery, AI-powered negotiation, multi-armed bandit selection algorithms, and a token-based payment system.

---

### Key Features

* **Autonomous Agents**: Three specialized agents offering different services
* **AI Negotiation**: Reinforcement learning-based price negotiation
* **Intelligent Selection**: Contextual bandit algorithms for optimal agent selection
* **Token Economy**: Mock ledger system for tracking transactions
* **Web Interfaces**: Two Streamlit dashboards for visualization and interaction

---

### Project Structure

```
a2a_marketplace/
├── README.md
├── requirements.txt
├── main.py
├── agents/
│   ├── __init__.py
│   ├── agent_base.py
│   ├── agent_a.py
│   ├── agent_b.py
│   └── agent_c.py
├── communication/
│   ├── __init__.py
│   ├── message_schema.py
│   └── p2p_discovery.py
├── ledger/
│   ├── __init__.py
│   ├── mock_ledger.py
│   └── token_contract.sol
├── ai/
│   ├── __init__.py
│   ├── rl_negotiation.py
│   ├── bandit_selection.py
│   └── service_matcher.py
├── storage/
│   ├── __init__.py
│   └── storage_interface.py
├── blockchain/
│   ├── __init__.py
│   ├── token_contract.sol
│   └── voting_contract.sol
└── ui/
    ├── __init__.py
    ├── streamlit_ui.py
    └── interaction_ui.py
```

---

### Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

---

### Running the Simulator

#### Command Line Interface (CLI)

Run the main simulation:

```bash
python main.py
```

Options:

* `-r` or `--rounds`: Number of simulation rounds (default: 10)
* `--web`: Launch web interface (doesn't actually run it, just shows command)

Example:

```bash
python main.py -r 20
```

---

### Web Interfaces

#### 1. **Analytics Dashboard** (`streamlit_ui.py`)

Launch:

```bash
streamlit run ui/streamlit_ui.py
```

Features:

* Overview of key metrics
* Agent performance details
* Market analytics
* ML algorithm performance
* Network statistics

---

#### 2. **Interaction Simulator** (`interaction_ui.py`)

**To run the Interaction UI:**

```bash
streamlit run ui/interaction_ui.py
```

Features:

* Manually create and send service requests between agents
* Run automated simulations with customizable parameters
* Visualize negotiations, decisions, and transactions in real time
* Stub support for batch simulation input

---

### Agent Descriptions

**DataProcessor\_A**

* Services: Data cleaning, validation, transformation
* Success Rate: 98%
* Response Time: 1.5s
* Reputation: 4.8/5.0

**Translator\_B**

* Services: Text translation, summarization, sentiment analysis
* Success Rate: 95%
* Response Time: 2.0s
* Reputation: 4.6/5.0

**Computer\_C**

* Services: Analysis, report generation, model optimization
* Success Rate: 92%
* Response Time: 3.5s
* Reputation: 4.4/5.0

---

### Key Components

#### AI Components

**RLNegotiator** (`ai/rl_negotiation.py`)

* Q-learning based negotiation
* Learns optimal pricing over time
* Tracks negotiation history and success rates

**MultiArmedBandit / ContextualBandit** (`ai/bandit_selection.py`)

* Epsilon-greedy, UCB1, Thompson sampling
* ContextualBandit considers service type, urgency, budget, time of day
* Learns from outcomes to improve agent selection

#### Economic Components

**MockLedger** (`ledger/mock_ledger.py`)

* Token balances and escrow
* Logs transactions and service payments

**Token Contract** (`blockchain/token_contract.sol`)

* Solidity contract for payment and escrow handling

#### Communication Components

**P2PNetwork** (`communication/p2p_discovery.py`)

* Agent registration and service discovery
* Lookup and network tracking

**Message Schemas** (`communication/message_schema.py`)

* Dataclasses for requests, responses, offers

---

### Usage Examples

**Run CLI Simulation**:

```bash
python main.py -r 50
```

Sample Output:

```
🚀 Starting simulation with 50 rounds...

🔹 Round 1: Computer_C requesting translate_text from Translator_B
  ✅ Success! Cost: 4, Time: 2.3s

🔹 Round 2: DataProcessor_A requesting run_analysis from Computer_C
  🔄 Bandit redirected to Computer_C
  ✅ Success! Cost: 12, Time: 3.1s

🔹 Round 3: Translator_B requesting clean_data from DataProcessor_A
  ❌ Negotiation rejected

📊 Simulation Results:
Total transactions: 50
Successful transactions: 38 (76.0%)
Average price: 7.2 tokens
Average time: 2.4s
```

**Launch Interaction UI**:

```bash
streamlit run ui/interaction_ui.py
```

---

### Troubleshooting

**Missing Dependencies**

```bash
pip install -r requirements.txt
```

**Streamlit Issues**

* Use Python 3.7+
* Upgrade Streamlit if needed:

  ```bash
  pip install --upgrade streamlit
  ```

**Simulation Fails to Start**

* Check for syntax/import errors
* Verify all modules and files are intact

---

### Extending the System

**Add a New Agent**

1. Create a new file in `agents/`
2. Subclass `AgentBase`
3. Register in `main.py`

**Add a New Service**

1. Update an agent’s service dictionary
2. Set price, metadata, response behavior

**Modify AI Algorithms**

* Edit files in `ai/`
* Tune parameters or strategies
* Changes take effect in the next run

---

### License

This project is licensed under the MIT License. See the LICENSE file for more information.

