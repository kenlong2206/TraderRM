import pytest
import os
from fastapi.testclient import TestClient
from Exchange.src.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def setup_teardown():
    # setup and teardown function to create the test environment before each test, and revert it after each test

    # firstly start by creating a backup of any current trade log file
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    data_file = os.path.join(PROJECT_ROOT, 'Exchange', 'data', 'exchange_log.txt')
    backup_file = data_file + '.bak'

    # remove any old backup files
    if os.path.exists(backup_file):
        os.remove(data_file)

    # if there is a trade log back it up
    if os.path.exists(data_file):
        os.rename(data_file, backup_file)

    # now the tests can start with no trade log
    yield data_file

    # delete the trade log created for testing and restore the original trade log
    if os.path.exists(data_file):
        os.remove(data_file)
    if os.path.exists(backup_file):
        os.rename(backup_file, data_file)

def test_make_trade_success(client, setup_teardown):
    # post a trade (if a trade log doesnt exist it should create one)
    response = client.post('/make_trade', json={"title": "trade 1 to create a new trade log", "exchange": "Binance", "order_type": "limit", "currency_pair": "BTC/USD", "limit_order_price": 50000, "take_profit_price": 55000, "stop_loss": 45000, "amount": 1, "leverage": 10, "user": "test_user"})
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    assert response.json()['data']['title'] == 'trade 1 to create a new trade log'

    # now post a second trade (the trade log should exist)
    response = client.post('/make_trade', json={"title": "trade 2 to append an existing trade log", "exchange": "Binance", "order_type": "limit", "currency_pair": "BTC/USD", "limit_order_price": 50000, "take_profit_price": 55000, "stop_loss": 45000, "amount": 1, "leverage": 10, "user": "test_user"})
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    assert response.json()['data']['title'] == 'trade 2 to append an existing trade log'


def test_get_all_trades_success(client, setup_teardown):

    # post 2 trades to create a trade log
    response = client.post('/make_trade', json={"title": "trade 1", "exchange": "Binance", "order_type": "limit", "currency_pair": "BTC/USD", "limit_order_price": 50000, "take_profit_price": 55000, "stop_loss": 45000, "amount": 1, "leverage": 10, "user": "test_user"})
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    response = client.post('/make_trade', json={"title": "trade 2", "exchange": "Binance", "order_type": "limit", "currency_pair": "BTC/USD", "limit_order_price": 50000, "take_profit_price": 55000, "stop_loss": 45000, "amount": 1, "leverage": 10, "user": "test_user"})
    assert response.status_code == 200
    assert response.json()['status'] == 'success'

    # request all trades from trade log
    response = client.get('/get_all_trades')
    assert response.status_code == 200
    assert response.json()['status'] == 'success'

    # extract the data dict and check it is populated
    data = response.json()['data']
    assert isinstance(data, list)
    assert len(data) > 0

    # check each record contains data
    for trade in data:
        assert 'time' in trade
        assert 'trade_id' in trade
        assert 'user' in trade
        assert 'order_type' in trade


def test_get_all_trades_not_found(client, setup_teardown):

    # call to confirm error as no trade log exists
    response = client.get('/get_all_trades')
    assert response.status_code == 404
    assert response.json()['detail'] == "No trade log exists"

def test_get_trade_success(client, setup_teardown):
    # post a trade and store its trade_id
    response = client.post('/make_trade', json={"title": "trade 1", "exchange": "Binance", "order_type": "limit", "currency_pair": "BTC/USD", "limit_order_price": 50000, "take_profit_price": 55000, "stop_loss": 45000, "amount": 1, "leverage": 10, "user": "test_user"})
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    trade_id = response.json()['data']['trade_id']

    # lookup the trade_id
    response = client.get(f'/get_trade/{trade_id}')
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    assert response.json()['detail'] == "Trade log exists"
    assert response.json()['data']['trade_id'] == trade_id
    assert response.json()['data']['user'] == 'test_user'
    assert response.json()['data']['trade_status'] == 'new'


def test_delete_trade_success(client, setup_teardown):
    # post a trade and store its trade_id
    response = client.post('/make_trade', json={"title": "trade 1", "exchange": "Binance", "order_type": "limit", "currency_pair": "BTC/USD", "limit_order_price": 50000, "take_profit_price": 55000, "stop_loss": 45000, "amount": 1, "leverage": 10, "user": "test_user"})
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    trade_id = response.json()['data']['trade_id']

    # delete trade
    response = client.delete(f'/delete_trade/{trade_id}')
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    message_response = f"Trade {trade_id} deleted"
    assert response.json()['message'] == message_response

# def test_update_trade_success(client, setup_teardown):
#     # post a trade and store its trade_id
#     response = client.post('/make_trade', json={"title": "initial trade", "exchange": "Binance", "order_type": "limit", "currency_pair": "BTC/USD", "limit_order_price": 50000, "take_profit_price": 55000, "stop_loss": 45000, "amount": 1, "leverage": 10, "user": "test_user"})
#     assert response.status_code == 200
#     assert response.json()['status'] == 'success'
#     trade_id = response.json()['data']['trade_id']
#
#     # delete trade
#     response = client.put(f'/update_trade/{trade_id}', json={"title": "updated trade", "exchange": "Binance", "order_type": "limit", "currency_pair": "BTC/USD", "limit_order_price": 50000, "take_profit_price": 55000, "stop_loss": 45000, "amount": 1, "leverage": 10, "user": "test_user"})
#     assert response.status_code == 200
#     assert response.json()['status'] == 'success'
#     assert response.json()['data']['title'] == "updated trade"
