from fastapi import FastAPI, Body
from pydantic import BaseModel

app = FastAPI()


class OpenPositionRequest(BaseModel):
    Exchange: str


class OpenPositionResponse(BaseModel):
    TradeResult: str


@app.post("/exchange")
async def exchange(data: OpenPositionRequest = Body(...)):
    if data.Exchange == "Binance":
        result = "Success"
    elif data.Exchange == "Kucoin":
        result = "Invalid Exchange"
    else:
        result = "Invalid Request"
    return OpenPositionResponse(TradeResult=result)
