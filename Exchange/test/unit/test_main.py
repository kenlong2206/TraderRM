import unittest
from fastapi.testclient import TestClient
from main import app
import os

class TestMain(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.data_file = 'trades.txt'
        # Ensure the file is empty before each test
        open(self.data_file, 'w').close()

    def tearDown(self):
        # Clean up the file after each test
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    def test_trade_success(self):
        response = self.client.post('/trade', json={
            "order_type": "limit",
            "crypto_currency_pair": "BTC/USD",
            "limit_order_price": 50000,
            "take_profit_price": 55000,
            "stop_loss": 45000,
            "amount": 1,
            "leverage": 10,
            "user": "test_user"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertIn('data', response.json())

    def test_read_trades_success(self):
        # First, create a trade to have something in the file
        self.client.post('/trade', json={
            "order_type": "limit",
            "crypto_currency_pair": "BTC/USD",
            "limit_order_price": 50000,
            "take_profit_price": 55000,
            "stop_loss": 45000,
            "amount": 1,
            "leverage": 10,
            "user": "test_user"
        })
        response = self.client.get('/trades')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertIn('Time:', response.json()['data'])
        self.assertIn('User: test_user', response.json()['data'])

    def test_read_trades_not_found(self):
        response = self.client.get('/trades')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
