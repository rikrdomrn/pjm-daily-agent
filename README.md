# PJM Daily Market Intelligence Agent

An automated AI agent that analyzes PJM real-time energy market data and generates daily intelligence briefs using Claude AI.

## 🎯 Features

- **Automated PJM Market Analysis**: Analyzes real-time LMP, congestion, and energy components
- **Zone-Level Intelligence**: Provides insights across different PJM zones
- **AI-Powered Insights**: Uses Claude API to identify patterns and trading opportunities
- **Email Delivery**: Automatically sends daily briefs to your team
- **Scheduled Execution**: Runs daily via cron for hands-free operation

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database with PJM market data
- Anthropic Claude API key
- Gmail account (or other SMTP email service)

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd pjm-daily-agent
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual credentials
nano .env  # or use VS Code
```

Fill in your actual values:
- `ANTHROPIC_API_KEY`: Get from https://console.anthropic.com/
- `DB_*`: Your PostgreSQL connection details
- `EMAIL_*`: Your email configuration (use Gmail App Password for Gmail)

### 5. Test Database Connection
```bash
python test_db.py
```

### 6. Test Email Configuration
```bash
python test_email.py
```

### 7. Run the Agent
```bash
python pjm_daily_agent.py
```

## 📊 Database Schema

The agent expects the following schema in PostgreSQL:
```sql
-- Schema: pjm_data
-- Table: realtime_prices

CREATE TABLE pjm_data.realtime_prices (
    id BIGINT PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    node_name VARCHAR,
    pnode_id INTEGER,
    lmp NUMERIC,
    energy_component NUMERIC,
    congestion_component NUMERIC,
    loss_component NUMERIC,
    voltage_level VARCHAR,
    zone VARCHAR,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
```

## ⏰ Schedule Daily Execution

To run the agent automatically every morning at 7 AM:
```bash
# Edit crontab
crontab -e

# Add this line (adjust paths as needed)
0 7 * * * /bin/bash -c 'cd /path/to/pjm-daily-agent && source venv/bin/activate && python pjm_daily_agent.py >> logs/cron.log 2>&1'
```

## 📁 Project Structure
```
pjm-daily-agent/
├── pjm_daily_agent.py    # Main agent script
├── test_db.py            # Database connection tester
├── test_email.py         # Email configuration tester
├── check_prices.py       # Database schema explorer
├── explore_db.py         # Full database explorer
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your actual credentials (NOT in git)
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── reports/             # Generated reports (gitignored)
├── logs/                # Execution logs (gitignored)
└── venv/                # Virtual environment (gitignored)
```

## 🔧 Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Test connection
python test_db.py
```

### Email Issues

For Gmail users:
1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the 16-character app password in `.env`

### No Data Available

Check your database has recent data:
```bash
python check_prices.py
```

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature-name`
2. Make your changes
3. Test thoroughly
4. Commit: `git commit -m "Description"`
5. Push: `git push origin feature-name`
6. Create a Pull Request

## 📝 License

Internal use only - Merelec Energy Trading Team

## 👥 Authors

- **Ricardo Morán** - Data & Analytics Manager, Merelec

## 📧 Contact

For questions or issues, contact the Data & Analytics team.