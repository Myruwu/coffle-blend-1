from flask import Flask, jsonify, request, render_template
import random
import hashlib

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('store_receive.html')
# Simulated conversion rates
conversion_rates = {
    'BTC': 1500000,  # 1 BTC = 1,500,000 PHP
    'XRP': 30,       # 1 XRP = 30 PHP
    'ETH': 100000,   # 1 ETH = 100,000 PHP
    'SOL': 150,      # 1 SOL = 150 PHP
    'DOGE': 0.3,     # 1 DOGE = 0.3 PHP
    'SHIB': 0.0001    # 1 SHIB = 0.0001 PHP
}

class BitcoinWallet:
    def __init__(self, owner_name, initial_balance=0.0):
        self.owner_name = owner_name
        self.balance = initial_balance
        self.address = self.generate_address()

    def generate_address(self):
        random_salt = str(random.random()).encode('utf-8')
        address = hashlib.sha256(self.owner_name.encode('utf-8') + random_salt).hexdigest()
        return address

    def add_funds(self, amount):
        self.balance += amount

user_wallet = {
    'BTC': BitcoinWallet("User BTC", initial_balance=0.02),
    'XRP': BitcoinWallet("User XRP", initial_balance=100),
    'ETH': BitcoinWallet("User ETH", initial_balance=0.5),
    'SOL': BitcoinWallet("User SOL", initial_balance=2),
    'DOGE': BitcoinWallet("User DOGE", initial_balance=5000),
    'SHIB': BitcoinWallet("User SHIB", initial_balance=10000000)
}

store_wallet = BitcoinWallet("StoreOwner", initial_balance=0.01)  # Store Owner has 0.01 BTC

# Log of received payments
payment_log = []

@app.route('/api/store_balance', methods=['GET'])
def get_store_balance():
    return jsonify({
        'store_owner': store_wallet.owner_name,
        'balance': store_wallet.balance,
        'payment_log': payment_log
    })

@app.route('/api/payment_received', methods=['POST'])
def payment_received():
    data = request.json
    amount = data.get('amount')
    currency = data.get('currency')

    # Add the received payment to the store wallet
    store_wallet.add_funds(amount)

    # Log the payment
    payment_log.append({
        'amount': amount,
        'currency': currency,
        'message': f"{amount:.8f} {currency} received by {store_wallet.owner_name}"
    })

    return jsonify({
        'status': 'success',
        'message': f"Received {amount:.8f} {currency}",
        'balance': store_wallet.balance,
        'payment_log': payment_log
    })

if __name__ == '__main__':
    app.run(port=5001, debug=True)  # Run on a different port
