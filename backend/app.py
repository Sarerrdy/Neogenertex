from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return "Backend Server is Running"


@app.route('/process_payment', methods=['POST'])
def process_payment():
    data = request.json
    # Implement payment processing logic here
    return jsonify({'status': 'Payment processed successfully'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
