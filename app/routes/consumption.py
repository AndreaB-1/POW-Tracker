from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import Consumption, GrowattConfig, SystemSettings
from datetime import date, timedelta
from sqlalchemy import func
import json

consumption_bp = Blueprint('consumption', __name__)


@consumption_bp.route('/')
def index():
    entries = Consumption.query.order_by(Consumption.date.desc()).limit(30).all()

    # Chart data: last 30 days
    thirty_days_ago = date.today() - timedelta(days=29)
    chart_entries = (
        Consumption.query
        .filter(Consumption.date >= thirty_days_ago)
        .order_by(Consumption.date.asc())
        .all()
    )
    chart_labels = [e.date.strftime('%b %d') for e in chart_entries]
    production_data = [e.production_kwh for e in chart_entries]
    consumption_data = [e.consumption_kwh for e in chart_entries]
    export_data = [e.grid_export_kwh for e in chart_entries]

    # Totals
    totals = db.session.query(
        func.sum(Consumption.production_kwh),
        func.sum(Consumption.consumption_kwh),
        func.sum(Consumption.grid_export_kwh),
        func.sum(Consumption.grid_import_kwh),
    ).first()
    total_production = round(totals[0] or 0, 2)
    total_consumption = round(totals[1] or 0, 2)
    total_export = round(totals[2] or 0, 2)
    total_import = round(totals[3] or 0, 2)

    settings = SystemSettings.query.first()
    currency = settings.currency if settings else 'USD'
    electricity_rate = settings.electricity_rate if settings else 0.25

    growatt_cfg = GrowattConfig.query.first()

    return render_template(
        'consumption/index.html',
        entries=entries,
        chart_labels=json.dumps(chart_labels),
        production_data=json.dumps(production_data),
        consumption_data=json.dumps(consumption_data),
        export_data=json.dumps(export_data),
        total_production=total_production,
        total_consumption=total_consumption,
        total_export=total_export,
        total_import=total_import,
        today=date.today().isoformat(),
        currency=currency,
        electricity_rate=electricity_rate,
        growatt_cfg=growatt_cfg,
    )


@consumption_bp.route('/add', methods=['POST'])
def add():
    try:
        entry_date = date.fromisoformat(request.form['date'])
        existing = Consumption.query.filter_by(date=entry_date).first()
        if existing:
            existing.production_kwh = float(request.form.get('production_kwh', 0))
            existing.consumption_kwh = float(request.form.get('consumption_kwh', 0))
            existing.grid_export_kwh = float(request.form.get('grid_export_kwh', 0))
            existing.grid_import_kwh = float(request.form.get('grid_import_kwh', 0))
            existing.source = 'manual'
        else:
            entry = Consumption(
                date=entry_date,
                production_kwh=float(request.form.get('production_kwh', 0)),
                consumption_kwh=float(request.form.get('consumption_kwh', 0)),
                grid_export_kwh=float(request.form.get('grid_export_kwh', 0)),
                grid_import_kwh=float(request.form.get('grid_import_kwh', 0)),
                source='manual',
            )
            db.session.add(entry)
        db.session.commit()
        flash('Consumption data saved.', 'success')
    except (ValueError, KeyError) as e:
        flash(f'Error saving consumption: {e}', 'danger')
    return redirect(url_for('consumption.index'))


@consumption_bp.route('/delete/<int:entry_id>', methods=['POST'])
def delete(entry_id):
    entry = Consumption.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('Entry deleted.', 'success')
    return redirect(url_for('consumption.index'))


# ---------------------------------------------------------------------------
# Growatt integration stub
# ---------------------------------------------------------------------------

@consumption_bp.route('/growatt/save', methods=['POST'])
def growatt_save():
    cfg = GrowattConfig.query.first()
    if not cfg:
        cfg = GrowattConfig()
        db.session.add(cfg)

    cfg.username = request.form.get('username', '')
    cfg.plant_id = request.form.get('plant_id', '')
    cfg.enabled = 'enabled' in request.form

    password = request.form.get('password', '')
    if password:
        # TODO: Replace with proper encryption (e.g. Fernet) before production use
        cfg.password_hash = password

    db.session.commit()
    flash('Growatt configuration saved.', 'success')
    return redirect(url_for('consumption.index'))


@consumption_bp.route('/growatt/sync', methods=['POST'])
def growatt_sync():
    """
    Placeholder for Growatt inverter sync.

    To implement real sync, install the `growattServer` Python package
    (https://github.com/indykoning/PyPi_GrowattServer) and replace the
    stub below with actual API calls.

    Example (not active):
        import growattServer
        api = growattServer.GrowattServer()
        login_response = api.login(username, password)
        plant_list = api.plant_list(login_response['user']['id'])
        plant_id = plant_list['data'][0]['plantId']
        plant_detail = api.plant_detail(plant_id, 1, date.today().isoformat())
    """
    cfg = GrowattConfig.query.first()
    if not cfg or not cfg.enabled:
        return jsonify({'status': 'error', 'message': 'Growatt integration is not enabled.'}), 400

    # Stub response — replace with real API call
    return jsonify({
        'status': 'placeholder',
        'message': (
            'Growatt sync is not yet implemented. '
            'Configure the growattServer library with your credentials to enable live sync.'
        ),
    }), 200
