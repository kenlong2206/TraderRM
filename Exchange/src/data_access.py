import os
import uuid
import json
from datetime import datetime
from Exchange.models.trade import Trade
from Exchange.src.logging_config import setup_logging

# Set up logging
logger = setup_logging()

def get_data_file() -> str:
    # Define the path to the data file
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    # Determine the data file based on environment variable
    is_test = os.getenv('IS_TEST', 'false')
    if is_test == 'true':
        data_file = os.path.join(PROJECT_ROOT, 'Exchange', 'data', 'exchange_data_test.txt')
    else:
        data_file = os.path.join(PROJECT_ROOT, 'Exchange', 'data', 'exchange_data.txt')

    # Ensure the data directory exists
    os.makedirs(os.path.dirname(data_file), exist_ok=True)

    return data_file


def create_trade(trade: Trade) -> Trade:

    trade.trade_id = str(uuid.uuid4())
    trade.trade_status = "new"
    trade.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    trade_data = trade.dict()

    data_file = get_data_file()
    with open(data_file, 'a') as file:
        file.write(json.dumps(trade_data) + "\n")

    return trade

def read_trades(filters=None):
    data_file = get_data_file()

    if not os.path.exists(data_file):
        return []

    trades = []
    with open(data_file, 'r') as file:
        for line in file:
            try:
                # Parse the JSON
                trade_data = json.loads(line.strip())

                # Convert to Trade object
                trade = Trade(**trade_data)
                trades.append(trade)
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {e} for line: {line.strip()}")
            except TypeError as e:
                print(f"TypeError: {e} for data: {trade_data}")
            except Exception as e:
                print(f"Unexpected error: {e} for line: {line.strip()}")

    if filters:
        return [trade for trade in trades if all(getattr(trade, key) == value for key, value in filters.items())]

    return trades

def update_trade(trade: Trade) -> Trade:
    trades = read_trades()
    for i, t in enumerate(trades):
        if t.trade_id == trade.trade_id:
            trades[i] = trade
            break
    else:
        raise ValueError(f"Trade with ID {trade.trade_id} not found")

    data_file = get_data_file()
    with open(data_file, 'w') as file:
        for trade in trades:
            file.write(json.dumps(trade.dict()) + "\n")

    return trade

def delete_trade(trade_id: str):
    trades = read_trades()
    trades = [trade for trade in trades if trade.trade_id != trade_id]

    data_file = get_data_file()
    with open(data_file, 'w') as file:
        for trade in trades:
            file.write(json.dumps(trade.dict()) + "\n")
