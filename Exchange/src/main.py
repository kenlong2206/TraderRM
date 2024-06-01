from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
import os

app = FastAPI()
data_file = 'Exchange/data/exchange_log.txt'

class Trade(BaseModel):
    order_type: str
    crypto_currency_pair: str
    limit_order_price: float
    take_profit_price: float
    stop_loss: float
    amount: float
    leverage: int
    user: str

@app.post("/make_trade")
async def make_trade(trade: Trade, request: Request):
    # Get current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Construct the data to write
    data_to_write = f"Time: {current_time}, User: {trade.user}, Trade Data: {trade.dict()}\n"

    # Write the data to the file
    with open(data_file, 'a') as file:
        file.write(data_to_write)

    return {"status": "success", "data": trade}

@app.get("/get_all_trades")
async def get_all_trades():
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Trade data file not found")

    with open(data_file, 'r') as file:
        data = file.read()

    return {"status": "success", "data": data}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
