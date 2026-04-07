from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import Expense, SystemSettings, EXPENSE_CATEGORIES
from datetime import date

expenses_bp = Blueprint('expenses', __name__)


@expenses_bp.route('/')
def index():
    category_filter = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    query = Expense.query

    if category_filter:
        query = query.filter(Expense.category == category_filter)
    if date_from:
        query = query.filter(Expense.date >= date_from)
    if date_to:
        query = query.filter(Expense.date <= date_to)

    expenses = query.order_by(Expense.date.desc()).all()
    total = sum(e.amount for e in expenses)

    settings = SystemSettings.query.first()
    currency = settings.currency if settings else 'USD'

    return render_template(
        'expenses/index.html',
        expenses=expenses,
        total=round(total, 2),
        categories=EXPENSE_CATEGORIES,
        selected_category=category_filter,
        date_from=date_from,
        date_to=date_to,
        currency=currency,
    )


@expenses_bp.route('/add', methods=['GET', 'POST'])
def add():
    settings = SystemSettings.query.first()
    currency = settings.currency if settings else 'USD'

    if request.method == 'POST':
        try:
            expense = Expense(
                date=date.fromisoformat(request.form['date']),
                category=request.form['category'],
                description=request.form['description'],
                amount=float(request.form['amount']),
                notes=request.form.get('notes', ''),
            )
            db.session.add(expense)
            db.session.commit()
            flash('Expense added successfully.', 'success')
            return redirect(url_for('expenses.index'))
        except (ValueError, KeyError) as e:
            flash(f'Error adding expense: {e}', 'danger')

    return render_template(
        'expenses/form.html',
        expense=None,
        categories=EXPENSE_CATEGORIES,
        today=date.today().isoformat(),
        currency=currency,
    )


@expenses_bp.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    settings = SystemSettings.query.first()
    currency = settings.currency if settings else 'USD'

    if request.method == 'POST':
        try:
            expense.date = date.fromisoformat(request.form['date'])
            expense.category = request.form['category']
            expense.description = request.form['description']
            expense.amount = float(request.form['amount'])
            expense.notes = request.form.get('notes', '')
            db.session.commit()
            flash('Expense updated successfully.', 'success')
            return redirect(url_for('expenses.index'))
        except (ValueError, KeyError) as e:
            flash(f'Error updating expense: {e}', 'danger')

    return render_template(
        'expenses/form.html',
        expense=expense,
        categories=EXPENSE_CATEGORIES,
        today=date.today().isoformat(),
        currency=currency,
    )


@expenses_bp.route('/delete/<int:expense_id>', methods=['POST'])
def delete(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted.', 'success')
    return redirect(url_for('expenses.index'))


@expenses_bp.route('/api/list')
def api_list():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return jsonify([e.to_dict() for e in expenses])
