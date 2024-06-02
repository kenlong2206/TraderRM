import pytest
import os
from fastapi.testclient import TestClient
from Exchange.src.main import app

@pytest.fixture
def client():
    return TestClient(app)



def test_make_trade1_success(client):
    response = client.post('/make_trade', json={
        "exchange": "Binance",
        "order_type": "limit",
        "currency_pair": "BTC/USD",
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
        "exchange": "Binance",
        "order_type": "market",
        "currency_pair": "ETH/USD",
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
    assert 'time' in response.json()['data']
    assert 'test_user' in response.json()['data']

def test_get_trades_not_found(client):

    # rename the file so it generates a not found error
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    data_file = os.path.join(PROJECT_ROOT, 'Exchange', 'data', 'exchange_log.txt')

    # rename the file
    backup_file = data_file + '.bak'
    os.rename(data_file, backup_file)

    # call to confirm error as file not found
    response = client.get('/get_all_trades')
    assert response.status_code == 404

    # now rename it back
    os.rename(backup_file, data_file)

def test_get_trade_success(client):
    response = client.post('/make_trade', json={
        "exchange": "Binance",
        "order_type": "market",
        "currency_pair": "ETH/USD",
        "limit_order_price": 4000,
        "take_profit_price": 5000,
        "stop_loss": 3900,
        "amount": 100,
        "leverage": 20,
        "user": "test_user"
    })
    trade_id = response.json()['data']['trade_id']

    response = client.get(f'/get_trade/{trade_id}')
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    assert response.json()['data']['trade_id'] == trade_id
    assert response.json()['data']['user'] == 'test_user'
    assert response.json()['data']['trade_status'] == 'pending'
