import os
from Exchange.src.logging_config import setup_logging
from fastapi import FastAPI, HTTPException
from Exchange.models.trade import Trade
from Exchange.src import data_access

# set the environment variable to indicate whether to use test files for data and logs
os.environ['IS_TEST'] = 'false'

# Set up logging
logger = setup_logging()

app = FastAPI()


@app.post("/make_trade")
async def make_trade(trade: Trade):
    saved_trade = data_access.create_trade(trade)
    logger.info(f"Trade created: {saved_trade}")
    return {"status": "success", "trade_id": saved_trade.trade_id, "data": saved_trade}


@app.get("/get_all_trades")
async def get_all_trades():
    trades = data_access.read_trades()
    logger.info(f"Get all trades")
    if not trades:
        logger.info(f"Get all trades exception - No trade log exists")
        raise HTTPException(status_code=404, detail="No trade log exists")

    return {"status": "success", "data": trades}


@app.get("/get_trade/{trade_id}")
async def get_trade(trade_id: str):
    trades = data_access.read_trades(filters={"trade_id": trade_id})
    if not trades:
        logger.info(f"Get trade {trade_id} not found")
        raise HTTPException(status_code=404, detail="Trade not found")
    logger.info(f"Get trade {trade_id}")
    return {"status": "success", "data": trades[0]}


@app.put("/update_trade")
async def update_trade(trade: Trade):
    try:
        updated_trade = data_access.update_trade(trade)
        logger.info(f"Trade updated: {updated_trade}")
        return {"status": "success", "trade_id": updated_trade.trade_id, "data": updated_trade}
    except ValueError as e:
        logger.info(f"update_trade error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/delete_trade/{trade_id}")
async def delete_trade(trade_id: str):
    data_access.delete_trade(trade_id)
    logger.info(f"Trade deleted: {trade_id}")
    return {"status": "success", "message": f"Trade {trade_id} deleted"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
