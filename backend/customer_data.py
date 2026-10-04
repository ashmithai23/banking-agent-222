"""
Comprehensive customer dataset for VectraBank.
Provides 35+ realistic, diverse customer profiles across retail, wealth, commercial,
mortgage, student, and compliance monitoring tiers.
"""

CUSTOMER_DATA = [
    {
        "customer_id": "12345",
        "income": 75000.0,
        "credit_score": 780,
        "account_type": "premium_plus",
        "customer_since": "2019-05-15",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "mortgage", "investment", "credit_card"],
        "last_review_date": "2024-01-10",
        "sample_query": "I need comprehensive financial planning including index fund compounding and retirement options.",
        "recent_transactions": [
            {"amount": 4500.00, "description": "Salary Direct Deposit - Apex Tech", "ts": "2024-03-20"},
            {"amount": -1500.00, "description": "Mortgage Payment Auto-Debit", "ts": "2024-03-15"},
            {"amount": -300.00, "description": "Vanguard Investment Contribution", "ts": "2024-03-10"},
            {"amount": -145.20, "description": "Pacific Gas & Electric Utility", "ts": "2024-03-05"},
            {"amount": -89.40, "description": "Trader Joe's Groceries", "ts": "2024-03-02"}
        ]
    },
    {
        "customer_id": "67890",
        "income": 45000.0,
        "credit_score": 680,
        "account_type": "standard",
        "customer_since": "2021-08-20",
        "risk_tier": "medium",
        "banking_products": ["checking", "savings", "credit_card"],
        "last_review_date": "2024-02-15",
        "sample_query": "I want to apply for a first-time homebuyer mortgage and understand my maximum borrowing limit.",
        "recent_transactions": [
            {"amount": 3200.00, "description": "Bi-Weekly Payroll Deposit", "ts": "2024-03-20"},
            {"amount": -1200.00, "description": "Residential Lease Rent Payment", "ts": "2024-03-14"},
            {"amount": -380.00, "description": "Honda Financial Services Auto Loan", "ts": "2024-03-08"},
            {"amount": -150.00, "description": "Federal Student Loan Servicing", "ts": "2024-03-02"}
        ]
    },
    {
        "customer_id": "11111",
        "income": 28000.0,
        "credit_score": 620,
        "account_type": "basic",
        "customer_since": "2023-01-10",
        "risk_tier": "high",
        "banking_products": ["checking"],
        "last_review_date": "2024-03-01",
        "sample_query": "I noticed unusual debit transactions on my card and need to dispute them immediately.",
        "recent_transactions": [
            {"amount": 2300.00, "description": "Retail Logistics Payroll Deposit", "ts": "2024-03-20"},
            {"amount": -800.00, "description": "Apartment Rent Payment", "ts": "2024-03-12"},
            {"amount": -300.00, "description": "Credit Card Minimum Due", "ts": "2024-03-07"},
            {"amount": -35.00, "description": "Overdraft Incident Fee", "ts": "2024-03-01"}
        ]
    },
    {
        "customer_id": "20101",
        "income": 240000.0,
        "credit_score": 815,
        "account_type": "private_wealth",
        "customer_since": "2015-03-12",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "investment", "credit_card", "jumbo_mortgage"],
        "last_review_date": "2024-02-28",
        "sample_query": "I would like to explore tax-advantaged municipal bond portfolios and private wealth liquidity options.",
        "recent_transactions": [
            {"amount": 16000.00, "description": "Executive Compensation - Bi-Weekly", "ts": "2024-03-25"},
            {"amount": -4800.00, "description": "Jumbo Mortgage Automatic Draft", "ts": "2024-03-18"},
            {"amount": -5000.00, "description": "Private Wealth Fund Allocation", "ts": "2024-03-10"},
            {"amount": -620.00, "description": "The Ritz-Carlton Dining", "ts": "2024-03-04"}
        ]
    },
    {
        "customer_id": "20102",
        "income": 135000.0,
        "credit_score": 745,
        "account_type": "premium_plus",
        "customer_since": "2018-09-01",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "investment", "credit_card"],
        "last_review_date": "2024-01-22",
        "sample_query": "Can I refinance my 30-year fixed loan into a 15-year term to reduce overall lifetime interest?",
        "recent_transactions": [
            {"amount": 8400.00, "description": "Software Engineering Payroll", "ts": "2024-03-22"},
            {"amount": -2200.00, "description": "Conforming Loan Payment", "ts": "2024-03-16"},
            {"amount": -1000.00, "description": "Fidelity Roth IRA Transfer", "ts": "2024-03-08"},
            {"amount": -180.00, "description": "Costco Wholesale", "ts": "2024-03-03"}
        ]
    },
    {
        "customer_id": "20103",
        "income": 520000.0,
        "credit_score": 790,
        "account_type": "commercial",
        "customer_since": "2017-06-18",
        "risk_tier": "low",
        "banking_products": ["checking", "commercial_line", "merchant_services", "treasury_management"],
        "last_review_date": "2024-03-15",
        "sample_query": "We require a $250,000 revolving line of credit expansion for quarterly inventory acquisition.",
        "recent_transactions": [
            {"amount": 42000.00, "description": "Stripe Merchant Batch Settlement", "ts": "2024-03-24"},
            {"amount": -28500.00, "description": "Gusto Payroll ACH Outflow", "ts": "2024-03-20"},
            {"amount": -8200.00, "description": "Commercial Warehouse Lease", "ts": "2024-03-15"},
            {"amount": -3400.00, "description": "Corporate AWS Cloud Services", "ts": "2024-03-10"}
        ]
    },
    {
        "customer_id": "20104",
        "income": 58000.0,
        "credit_score": 640,
        "account_type": "standard",
        "customer_since": "2022-04-11",
        "risk_tier": "medium",
        "banking_products": ["checking", "savings", "auto_loan"],
        "last_review_date": "2024-02-01",
        "sample_query": "Can I consolidate $14,000 in credit card balances into a lower fixed-rate personal loan?",
        "recent_transactions": [
            {"amount": 3400.00, "description": "Health Network Payroll Direct Deposit", "ts": "2024-03-21"},
            {"amount": -1150.00, "description": "Apartment Community Rent", "ts": "2024-03-14"},
            {"amount": -450.00, "description": "Car Loan Payment", "ts": "2024-03-09"},
            {"amount": -220.00, "description": "High-Interest Credit Card Payment", "ts": "2024-03-02"}
        ]
    },
    {
        "customer_id": "20105",
        "income": 95000.0,
        "credit_score": 710,
        "account_type": "standard",
        "customer_since": "2020-11-05",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "credit_card"],
        "last_review_date": "2024-01-18",
        "sample_query": "What are current high-yield savings interest rates and 12-month CD certificate yields?",
        "recent_transactions": [
            {"amount": 5800.00, "description": "Consulting Group Direct Deposit", "ts": "2024-03-22"},
            {"amount": -1650.00, "description": "Suburban Lease Rent", "ts": "2024-03-15"},
            {"amount": -800.00, "description": "Transfer to High-Yield Savings", "ts": "2024-03-10"},
            {"amount": -130.00, "description": "Whole Foods Market", "ts": "2024-03-04"}
        ]
    },
    {
        "customer_id": "20106",
        "income": 32000.0,
        "credit_score": 580,
        "account_type": "basic",
        "customer_since": "2023-08-19",
        "risk_tier": "critical",
        "banking_products": ["checking"],
        "last_review_date": "2024-03-12",
        "sample_query": "I have multiple consecutive cash deposits just under $10k and need to clarify compliance holds.",
        "recent_transactions": [
            {"amount": 9500.00, "description": "Branch Cash Deposit - Counter", "ts": "2024-03-24"},
            {"amount": 9200.00, "description": "Branch Cash Deposit - Counter", "ts": "2024-03-22"},
            {"amount": 9800.00, "description": "Branch Cash Deposit - Counter", "ts": "2024-03-20"},
            {"amount": -18000.00, "description": "International Outgoing Wire - Remittance", "ts": "2024-03-18"}
        ]
    },
    {
        "customer_id": "20107",
        "income": 110000.0,
        "credit_score": 765,
        "account_type": "premium",
        "customer_since": "2019-10-30",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "credit_card", "auto_loan"],
        "last_review_date": "2024-02-14",
        "sample_query": "I am looking for an auto refinance to lower my APR from 6.8% to current prime rates.",
        "recent_transactions": [
            {"amount": 6900.00, "description": "Bi-Weekly Corporate Salary", "ts": "2024-03-21"},
            {"amount": -1800.00, "description": "Mortgage Payment", "ts": "2024-03-15"},
            {"amount": -520.00, "description": "Auto Financing Monthly Installment", "ts": "2024-03-09"},
            {"amount": -310.00, "description": "Target Department Store", "ts": "2024-03-05"}
        ]
    },
    {
        "customer_id": "20108",
        "income": 185000.0,
        "credit_score": 805,
        "account_type": "premium_plus",
        "customer_since": "2016-07-25",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "investment", "credit_card", "heloc"],
        "last_review_date": "2024-01-30",
        "sample_query": "Can I draw $60,000 from my Home Equity Line of Credit (HELOC) for home energy renovations?",
        "recent_transactions": [
            {"amount": 11500.00, "description": "Medical Practice Partner Distribution", "ts": "2024-03-25"},
            {"amount": -3100.00, "description": "First Mortgage Auto-Debit", "ts": "2024-03-16"},
            {"amount": -2000.00, "description": "529 College Savings Plan", "ts": "2024-03-11"},
            {"amount": -450.00, "description": "Home Depot Building Materials", "ts": "2024-03-06"}
        ]
    },
    {
        "customer_id": "20109",
        "income": 42000.0,
        "credit_score": 665,
        "account_type": "standard",
        "customer_since": "2021-02-14",
        "risk_tier": "medium",
        "banking_products": ["checking", "savings", "credit_card"],
        "last_review_date": "2024-02-10",
        "sample_query": "Am I eligible to request a credit card limit increase from $2,500 to $6,000?",
        "recent_transactions": [
            {"amount": 2900.00, "description": "Hospital Administrative Salary", "ts": "2024-03-20"},
            {"amount": -1050.00, "description": "Rent Payment - Zelle", "ts": "2024-03-14"},
            {"amount": -250.00, "description": "Credit Card Payment", "ts": "2024-03-08"},
            {"amount": -85.00, "description": "Shell Oil Fuel", "ts": "2024-03-03"}
        ]
    },
    {
        "customer_id": "20110",
        "income": 310000.0,
        "credit_score": 830,
        "account_type": "private_wealth",
        "customer_since": "2014-12-05",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "investment", "credit_card", "trust_account"],
        "last_review_date": "2024-03-01",
        "sample_query": "We want to establish an irrevocable family trust account and verify fiduciary documentation.",
        "recent_transactions": [
            {"amount": 19500.00, "description": "Senior Partner Bi-Weekly Compensation", "ts": "2024-03-22"},
            {"amount": -5500.00, "description": "Mortgage Payment - Luxury Estate", "ts": "2024-03-15"},
            {"amount": -7500.00, "description": "Morgan Stanley Portfolio Deposit", "ts": "2024-03-08"},
            {"amount": -850.00, "description": "Country Club Membership Dues", "ts": "2024-03-02"}
        ]
    },
    {
        "customer_id": "20111",
        "income": 62000.0,
        "credit_score": 695,
        "account_type": "standard",
        "customer_since": "2020-05-18",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "auto_loan", "credit_card"],
        "last_review_date": "2024-01-14",
        "sample_query": "What is the remaining balance and payoff quotation on my vehicle financing agreement?",
        "recent_transactions": [
            {"amount": 3900.00, "description": "Public School District Payroll", "ts": "2024-03-22"},
            {"amount": -1350.00, "description": "Apartment Lease Payment", "ts": "2024-03-15"},
            {"amount": -410.00, "description": "Auto Financing Monthly Auto-Debit", "ts": "2024-03-09"},
            {"amount": -140.00, "description": "Kroger Grocery Store", "ts": "2024-03-04"}
        ]
    },
    {
        "customer_id": "20112",
        "income": 720000.0,
        "credit_score": 775,
        "account_type": "commercial",
        "customer_since": "2018-03-29",
        "risk_tier": "low",
        "banking_products": ["checking", "commercial_line", "treasury_management"],
        "last_review_date": "2024-03-19",
        "sample_query": "We need to set up automated Fedwire sweeps and dual-custody authorization rules for payroll.",
        "recent_transactions": [
            {"amount": 65000.00, "description": "B2B Enterprise Contract Payout", "ts": "2024-03-25"},
            {"amount": -48000.00, "description": "Employee Bi-Weekly Payroll ACH", "ts": "2024-03-22"},
            {"amount": -12000.00, "description": "Corporate Office Commercial Rent", "ts": "2024-03-15"},
            {"amount": -4500.00, "description": "Microsoft Azure Enterprise Licensing", "ts": "2024-03-10"}
        ]
    },
    {
        "customer_id": "20113",
        "income": 22000.0,
        "credit_score": 595,
        "account_type": "student",
        "customer_since": "2023-09-08",
        "risk_tier": "medium",
        "banking_products": ["checking", "student_credit_card"],
        "last_review_date": "2024-02-18",
        "sample_query": "What are the student fee waivers and credit-builder card guidelines for undergraduates?",
        "recent_transactions": [
            {"amount": 1400.00, "description": "University Student Work-Study Stipend", "ts": "2024-03-20"},
            {"amount": -650.00, "description": "Campus Housing Residence Rent", "ts": "2024-03-14"},
            {"amount": -110.00, "description": "University Bookstore Textbooks", "ts": "2024-03-07"},
            {"amount": -45.00, "description": "Campus Dining Services", "ts": "2024-03-02"}
        ]
    },
    {
        "customer_id": "20114",
        "income": 128000.0,
        "credit_score": 750,
        "account_type": "premium",
        "customer_since": "2017-11-20",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "mortgage", "credit_card"],
        "last_review_date": "2024-01-25",
        "sample_query": "I would like to open a certificate of deposit ladder and understand early redemption terms.",
        "recent_transactions": [
            {"amount": 7900.00, "description": "Engineering Firm Direct Deposit", "ts": "2024-03-22"},
            {"amount": -2100.00, "description": "Primary Home Mortgage Payment", "ts": "2024-03-15"},
            {"amount": -1200.00, "description": "CD Ladder Initial Funding", "ts": "2024-03-10"},
            {"amount": -210.00, "description": "REI Outdoor Equipment", "ts": "2024-03-04"}
        ]
    },
    {
        "customer_id": "20115",
        "income": 49000.0,
        "credit_score": 635,
        "account_type": "standard",
        "customer_since": "2022-06-30",
        "risk_tier": "high",
        "banking_products": ["checking", "credit_card"],
        "last_review_date": "2024-03-05",
        "sample_query": "My checking account went negative due to recurring subscriptions. Can overdraft fees be waived?",
        "recent_transactions": [
            {"amount": 3100.00, "description": "Distribution Center Payroll", "ts": "2024-03-21"},
            {"amount": -1100.00, "description": "Rental Property Payment", "ts": "2024-03-15"},
            {"amount": -35.00, "description": "Overdraft Item Fee", "ts": "2024-03-10"},
            {"amount": -35.00, "description": "Overdraft Item Fee", "ts": "2024-03-08"}
        ]
    },
    {
        "customer_id": "20116",
        "income": 165000.0,
        "credit_score": 795,
        "account_type": "premium_plus",
        "customer_since": "2016-04-14",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "investment", "credit_card"],
        "last_review_date": "2024-02-20",
        "sample_query": "I am planning an international real estate purchase and need to verify cross-border wire documentation.",
        "recent_transactions": [
            {"amount": 10200.00, "description": "Bi-Weekly Corporate Director Salary", "ts": "2024-03-22"},
            {"amount": -2700.00, "description": "Mortgage Payment", "ts": "2024-03-15"},
            {"amount": -2500.00, "description": "International Wire - Property Deposit", "ts": "2024-03-10"},
            {"amount": -380.00, "description": "Delta Air Lines Flight Ticket", "ts": "2024-03-05"}
        ]
    },
    {
        "customer_id": "20117",
        "income": 88000.0,
        "credit_score": 725,
        "account_type": "standard",
        "customer_since": "2019-08-11",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "mortgage", "credit_card"],
        "last_review_date": "2024-01-09",
        "sample_query": "How will an extra $500 monthly principal contribution affect the amortization schedule of my mortgage?",
        "recent_transactions": [
            {"amount": 5400.00, "description": "Marketing Director Direct Deposit", "ts": "2024-03-21"},
            {"amount": -1750.00, "description": "Mortgage Amortization Payment", "ts": "2024-03-15"},
            {"amount": -500.00, "description": "Mortgage Principal Extra Payment", "ts": "2024-03-15"},
            {"amount": -175.00, "description": "Amazon Online Marketplace", "ts": "2024-03-06"}
        ]
    },
    {
        "customer_id": "20118",
        "income": 380000.0,
        "credit_score": 820,
        "account_type": "private_wealth",
        "customer_since": "2013-05-22",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "investment", "credit_card", "line_of_credit"],
        "last_review_date": "2024-02-12",
        "sample_query": "I would like to structure an asset-backed securities credit facility for commercial real estate.",
        "recent_transactions": [
            {"amount": 24000.00, "description": "Bi-Weekly Executive Equity Payout", "ts": "2024-03-25"},
            {"amount": -6200.00, "description": "Primary Residence Mortgage", "ts": "2024-03-18"},
            {"amount": -10000.00, "description": "Vanguard Taxable Wealth Transfer", "ts": "2024-03-12"},
            {"amount": -1200.00, "description": "Private Concierge Aviation", "ts": "2024-03-05"}
        ]
    },
    {
        "customer_id": "20119",
        "income": 36000.0,
        "credit_score": 610,
        "account_type": "basic",
        "customer_since": "2022-12-01",
        "risk_tier": "medium",
        "banking_products": ["checking", "credit_card"],
        "last_review_date": "2024-03-02",
        "sample_query": "Can I qualify for an emergency hardship payment deferral program for my personal credit card?",
        "recent_transactions": [
            {"amount": 2500.00, "description": "Hospitality Staff Payroll Direct Deposit", "ts": "2024-03-20"},
            {"amount": -950.00, "description": "Residential Lease Rental", "ts": "2024-03-14"},
            {"amount": -280.00, "description": "Personal Credit Card Payment", "ts": "2024-03-08"},
            {"amount": -115.00, "description": "Walmart Supercenter", "ts": "2024-03-03"}
        ]
    },
    {
        "customer_id": "20120",
        "income": 142000.0,
        "credit_score": 760,
        "account_type": "premium",
        "customer_since": "2018-01-19",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "mortgage", "credit_card", "auto_loan"],
        "last_review_date": "2024-01-17",
        "sample_query": "What are the requirements for applying for an investment property loan with 25% down payment?",
        "recent_transactions": [
            {"amount": 8800.00, "description": "Senior Pharmacist Payroll Deposit", "ts": "2024-03-22"},
            {"amount": -2400.00, "description": "Residential Mortgage Payment", "ts": "2024-03-16"},
            {"amount": -1500.00, "description": "Escrow Downpayment Reserve", "ts": "2024-03-10"},
            {"amount": -320.00, "description": "Nordstrom Fashion Retail", "ts": "2024-03-04"}
        ]
    },
    {
        "customer_id": "20121",
        "income": 450000.0,
        "credit_score": 785,
        "account_type": "commercial",
        "customer_since": "2019-04-03",
        "risk_tier": "low",
        "banking_products": ["checking", "commercial_line", "merchant_services"],
        "last_review_date": "2024-03-10",
        "sample_query": "We want to review merchant interchange processing fees and point-of-sale volume discounts.",
        "recent_transactions": [
            {"amount": 38000.00, "description": "Square POS Daily Merchant Payout", "ts": "2024-03-24"},
            {"amount": -22000.00, "description": "Supplier Food & Beverage Inventory", "ts": "2024-03-20"},
            {"amount": -9500.00, "description": "Staff Weekly Payroll Outflow", "ts": "2024-03-15"},
            {"amount": -2100.00, "description": "Commercial Kitchen Maintenance", "ts": "2024-03-08"}
        ]
    },
    {
        "customer_id": "20122",
        "income": 54000.0,
        "credit_score": 670,
        "account_type": "standard",
        "customer_since": "2021-07-29",
        "risk_tier": "medium",
        "banking_products": ["checking", "savings", "credit_card"],
        "last_review_date": "2024-02-22",
        "sample_query": "I am interested in taking out a $12,000 personal loan for home improvements. What is my APR?",
        "recent_transactions": [
            {"amount": 3300.00, "description": "Paramedic Services Payroll", "ts": "2024-03-21"},
            {"amount": -1180.00, "description": "Apartment Rental Draft", "ts": "2024-03-15"},
            {"amount": -320.00, "description": "Car Insurance Premium", "ts": "2024-03-09"},
            {"amount": -95.00, "description": "Lowe's Home Improvement", "ts": "2024-03-03"}
        ]
    },
    {
        "customer_id": "20123",
        "income": 195000.0,
        "credit_score": 810,
        "account_type": "premium_plus",
        "customer_since": "2015-10-10",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "investment", "credit_card"],
        "last_review_date": "2024-01-29",
        "sample_query": "How do backdoor Roth IRA conversions work and can VectraBank handle the tax reporting?",
        "recent_transactions": [
            {"amount": 12100.00, "description": "Consulting Principal Compensation", "ts": "2024-03-22"},
            {"amount": -3200.00, "description": "Fixed Mortgage Draft", "ts": "2024-03-16"},
            {"amount": -6500.00, "description": "Traditional to Roth IRA Conversion Transfer", "ts": "2024-03-10"},
            {"amount": -280.00, "description": "Tesla Supercharger Network", "ts": "2024-03-05"}
        ]
    },
    {
        "customer_id": "20124",
        "income": 19000.0,
        "credit_score": 570,
        "account_type": "basic",
        "customer_since": "2023-11-15",
        "risk_tier": "high",
        "banking_products": ["checking"],
        "last_review_date": "2024-03-08",
        "sample_query": "My card was lost or stolen during travel. Can we lock the account and issue an emergency card?",
        "recent_transactions": [
            {"amount": 1600.00, "description": "Gig Economy Courier Payout", "ts": "2024-03-20"},
            {"amount": -550.00, "description": "Shared Rent Payment", "ts": "2024-03-14"},
            {"amount": -45.00, "description": "Late Fee Assessment", "ts": "2024-03-08"},
            {"amount": -120.00, "description": "Suspicious Gas Station Terminal", "ts": "2024-03-02"}
        ]
    },
    {
        "customer_id": "20125",
        "income": 105000.0,
        "credit_score": 735,
        "account_type": "premium",
        "customer_since": "2020-03-17",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "auto_loan", "credit_card"],
        "last_review_date": "2024-02-16",
        "sample_query": "What are the rules and tax advantages for contributing to a Health Savings Account (HSA)?",
        "recent_transactions": [
            {"amount": 6500.00, "description": "Bi-Weekly Corporate HR Salary", "ts": "2024-03-21"},
            {"amount": -1700.00, "description": "Townhome Lease Payment", "ts": "2024-03-15"},
            {"amount": -415.00, "description": "HSA Pre-Tax Contribution", "ts": "2024-03-10"},
            {"amount": -165.00, "description": "CVS Pharmacy Prescription", "ts": "2024-03-04"}
        ]
    },
    {
        "customer_id": "20126",
        "income": 610000.0,
        "credit_score": 825,
        "account_type": "private_wealth",
        "customer_since": "2012-08-04",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "investment", "credit_card", "line_of_credit", "trust_account"],
        "last_review_date": "2024-02-25",
        "sample_query": "We want to review portfolio stress-testing models under various interest rate cut scenarios.",
        "recent_transactions": [
            {"amount": 38000.00, "description": "Bi-Weekly Managing Director Draw", "ts": "2024-03-25"},
            {"amount": -8500.00, "description": "Executive Property Mortgage", "ts": "2024-03-18"},
            {"amount": -15000.00, "description": "Alternative Assets Venture Allocation", "ts": "2024-03-12"},
            {"amount": -950.00, "description": "Equinox Luxury Health Club", "ts": "2024-03-06"}
        ]
    },
    {
        "customer_id": "20127",
        "income": 48000.0,
        "credit_score": 655,
        "account_type": "standard",
        "customer_since": "2021-10-12",
        "risk_tier": "medium",
        "banking_products": ["checking", "savings", "credit_card"],
        "last_review_date": "2024-01-20",
        "sample_query": "I received an unverified text requesting my online banking one-time passcode. Was my account compromised?",
        "recent_transactions": [
            {"amount": 3100.00, "description": "Manufacturing Tech Payroll Deposit", "ts": "2024-03-21"},
            {"amount": -1080.00, "description": "Rent Payment - Electronic Transfer", "ts": "2024-03-15"},
            {"amount": -220.00, "description": "Credit Card Minimum", "ts": "2024-03-08"},
            {"amount": -14.99, "description": "Streaming Media Subscription", "ts": "2024-03-03"}
        ]
    },
    {
        "customer_id": "20128",
        "income": 155000.0,
        "credit_score": 770,
        "account_type": "premium_plus",
        "customer_since": "2017-02-28",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "mortgage", "credit_card"],
        "last_review_date": "2024-02-08",
        "sample_query": "Can I remove private mortgage insurance (PMI) now that my home loan-to-value is under 78%?",
        "recent_transactions": [
            {"amount": 9600.00, "description": "Bi-Weekly Civil Engineer Salary", "ts": "2024-03-22"},
            {"amount": -2600.00, "description": "Mortgage Draft with PMI Escrow", "ts": "2024-03-16"},
            {"amount": -1000.00, "description": "High-Yield Reserve Deposit", "ts": "2024-03-10"},
            {"amount": -220.00, "description": "Best Buy Electronics", "ts": "2024-03-04"}
        ]
    },
    {
        "customer_id": "20129",
        "income": 82000.0,
        "credit_score": 705,
        "account_type": "standard",
        "customer_since": "2020-08-23",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "auto_loan", "credit_card"],
        "last_review_date": "2024-01-12",
        "sample_query": "What are current auto loan terms for purchasing an electric vehicle with federal tax incentives?",
        "recent_transactions": [
            {"amount": 5100.00, "description": "Bi-Weekly Registered Nurse Payroll", "ts": "2024-03-21"},
            {"amount": -1550.00, "description": "Condo Mortgage Payment", "ts": "2024-03-15"},
            {"amount": -430.00, "description": "EV Auto Loan Monthly Installment", "ts": "2024-03-09"},
            {"amount": -190.00, "description": "Sprouts Farmers Market", "ts": "2024-03-03"}
        ]
    },
    {
        "customer_id": "20130",
        "income": 29000.0,
        "credit_score": 605,
        "account_type": "basic",
        "customer_since": "2023-04-16",
        "risk_tier": "high",
        "banking_products": ["checking"],
        "last_review_date": "2024-03-14",
        "sample_query": "How can I set up automatic low-balance alerts and debit overdraft protection with savings?",
        "recent_transactions": [
            {"amount": 2200.00, "description": "Call Center Operations Salary", "ts": "2024-03-20"},
            {"amount": -850.00, "description": "Rental Payment - ACH", "ts": "2024-03-14"},
            {"amount": -180.00, "description": "Electric & Gas Utility", "ts": "2024-03-08"},
            {"amount": -35.00, "description": "Non-Sufficient Funds Fee", "ts": "2024-03-02"}
        ]
    },
    {
        "customer_id": "20131",
        "income": 275000.0,
        "credit_score": 800,
        "account_type": "private_wealth",
        "customer_since": "2016-01-11",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "investment", "credit_card", "mortgage"],
        "last_review_date": "2024-02-19",
        "sample_query": "I would like to explore 1031 real estate exchange escrow mechanics for commercial properties.",
        "recent_transactions": [
            {"amount": 17200.00, "description": "Corporate VP Direct Compensation", "ts": "2024-03-22"},
            {"amount": -4400.00, "description": "Primary Mortgage Payment", "ts": "2024-03-16"},
            {"amount": -4000.00, "description": "1031 Qualified Intermediary Hold", "ts": "2024-03-11"},
            {"amount": -510.00, "description": "American Express Corporate Card", "ts": "2024-03-05"}
        ]
    },
    {
        "customer_id": "20132",
        "income": 68000.0,
        "credit_score": 685,
        "account_type": "standard",
        "customer_since": "2021-05-07",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "credit_card"],
        "last_review_date": "2024-01-26",
        "sample_query": "How do travel credit card reward points transfer to international airline partner alliances?",
        "recent_transactions": [
            {"amount": 4200.00, "description": "Marketing Manager Bi-Weekly Payroll", "ts": "2024-03-21"},
            {"amount": -1400.00, "description": "Apartment Rental Draft", "ts": "2024-03-15"},
            {"amount": -450.00, "description": "Premium Travel Rewards Card Payment", "ts": "2024-03-09"},
            {"amount": -130.00, "description": "Lyft Rideshare Transits", "ts": "2024-03-04"}
        ]
    },
    {
        "customer_id": "20133",
        "income": 890000.0,
        "credit_score": 835,
        "account_type": "private_wealth",
        "customer_since": "2011-09-14",
        "risk_tier": "low",
        "banking_products": ["checking", "savings", "investment", "credit_card", "jumbo_mortgage", "trust_account"],
        "last_review_date": "2024-03-22",
        "sample_query": "We require a specialized sovereign bond allocation strategy for our charitable family foundation.",
        "recent_transactions": [
            {"amount": 55000.00, "description": "Hedge Fund Managing Partner Distribution", "ts": "2024-03-25"},
            {"amount": -11500.00, "description": "Jumbo Mortgage Automatic Payout", "ts": "2024-03-18"},
            {"amount": -25000.00, "description": "Charitable Foundation Endowment Transfer", "ts": "2024-03-12"},
            {"amount": -1800.00, "description": "Sotheby's Auction Gallery", "ts": "2024-03-06"}
        ]
    }
]

def get_customer_profiles_dict():
    try:
        from main_starter import CustomerProfile
    except ImportError:
        from backend.main_starter import CustomerProfile
    profiles = {}
    for d in CUSTOMER_DATA:
        # Map account_type to valid literal if needed
        acc_type = d["account_type"]
        if acc_type not in ["basic", "standard", "premium", "premium_plus"]:
            acc_type = "premium_plus" if "wealth" in acc_type or "commercial" in acc_type else "standard"
            
        profiles[d["customer_id"]] = CustomerProfile(
            customer_id=d["customer_id"],
            income=d["income"],
            credit_score=d["credit_score"],
            account_type=acc_type,
            customer_since=d["customer_since"],
            risk_tier=d["risk_tier"] if d["risk_tier"] in ["low", "medium", "high", "critical"] else "medium",
            recent_transactions=d["recent_transactions"],
            banking_products=d["banking_products"],
            last_review_date=d["last_review_date"]
        )
    return profiles

def get_sample_queries_dict():
    return {d["customer_id"]: d["sample_query"] for d in CUSTOMER_DATA}
