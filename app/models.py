from datetime import datetime, date
from app import db


EXPENSE_CATEGORIES = [
    'Solar Panels',
    'Inverter',
    'Battery Storage',
    'Installation Labor',
    'Electrical Work',
    'Mounting Hardware',
    'Monitoring Equipment',
    'Permits & Inspections',
    'Grid Connection',
    'Maintenance & Repairs',
    'Insurance',
    'Other',
]


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'category': self.category,
            'description': self.description,
            'amount': self.amount,
            'notes': self.notes,
        }


class Consumption(db.Model):
    __tablename__ = 'consumption'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    production_kwh = db.Column(db.Float, default=0.0)
    consumption_kwh = db.Column(db.Float, default=0.0)
    grid_export_kwh = db.Column(db.Float, default=0.0)
    grid_import_kwh = db.Column(db.Float, default=0.0)
    # manual | growatt
    source = db.Column(db.String(20), default='manual')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def self_consumption_pct(self):
        if self.production_kwh and self.production_kwh > 0:
            used_from_solar = self.production_kwh - self.grid_export_kwh
            return round((used_from_solar / self.production_kwh) * 100, 1)
        return 0.0


class GrowattConfig(db.Model):
    __tablename__ = 'growatt_config'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), default='')
    # NOTE: In production, encrypt this field
    password_hash = db.Column(db.String(200), default='')
    plant_id = db.Column(db.String(100), default='')
    enabled = db.Column(db.Boolean, default=False)
    last_sync = db.Column(db.DateTime, nullable=True)
    sync_status = db.Column(db.String(50), default='never_synced')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SystemSettings(db.Model):
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True)
    system_size_kw = db.Column(db.Float, default=0.0)
    installation_date = db.Column(db.Date, nullable=True)
    panel_count = db.Column(db.Integer, default=0)
    inverter_brand = db.Column(db.String(100), default='')
    expected_annual_production_kwh = db.Column(db.Float, default=0.0)
    electricity_rate = db.Column(db.Float, default=0.25)
    currency = db.Column(db.String(10), default='USD')
    notes = db.Column(db.Text, default='')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
