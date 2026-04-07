from flask import Blueprint, render_template, jsonify
from sqlalchemy import func, extract
from app import db
from app.models import Expense, Consumption, SystemSettings
from datetime import date, datetime, timedelta
import json

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    settings = SystemSettings.query.first()

    total_investment = db.session.query(func.sum(Expense.amount)).scalar() or 0.0

    expense_count = Expense.query.count()

    by_category = (
        db.session.query(Expense.category, func.sum(Expense.amount))
        .group_by(Expense.category)
        .all()
    )
    category_data = {cat: round(amt, 2) for cat, amt in by_category}

    # Monthly expenses for last 12 months
    twelve_months_ago = date.today() - timedelta(days=365)
    monthly_expenses = (
        db.session.query(
            extract('year', Expense.date).label('year'),
            extract('month', Expense.date).label('month'),
            func.sum(Expense.amount).label('total'),
        )
        .filter(Expense.date >= twelve_months_ago)
        .group_by('year', 'month')
        .order_by('year', 'month')
        .all()
    )
    monthly_labels = []
    monthly_values = []
    for row in monthly_expenses:
        label = datetime(int(row.year), int(row.month), 1).strftime('%b %Y')
        monthly_labels.append(label)
        monthly_values.append(round(row.total, 2))

    # Payback period estimate
    payback_years = None
    if settings and settings.expected_annual_production_kwh and settings.electricity_rate and total_investment > 0:
        annual_savings = settings.expected_annual_production_kwh * settings.electricity_rate
        if annual_savings > 0:
            payback_years = round(total_investment / annual_savings, 1)

    # Years since installation
    years_installed = None
    if settings and settings.installation_date:
        delta = date.today() - settings.installation_date
        years_installed = round(delta.days / 365.25, 1)

    # Estimated savings so far
    estimated_savings = None
    if payback_years and years_installed and settings:
        annual_savings = settings.expected_annual_production_kwh * settings.electricity_rate
        estimated_savings = round(years_installed * annual_savings, 2)

    recent_expenses = Expense.query.order_by(Expense.date.desc()).limit(5).all()

    currency = settings.currency if settings else 'USD'

    return render_template(
        'dashboard.html',
        settings=settings,
        total_investment=round(total_investment, 2),
        expense_count=expense_count,
        category_data=json.dumps(category_data),
        monthly_labels=json.dumps(monthly_labels),
        monthly_values=json.dumps(monthly_values),
        payback_years=payback_years,
        years_installed=years_installed,
        estimated_savings=estimated_savings,
        recent_expenses=recent_expenses,
        currency=currency,
    )
