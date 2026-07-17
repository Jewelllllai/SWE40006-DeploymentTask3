# 💰 Budget Tracker Application

A modern, full-stack web application for personal finance management built with **FastAPI** and **MongoDB**. Track your income and expenses, manage savings goals, and monitor your financial health—all in one place.

## 🎯 Features

- **Transaction Management**: Add, view, and organize income and expense transactions
- **Multi-Currency Support**: Track finances in 8+ currencies (USD, EUR, GBP, JPY, MYR, SGD, AUD, CAD, INR, CNY)
- **Savings Goals**: Set and track savings goals with visual progress indicators
- **Real-time Dashboard**: View your balance, total income, total expenses, and savings progress at a glance
- **Persistent Storage**: All data is securely stored in MongoDB
- **Responsive Design**: Clean, modern UI optimized for desktop and mobile devices
- **Health Checks**: Built-in endpoints for monitoring application and database connectivity

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python web framework)
- **Database**: MongoDB (NoSQL database)
- **Frontend**: HTML, CSS, JavaScript with Jinja2 templating
- **Static Files**: Static assets management
- **Environment Configuration**: Python-dotenv for secure credential management

## 📋 Project Structure

```
.
├── main.py                 # FastAPI application and core endpoints
├── templates/              # HTML templates (Jinja2)
│   └── index.html         # Main dashboard template
├── static/                # Static assets (CSS, JS, images)
├── .env                   # Environment variables (not committed)
└── README.md             # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MongoDB instance (local or cloud)
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jewelllllai/SWE40006-DeploymentTask3.git
   cd SWE40006-DeploymentTask3
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   DB_NAME=budget_db
   ```

4. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```
   The application will be available at `http://localhost:8000`

## 📚 API Endpoints

### Health & Monitoring
- `GET /health` - Check application status
- `GET /db-test` - Test MongoDB connectivity and configuration

### Dashboard
- `GET /` - Main dashboard displaying transactions and savings overview

### Transactions
- `POST /add` - Add a new transaction
  - Parameters: `title`, `amount`, `category` (income/expense)

### Currency
- `POST /set_currency` - Set preferred currency for display
  - Parameters: `currency` (USD, EUR, GBP, etc.)

### Savings Goals
- `POST /savings/set` - Create or update savings goal
  - Parameters: `name`, `goal` (target amount)
- `POST /savings/deposit` - Add funds to savings goal
  - Parameters: `amount`
- `POST /savings/delete` - Delete current savings goal

## 💡 Key Features Explained

### Multi-Currency Support
The app supports multiple currencies with appropriate symbols:
- 💵 USD ($), EUR (€), GBP (£), JPY (¥)
- MYR (RM), SGD (S$), AUD (A$), CAD (C$)
- INR (₹), CNY (¥)

Currency preference is stored in browser cookies for persistence.

### Transaction Categorization
All transactions are categorized as either:
- **Income**: Money coming in
- **Expense**: Money going out

The dashboard automatically calculates:
- Total Income
- Total Expenses
- Current Balance (Income - Expenses)

### Savings Tracking
Set a savings goal with a target amount and track your progress:
- Visual percentage indicator (0-100%)
- Easily deposit additional funds
- Update or delete goals as needed

### Database Integration
- **Transactions Collection**: Stores all income/expense records with timestamps
- **Savings Collection**: Maintains savings goal data (stored with `_id: "main"`)
- Auto-sorted transactions by most recent first

## 🔒 Security Features

- Environment variables for sensitive credentials (never hardcoded)
- Proper error handling and validation
- MongoDB connection pooling
- Input sanitization through FastAPI's automatic validation

## 📝 Sample Workflow

1. **Start**: User accesses the dashboard
2. **Add Transaction**: User enters transaction details and submits
3. **View Balance**: Dashboard updates with new transaction
4. **Set Savings Goal**: User creates a savings goal
5. **Track Progress**: User deposits funds toward the goal
6. **Monitor**: Dashboard displays current savings progress

## 🐛 Troubleshooting

### "MongoDB transactions collection is not connected"
- Ensure `MONGODB_URI` is correctly set in `.env`
- Verify MongoDB cluster is running and accessible
- Check database credentials and network permissions

### Database connection fails
- Test connectivity using `GET /db-test` endpoint
- Verify `MONGODB_URI` environment variable
- Check MongoDB Atlas firewall rules (if using cloud MongoDB)

## 📈 Future Enhancements

- Transaction filtering and search
- Monthly/yearly reports and analytics
- Budget categorization and limits
- Multiple savings goals
- Data export (CSV, PDF)
- User authentication and multi-user support
- Mobile app version

## 👨‍💻 Author

**Jewelllllai**

## 📄 License

This project is part of SWE40006 Deployment Task 3.

---

**Note**: This is a deployment task project. Ensure proper security practices when deploying to production, including secret management, rate limiting, and authentication.
