import os
import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from Exchange.models.trade import Trade
from logging_config import setup_logging

# Set up logging
logger = setup_logging()

# Define the path to the data file
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
data_file = os.path.join(PROJECT_ROOT, 'Exchange', 'data', 'exchange_log.txt')

# Ensure the data directory exists
os.makedirs(os.path.dirname(data_file), exist_ok=True)

def create_trade(trade: Trade) -> Trade:
    trade.trade_id = str(uuid.uuid4())
    trade.trade_status = "new"
    trade.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    trade_data = trade.dict()

    with open(data_file, 'a') as file:
        file.write(json.dumps(trade_data) + "\n")

    return trade

def read_trades(filters: Optional[Dict[str, Any]] = None) -> List[Trade]:
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
                # Log the error with the problematic line
                print(f"JSONDecodeError: {e} for line: {line.strip()}")
                continue
            except TypeError as e:
                # Log the error with the problematic data structure
                print(f"TypeError: {e} for data: {trade_data}")
                continue
            except Exception as e:
                # Log any other unexpected errors
                print(f"Unexpected error: {e} for line: {line.strip()}")
                continue

    if filters:
        filtered_trades = []
        for trade in trades:
            match = True
            for key, value in filters.items():
                if getattr(trade, key) != value:
                    match = False
                    break
            if match:
                filtered_trades.append(trade)
        return filtered_trades

    return trades

def update_trade(trade: Trade) -> Trade:
    trades = read_trades()
    for i, t in enumerate(trades):
        if t.trade_id == trade.trade_id:
            trades[i] = trade
            break
    else:
        raise ValueError(f"Trade with ID {trade.trade_id} not found")

    with open(data_file, 'w') as file:
        for trade in trades:
            file.write(json.dumps(trade.dict()) + "\n")

    return trade

def delete_trade(trade_id: str):
    trades = read_trades()
    trades = [trade for trade in trades if trade.trade_id != trade_id]

    with open(data_file, 'w') as file:
        for trade in trades:
            file.write(json.dumps(trade.dict()) + "\n")
