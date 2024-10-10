from fastapi import APIRouter, Query
from app.predict import predict_stock_change
from app.stocks_info import get_stock_open_price, get_top_headlines

router = APIRouter()

@router.get("/get_stock_prediction/")
def read_predictions(company_name: str = Query(...), symbol: str = Query(...)):
    try:
        open_price = get_stock_open_price(symbol)
        if isinstance(open_price, str) and "Error" in open_price:
            raise ValueError(f"Failed to retrieve stock price for {symbol}: {open_price}")

        headlines = get_top_headlines(company_name)
        if not headlines:
            raise ValueError(f"Failed to retrieve headlines for {company_name}")

        predicted_change, sentiment_score = predict_stock_change(open_price, symbol, [article['title'] for article in headlines])
        predicted_change = round(predicted_change, 2)
        predicted_change = str(predicted_change) + "%"
        return {"company_name": company_name, "symbol": symbol, "open_price": open_price, "sentiment_score": sentiment_score, "predicted_change": predicted_change}
    except ValueError as e:
        print(f"Error in prediction: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"Unexpected error in prediction: {e}")
        return {"error": "An unexpected error occurred"}

@router.get("/test")
def test():
    return {"message": "API is working!"}