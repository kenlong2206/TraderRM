import pytest
import os
from fastapi.testclient import TestClient
from Exchange.src.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_make_trade1_success(client):
    response = client.post('/make_trade', json={
        "order_type": "limit",
        "crypto_currency_pair": "BTC/USD",
        "limit_order_price": 50000,
        "take_profit_price": 55000,
        "stop_loss": 45000,
        "amount": 1,
        "leverage": 10,
        "user": "test_user"
    })
    assert response.status_code == 200
    assert response.json()['status'] == 'success'

def test_make_trade2_success(client):
    response = client.post('/make_trade', json={
        "order_type": "market",
        "crypto_currency_pair": "ETH/USD",
        "limit_order_price": 4000,
        "take_profit_price": 5000,
        "stop_loss": 3900,
        "amount": 100,
        "leverage": 20,
        "user": "test_user"
    })
    assert response.status_code == 200
    assert response.json()['status'] == 'success'

def test_get_trades_success(client):
    response = client.get('/get_all_trades')
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    assert 'Time:' in response.json()['data']
    assert 'User: test_user' in response.json()['data']

def test_get_trades_not_found(client):

    # rename the file so it generates a not found error
    data_file_path = 'Exchange/data/exchange_log.txt'
    backup_file_path = data_file_path + '.bak'
    os.rename(data_file_path, backup_file_path)

    response = client.get('/get_all_trades')
    assert response.status_code == 404

    # now rename it back
    os.rename(backup_file_path, data_file_path)
