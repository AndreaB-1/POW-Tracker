from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import SystemSettings
from datetime import date

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/', methods=['GET', 'POST'])
def index():
    settings = SystemSettings.query.first()

    if request.method == 'POST':
        settings.system_size_kw = float(request.form.get('system_size_kw') or 0)
        settings.panel_count = int(request.form.get('panel_count') or 0)
        settings.inverter_brand = request.form.get('inverter_brand', '')
        settings.expected_annual_production_kwh = float(
            request.form.get('expected_annual_production_kwh') or 0
        )
        settings.electricity_rate = float(request.form.get('electricity_rate') or 0.25)
        settings.currency = request.form.get('currency', 'USD')
        settings.notes = request.form.get('notes', '')

        install_date_str = request.form.get('installation_date', '')
        if install_date_str:
            settings.installation_date = date.fromisoformat(install_date_str)
        else:
            settings.installation_date = None

        db.session.commit()
        flash('Settings saved successfully.', 'success')
        return redirect(url_for('settings.index'))

    currencies = ['USD', 'EUR', 'GBP', 'AUD', 'CAD', 'CHF', 'JPY', 'BRL', 'ZAR', 'INR']
    return render_template('settings/index.html', settings=settings, currencies=currencies)
