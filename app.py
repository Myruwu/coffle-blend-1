from flask import Flask, request, jsonify, render_template
import random
import hashlib
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('crypto_payment.html')

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

    def deduct_funds(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            return True
        else:
            return False

# Initialize user wallets (example amounts)
user_wallet = {
    'BTC': BitcoinWallet("User BTC", initial_balance=0.02),
    'XRP': BitcoinWallet("User XRP", initial_balance=100),
    'ETH': BitcoinWallet("User ETH", initial_balance=0.5),
    'SOL': BitcoinWallet("User SOL", initial_balance=2),
    'DOGE': BitcoinWallet("User DOGE", initial_balance=5000),
    'SHIB': BitcoinWallet("User SHIB", initial_balance=10000000)
}

# Simulated store wallet (for the store owner)
store_wallet = BitcoinWallet("StoreOwner", initial_balance=0.01)  # Store Owner has 0.01 BTC

# Log of received payments
payment_log = []

@app.route('/api/convert', methods=['POST'])
def convert_to_crypto():
    data = request.json
    php_amount = data.get('php_amount')
    currency = data.get('currency')
    conversion_rate = conversion_rates.get(currency, 0)
    crypto_amount = php_amount / conversion_rate
    return jsonify({'crypto_amount': crypto_amount})

@app.route('/api/pay', methods=['POST'])
def process_payment():
    data = request.json
    php_amount = data.get('php_amount')
    currency = data.get('currency')
    conversion_rate = conversion_rates.get(currency, 0)
    crypto_amount = php_amount / conversion_rate

    if user_wallet[currency].deduct_funds(crypto_amount):
        store_wallet.add_funds(crypto_amount)
        
        # Notify the store owner of the payment
        requests.post("http://localhost:5001/api/payment_received", json={
            'amount': crypto_amount,
            'currency': currency
        })

        payment_log.append({
            'amount': crypto_amount,
            'currency': currency,
            'message': f"{crypto_amount:.8f} {currency} received by {store_wallet.owner_name}"
        })
        return jsonify({
            'status': 'success',
            'message': f"{crypto_amount:.8f} {currency} successfully sent to {store_wallet.owner_name}",
            'user_balance': {c: user_wallet[c].balance for c in user_wallet},
            'store_balance': store_wallet.balance
        })
    else:
        return jsonify({
            'status': 'failed',
            'message': "Insufficient balance in user's wallet."
        }), 400

@app.route('/api/store_balance', methods=['GET'])
def get_store_balance():
    return jsonify({
        'store_owner': store_wallet.owner_name,
        'balance': store_wallet.balance,
        'payment_log': payment_log
    })

if __name__ == '__main__':
    app.run(debug=True)