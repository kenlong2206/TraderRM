from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import os
import uuid


app = FastAPI()

# Define the path to the trade log file relative to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_file = os.path.join(PROJECT_ROOT, 'data', 'exchange_log.txt')

class Trade(BaseModel):
    trade_id: Optional[str] = None
    trade_status: Optional[str] = None
    time: Optional[str] = None
    title: Optional[str] = None
    notes: Optional[str] = None
    exchange: str
    order_type: str
    currency_pair: str
    limit_order_price: float
    take_profit_price: float
    stop_loss: float
    amount: float
    leverage: int
    user: str


def ensure_data_directory_exists():
    os.makedirs(os.path.dirname(data_file), exist_ok=True)

@app.post("/make_trade")
async def make_trade(trade: Trade, request: Request):
    # Generate a unique trade ID if not provided
    trade.trade_id = str(uuid.uuid4())

    # Set trade status and time
    trade.trade_status = "pending"
    trade.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Convert trade data to dictionary and include trade_id and status
    trade_data = trade.dict()

    # Ensure the directory exists
    ensure_data_directory_exists()

    # Write the data to the file
    with open(data_file, 'a') as file:
        file.write(f"{trade_data}\n")

    return {"status": "success", "data": trade}

@app.get("/get_all_trades")
async def get_all_trades():
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Trade data file not found")

    with open(data_file, 'r') as file:
        data = file.read()

    return {"status": "success", "data": data}

@app.get("/get_trade/{trade_id}")
async def get_trade(trade_id: str):
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Trade data file not found")

    with open(data_file, 'r') as file:
        lines = file.readlines()

    trade_data = None
    for line in lines:
        trade = eval(line.strip())
        if trade["trade_id"] == trade_id:
            trade_data = trade
            break

    if trade_data is None:
        raise HTTPException(status_code=404, detail=f"Trade with ID {trade_id} not found")

    return {"status": "success", "data": trade_data}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
