import json
import os
from datetime import datetime

class Account:
    def __init__(self, account_number, pin, balance=0.0):
        self.account_number = account_number
        self.pin = pin
        self.balance = balance
        self.transaction_history = []

class ATM:
    def __init__(self, data_file="accounts.json"):
        self.data_file = data_file
        self.accounts = {}
        self.current_account = None
        self.load_accounts()
    
    def load_accounts(self):
        """Load accounts from JSON file or create sample data if file doesn't exist"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as file:
                    data = json.load(file)
                    for acc_data in data.values():
                        account = Account(
                            acc_data['account_number'],
                            acc_data['pin'],
                            acc_data['balance']
                        )
                        account.transaction_history = acc_data.get('transaction_history', [])
                        self.accounts[account.account_number] = account
                print("Accounts loaded successfully!")
            except Exception as e:
                print(f"Error loading accounts: {e}. Creating new accounts file.")
                self.create_sample_accounts()
        else:
            print("No accounts file found. Creating sample accounts...")
            self.create_sample_accounts()
    
    def create_sample_accounts(self):
        """Create sample accounts for testing"""
        sample_accounts = [
            Account("1234567890", "1234", 1000.00),
            Account("0987654321", "5678", 500.00),
            Account("5555555555", "0000", 2500.00),
            Account("63799912940", "2003", 3400.00)

        ]
        
        for account in sample_accounts:
            self.accounts[account.account_number] = account
        
        self.save_accounts()
        print("Sample accounts created successfully!")
    
    def save_accounts(self):
        """Save all accounts to JSON file"""
        try:
            data = {}
            for account_number, account in self.accounts.items():
                data[account_number] = {
                    'account_number': account.account_number,
                    'pin': account.pin,
                    'balance': account.balance,
                    'transaction_history': account.transaction_history
                }
            
            with open(self.data_file, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"Error saving accounts: {e}")
    
    def add_transaction(self, account, transaction_type, amount, target_account=None):
        """Add a transaction to account history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transaction = {
            'type': transaction_type,
            'amount': amount,
            'timestamp': timestamp
        }
        
        if target_account:
            transaction['target_account'] = target_account
        
        account.transaction_history.append(transaction)
        # Keep only last 20 transactions to prevent file from growing too large
        if len(account.transaction_history) > 20:
            account.transaction_history = account.transaction_history[-20:]
    
    def login(self):
        """User login with account number and PIN"""
        print("\n=== ATM Login ===")
        account_number = input("Enter account number: ").strip()
        pin = input("Enter PIN: ").strip()
        
        if account_number in self.accounts:
            account = self.accounts[account_number]
            if account.pin == pin:
                self.current_account = account
                print(f"Login successful! Welcome, account {account_number}")
                self.add_transaction(account, "LOGIN", 0)
                return True
            else:
                print("Invalid PIN!")
        else:
            print("Account not found!")
        
        return False
    
    def logout(self):
        """Logout current user"""
        if self.current_account:
            self.add_transaction(self.current_account, "LOGOUT", 0)
            print(f"Goodbye! Account {self.current_account.account_number} logged out.")
            self.current_account = None
    
    def check_balance(self):
        """Check current account balance"""
        if not self.current_account:
            print("Please login first!")
            return
        
        print(f"\nCurrent balance: ${self.current_account.balance:.2f}")
        self.add_transaction(self.current_account, "BALANCE_CHECK", 0)
    
    def withdraw(self):
        """Withdraw money from account"""
        if not self.current_account:
            print("Please login first!")
            return
        
        print("\n=== Withdraw Money ===")
        try:
            amount = float(input("Enter amount to withdraw: $"))
            
            if amount <= 0:
                print("Amount must be positive!")
                return
            
            if amount > self.current_account.balance:
                print("Insufficient funds!")
                return
            
            self.current_account.balance -= amount
            self.add_transaction(self.current_account, "WITHDRAWAL", amount)
            self.save_accounts()
            
            print(f"Successfully withdrew ${amount:.2f}")
            print(f"New balance: ${self.current_account.balance:.2f}")
            
        except ValueError:
            print("Invalid amount! Please enter a valid number.")
        except Exception as e:
            print(f"Error during withdrawal: {e}")
    
    def deposit(self):
        """Deposit money to account"""
        if not self.current_account:
            print("Please login first!")
            return
        
        print("\n=== Deposit Money ===")
        try:
            amount = float(input("Enter amount to deposit: $"))
            
            if amount <= 0:
                print("Amount must be positive!")
                return
            
            self.current_account.balance += amount
            self.add_transaction(self.current_account, "DEPOSIT", amount)
            self.save_accounts()
            
            print(f"Successfully deposited ${amount:.2f}")
            print(f"New balance: ${self.current_account.balance:.2f}")
            
        except ValueError:
            print("Invalid amount! Please enter a valid number.")
        except Exception as e:
            print(f"Error during deposit: {e}")
    
    def transfer(self):
        """Transfer money to another account"""
        if not self.current_account:
            print("Please login first!")
            return
        
        print("\n=== Transfer Money ===")
        try:
            target_account_number = input("Enter target account number: ").strip()
            amount = float(input("Enter amount to transfer: $"))
            
            if amount <= 0:
                print("Amount must be positive!")
                return
            
            if amount > self.current_account.balance:
                print("Insufficient funds!")
                return
            
            if target_account_number not in self.accounts:
                print("Target account not found!")
                return
            
            if target_account_number == self.current_account.account_number:
                print("Cannot transfer to your own account!")
                return
            
            # Perform transfer
            target_account = self.accounts[target_account_number]
            self.current_account.balance -= amount
            target_account.balance += amount
            
            # Add transactions to both accounts
            self.add_transaction(self.current_account, "TRANSFER_OUT", amount, target_account_number)
            self.add_transaction(target_account, "TRANSFER_IN", amount, self.current_account.account_number)
            
            self.save_accounts()
            
            print(f"Successfully transferred ${amount:.2f} to account {target_account_number}")
            print(f"New balance: ${self.current_account.balance:.2f}")
            
        except ValueError:
            print("Invalid amount! Please enter a valid number.")
        except Exception as e:
            print(f"Error during transfer: {e}")
    
    def show_transactions(self):
        """Show last 5 transactions"""
        if not self.current_account:
            print("Please login first!")
            return
        
        transactions = self.current_account.transaction_history
        print("\n=== Last 5 Transactions ===")
        
        if not transactions:
            print("No transactions found.")
            return
        
        # Show last 5 transactions (most recent first)
        recent_transactions = transactions[-5:][::-1]  # Get last 5 and reverse for recent first
        
        for i, transaction in enumerate(recent_transactions, 1):
            print(f"{i}. {transaction['timestamp']} - {transaction['type']}: ${transaction['amount']:.2f}")
            if 'target_account' in transaction:
                print(f"   Target: {transaction['target_account']}")
    
    def show_menu(self):
        """Display main menu"""
        while True:
            print("\n" + "="*40)
            print("          ATM SIMULATION")
            print("="*40)
            
            if self.current_account:
                print(f"Logged in as: {self.current_account.account_number}")
                print(f"Balance: ${self.current_account.balance:.2f}")
                print("\n1. Check Balance")
                print("2. Withdraw Money")
                print("3. Deposit Money")
                print("4. Transfer Money")
                print("5. Show Last 5 Transactions")
                print("6. Logout")
                print("7. Exit")
            else:
                print("1. Login")
                print("2. Exit")
            
            choice = input("\nEnter your choice: ").strip()
            
            if self.current_account:
                # User is logged in
                if choice == '1':
                    self.check_balance()
                elif choice == '2':
                    self.withdraw()
                elif choice == '3':
                    self.deposit()
                elif choice == '4':
                    self.transfer()
                elif choice == '5':
                    self.show_transactions()
                elif choice == '6':
                    self.logout()
                elif choice == '7':
                    if self.current_account:
                        self.logout()
                    print("Thank you for using our ATM. Goodbye!")
                    break
                else:
                    print("Invalid choice! Please try again.")
            else:
                # User is not logged in
                if choice == '1':
                    if self.login():
                        continue
                elif choice == '2':
                    print("Thank you for using our ATM. Goodbye!")
                    break
                else:
                    print("Invalid choice! Please try again.")

def main():
    """Main function to run the ATM simulation"""
    print("Initializing ATM System...")
    atm = ATM()
    
    try:
        atm.show_menu()
    except KeyboardInterrupt:
        print("\n\nATM session interrupted. Goodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()