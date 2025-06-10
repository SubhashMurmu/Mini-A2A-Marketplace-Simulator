from typing import Dict, List, Optional
import time
import json

class Transaction:
    def __init__(self, sender: str, receiver: str, amount: int, service: str = None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.service = service
        self.timestamp = time.time()
        self.tx_id = f"tx_{int(self.timestamp)}_{hash(f'{sender}{receiver}{amount}') % 10000}"

class MockLedger:
    def __init__(self):
        self.accounts = {}
        self.transaction_history = []
        self.locked_funds = {}  # For escrow-like functionality
        
    def create_account(self, agent_name: str, initial_balance: int = 100):
        """Create a new account with initial balance"""
        self.accounts[agent_name] = initial_balance
        
    def get_balance(self, agent_name: str) -> int:
        """Get account balance"""
        return self.accounts.get(agent_name, 0)
    
    def transfer(self, sender: str, receiver: str, amount: int, service: str = None) -> bool:
        """Transfer tokens between accounts"""
        if self.accounts.get(sender, 0) >= amount:
            self.accounts[sender] -= amount
            self.accounts[receiver] = self.accounts.get(receiver, 0) + amount
            
            # Record transaction
            tx = Transaction(sender, receiver, amount, service)
            self.transaction_history.append(tx)
            
            return True
        return False
    
    def lock_funds(self, agent_name: str, amount: int, purpose: str) -> str:
        """Lock funds for escrow (e.g., during negotiation)"""
        if self.accounts.get(agent_name, 0) >= amount:
            self.accounts[agent_name] -= amount
            lock_id = f"lock_{int(time.time())}_{hash(purpose) % 10000}"
            self.locked_funds[lock_id] = {
                'agent': agent_name,
                'amount': amount,
                'purpose': purpose,
                'timestamp': time.time()
            }
            return lock_id
        return None
    
    def release_funds(self, lock_id: str, to_agent: str) -> bool:
        """Release locked funds to specified agent"""
        if lock_id in self.locked_funds:
            locked = self.locked_funds.pop(lock_id)
            self.accounts[to_agent] = self.accounts.get(to_agent, 0) + locked['amount']
            return True
        return False
    
    def return_locked_funds(self, lock_id: str) -> bool:
        """Return locked funds to original owner"""
        if lock_id in self.locked_funds:
            locked = self.locked_funds.pop(lock_id)
            self.accounts[locked['agent']] += locked['amount']
            return True
        return False
    
    def get_transaction_history(self, agent_name: str = None) -> List[Transaction]:
        """Get transaction history for an agent or all transactions"""
        if agent_name:
            return [tx for tx in self.transaction_history 
                   if tx.sender == agent_name or tx.receiver == agent_name]
        return self.transaction_history
    
    def get_ledger_stats(self):
        """Get ledger statistics"""
        total_supply = sum(self.accounts.values()) + sum(
            lock['amount'] for lock in self.locked_funds.values()
        )
        return {
            'total_accounts': len(self.accounts),
            'total_supply': total_supply,
            'total_transactions': len(self.transaction_history),
            'locked_funds': len(self.locked_funds)
        }

# Global ledger instance
ledger_instance = MockLedger()

# Initialize default accounts
ledger_instance.create_account("DataProcessor_A", 100)
ledger_instance.create_account("Translator_B", 100)
ledger_instance.create_account("Computer_C", 100)
ledger_instance.create_account("Client_X", 200)  # Test client