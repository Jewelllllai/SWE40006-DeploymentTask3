import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

MONGODB_URI = os.getenv("MONGODB_URI", "")
DB_NAME = os.getenv("DB_NAME", "budget_db")

client = MongoClient(MONGODB_URI) if MONGODB_URI else None
db = client[DB_NAME] if client is not None else None

transactions_collection = db["transactions"] if db is not None else None
savings_collection = db["savings"] if db is not None else None

CURRENCIES = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "MYR": "RM ",
    "SGD": "S$",
    "AUD": "A$",
    "CAD": "C$",
    "INR": "₹",
    "CNY": "¥",
}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-test")
def db_test():
    try:
        if client is None:
            return {"connected": False, "reason": "MONGODB_URI not set"}
        client.admin.command("ping")
        return {"connected": True, "database": DB_NAME}
    except Exception as e:
        return {"connected": False, "error": str(e)}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    currency = request.cookies.get("currency", "USD")
    currency_symbol = CURRENCIES.get(currency, "$")

    transactions = []
    total_income = 0.0
    total_expense = 0.0
    balance = 0.0
    savings = None

    if transactions_collection is not None:
        raw_transactions = list(
            transactions_collection.find().sort("created_at", -1)
        )

        for t in raw_transactions:
            item = {
                "title": str(t.get("title", "")),
                "amount": float(t.get("amount", 0)),
                "category": str(t.get("category", "")),
                "created_at": str(t.get("created_at", "")),
            }
            transactions.append(item)

            if item["category"] == "income":
                total_income += item["amount"]
            elif item["category"] == "expense":
                total_expense += item["amount"]

    balance = total_income - total_expense

    if savings_collection is not None:
        s = savings_collection.find_one({"_id": "main"})
        if s:
            goal = float(s.get("goal", 0))
            saved = float(s.get("saved", 0))
            pct = min(round((saved / goal) * 100, 1), 100) if goal > 0 else 0

            savings = {
                "name": str(s.get("name", "")),
                "goal": goal,
                "saved": saved,
                "pct": pct,
            }

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "transactions": transactions,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "currency": currency,
            "currency_symbol": currency_symbol,
            "savings": savings,
        },
    )


@app.post("/add")
def add_transaction(
    title: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
):
    try:
        if transactions_collection is None:
            return HTMLResponse(
                "MongoDB transactions collection is not connected.",
                status_code=500,
            )

        transactions_collection.insert_one(
            {
                "title": title,
                "amount": amount,
                "category": category,
                "created_at": datetime.now().strftime("%b %d, %Y · %I:%M %p"),
            }
        )

        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        return HTMLResponse(f"Error saving transaction: {str(e)}", status_code=500)


@app.post("/set_currency")
def set_currency(currency: str = Form(...)):
    response = RedirectResponse(url="/", status_code=303)
    if currency in CURRENCIES:
        response.set_cookie("currency", currency)
    return response


@app.post("/savings/set")
def savings_set(
    name: str = Form(...),
    goal: float = Form(...),
):
    try:
        if savings_collection is None:
            return HTMLResponse(
                "MongoDB savings collection is not connected.",
                status_code=500,
            )

        existing = savings_collection.find_one({"_id": "main"})

        if existing:
            savings_collection.update_one(
                {"_id": "main"},
                {"$set": {"name": name, "goal": goal}},
            )
        else:
            savings_collection.insert_one(
                {
                    "_id": "main",
                    "name": name,
                    "goal": goal,
                    "saved": 0.0,
                }
            )

        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        return HTMLResponse(f"Error saving savings goal: {str(e)}", status_code=500)


@app.post("/savings/deposit")
def savings_deposit(amount: float = Form(...)):
    try:
        if savings_collection is None:
            return HTMLResponse(
                "MongoDB savings collection is not connected.",
                status_code=500,
            )

        result = savings_collection.update_one(
            {"_id": "main"},
            {"$inc": {"saved": amount}},
        )

        if result.matched_count == 0:
            return HTMLResponse(
                "No savings goal found. Please create a savings goal first.",
                status_code=400,
            )

        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        return HTMLResponse(f"Error depositing savings: {str(e)}", status_code=500)


@app.post("/savings/delete")
def savings_delete():
    try:
        if savings_collection is None:
            return HTMLResponse(
                "MongoDB savings collection is not connected.",
                status_code=500,
            )

        savings_collection.delete_one({"_id": "main"})
        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        return HTMLResponse(f"Error deleting savings goal: {str(e)}", status_code=500)