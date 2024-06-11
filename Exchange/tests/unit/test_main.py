import pytest
import os
from fastapi.testclient import TestClient
from Exchange.src.logging_config import setup_logging
from Exchange.src.main import app

# Set up logging to use a test log file
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
test_log_file = os.path.join(PROJECT_ROOT, 'Exchange', 'logs', 'exchange_log_test.txt')
logger = setup_logging(file=test_log_file)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def setup_teardown(request):
    # setup and teardown function to create the test environment before each test, and revert it after each test.
    # The tests should preserve the trade log to its original state

    # set the environment variable to indicate testing
    os.environ['IS_TEST'] = 'true'

    # write to log file:
    test_name = request.node.name
    logger.info(f"UNIT TEST START: {test_name}")

    # now run the tests can start
    yield


    logger.info(f"UNIT TEST END: {test_name}")

    # reset the environment variable to indicate not testing
    os.environ['IS_TEST'] = 'false'

def test_make_trade_success(client, setup_teardown):
    # post a trade (if a trade log doesnt exist it should create one)
    response = client.post('/make_trade', json={"title": "trade 1 to create a new trade log", "exchange": "Binance", "order_type": "limit", "currency_pair": "BTC/USD", "limit_order_price": 50000, "take_profit_price": 55000, "stop_loss": 45000, "amount": 1, "leverage": 10, "user": "test_user"})
    logger.info(f"UNIT TEST - 1st trade created: {response.json()['data']}")
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    assert response.json()['data']['title'] == 'trade 1 to create a new trade log'


    # now post a second trade (the trade log should exist)
    response = client.post('/make_trade', json={"title": "trade 2 to append an existing trade log", "exchange": "Binance", "order_type": "limit", "currency_pair": "BTC/USD", "limit_order_price": 50000, "take_profit_price": 55000, "stop_loss": 45000, "amount": 1, "leverage": 10, "user": "test_user"})
    logger.info(f"UNIT TEST - 2nd Trade created: {response.json()['data']}")
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


def test_get_all_trades_no_file(client, setup_teardown):

    # rename data file
    data_file = os.path.join(PROJECT_ROOT, 'Exchange', 'data', 'exchange_data_test.txt')
    os.rename(data_file, data_file + '.bak')

    # call to confirm error as no trade log exists
    response = client.get('/get_all_trades')
    assert response.status_code == 404
    assert response.json()['detail'] == "No trade log exists"

    # restore original name
    os.rename(data_file + '.bak', data_file)


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

def test_update_trade_success(client, setup_teardown):
    # post a trade and store its trade_id
    response = client.post('/make_trade', json={"title": "initial trade xxx", "exchange": "Binance", "order_type": "limit", "currency_pair": "BTC/USD", "limit_order_price": 50000, "take_profit_price": 55000, "stop_loss": 45000, "amount": 1, "leverage": 10, "user": "test_user"})
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    trade_id = response.json()['data']['trade_id']

    # read the trade back
    response = client.get(f'/get_trade/{trade_id}')
    updated_trade = response.json()['data']
    updated_trade['trade_id'] = trade_id
    updated_trade['title'] = "updated trade"
    # print(f"\nUpdated trade before PUT: {updated_trade}")

    # update trade
    response = client.put('/update_trade/', json=updated_trade)
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    assert response.json()['data']['title'] == "updated trade"
