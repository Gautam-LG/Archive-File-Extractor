from datetime import datetime, timezone
from .extraction import process_archive

def _update_job_status(app, job_id, status, completed=False, **Kwargs):
    from .models import db, ExtractionJob
    with app.app_context():
        try:
            job = ExtractionJob.query.get(job_id)
            if not job:
                print(f"Job (Job_ID: {job_id} not found)")
                return
            
            job.status = status
            
            if completed:
                job.completed_at = datetime.now(timezone.utc)

            for key, value in Kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)

            db.session.commit()
        except Exception:
            db.session.rollback()
            print(f"Failed to update JOB status (JOB_ID = {job_id})")
            raise


def run_job(app, job_id, archive_path, pattern, source_archive):
    _update_job_status(app, job_id, "running")

    try:
        total = process_archive(app, archive_path, pattern, job_id, source_archive)
        _update_job_status(app, job_id,"completed", True, match_count=total)
    
    except Exception:
        _update_job_status(app, job_id, "failed", error="Extraction Failed")
