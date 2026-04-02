import os
from datetime import datetime
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

MONGODB_URI = os.getenv("MONGODB_URI", "")
DB_NAME = os.getenv("DB_NAME", "budget_db")

client = MongoClient(MONGODB_URI) if MONGODB_URI else None
db = client[DB_NAME] if client else None

transactions_collection = db["transactions"] if db else None
savings_collection = db["savings"] if db else None

CURRENCIES = {
    "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥",
    "MYR": "RM ", "SGD": "S$", "AUD": "A$", "CAD": "C$",
    "INR": "₹", "CNY": "¥",
}


@app.get("/health")
def health():
    return {"status": "ok"}


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
        raw_transactions = list(transactions_collection.find().sort("created_at", -1))
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
    if transactions_collection is not None:
        transactions_collection.insert_one({
            "title": title,
            "amount": amount,
            "category": category,
            "created_at": datetime.now().strftime("%b %d, %Y · %I:%M %p"),
        })
    return RedirectResponse(url="/", status_code=303)


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
    if savings_collection is not None:
        existing = savings_collection.find_one({"_id": "main"})
        if existing:
            savings_collection.update_one(
                {"_id": "main"},
                {"$set": {"name": name, "goal": goal}}
            )
        else:
            savings_collection.insert_one({
                "_id": "main",
                "name": name,
                "goal": goal,
                "saved": 0.0,
            })
    return RedirectResponse(url="/", status_code=303)


@app.post("/savings/deposit")
def savings_deposit(amount: float = Form(...)):
    if savings_collection is not None:
        savings_collection.update_one(
            {"_id": "main"},
            {"$inc": {"saved": amount}}
        )
    return RedirectResponse(url="/", status_code=303)


@app.post("/savings/delete")
def savings_delete():
    if savings_collection is not None:
        savings_collection.delete_one({"_id": "main"})
    return RedirectResponse(url="/", status_code=303)