from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ExtractionJob(db.Model):
    __tablename__ = "extraction_jobs"

    id = db.Column(db.String(36), primary_key=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    pattern = db.Column(db.String(255), nullable = False)
    match_count = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime(timezone=True), nullable = True)
    error = db.Column(db.Text, nullable=True)

    results = db.relationship("ExtractionResult", backref="job", lazy="dynamic")

class ExtractionResult(db.Model):
    __tablename__ = "extraction_results"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.String(36), db.ForeignKey("extraction_jobs.id"), nullable=False, index=True)
    file_path = db.Column(db.Text, nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.BigInteger, default=0)
    depth = db.Column(db.Integer, default=0)
    source_archive = db.Column(db.String(255), nullable=True)
    extracted_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
