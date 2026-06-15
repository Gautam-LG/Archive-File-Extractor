import os
import uuid
import tempfile
import shutil
from flask import Flask, request, jsonify
from .worker import run_job
from .models import db, ExtractionJob, ExtractionResult
from app import app, executor


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


@app.route("/extractions", methods=["POST"])
def create_extraction():
    if "archive" not in request.files:
        return jsonify({"error":"Missing 'archvive' file"}), 400
    
    file = request.files["archive"]
    if file.filename == "":
        return jsonify({"error":"No file selected"}), 400
    
    pattern = request.form.get("pattern")
    if not pattern:
        return jsonify({"error":"Missing 'Pattern' field"}), 400
    
    temp_dir = tempfile.mkdtemp()
    archive_path = os.path.join(temp_dir, file.filename)
    file.save(archive_path)

    job_id = str(uuid.uuid4())
    job = ExtractionJob(id=job_id, pattern=pattern)
    db.session.add(job)

    try: 
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        shutil.rmtree(temp_dir, ignore_errors=True)
        return jsonify({"error":"Extraction Job Failed, please retry"}), 500

    executor.submit(_run_extraction_job, temp_dir, job_id, archive_path, pattern, file.filename)

    return jsonify({"JOB_ID":job_id}), 202

def _run_extraction_job(temp_dir, job_id, archive_path, pattern, source_archive):
    try:
        run_job(job_id, archive_path, pattern, source_archive)
    except Exception as e:
        print(f"Job with job ID: {job_id}, has failed, error: {str(e)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.route("/extractions/<job_id>", methods=["GET"])
def get_extraction_status(job_id):
    job = ExtractionJob.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify({
        "job_id": job.id,
        "status": job.status,
        "pattern": job.pattern,
        "match_count": job.match_count,
        "submitted_at": job.submitted_at.isoformat() if job.submitted_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error": job.error
    })


@app.route("/extractions/<job_id>/results", methods=["GET"])
def get_extraction_results(job_id):
    job = ExtractionJob.query.get(job_id)
    if not job:
        return jsonify({"error":"Job not found"}), 404
    
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    pagination = ExtractionResult.query.filter_by(job_id=job_id)\
        .order_by(ExtractionResult.id)\
        .paginate(page=page, per_page=limit, error_out=False)

    return jsonify({
        "job_id": job_id,
        "page": page,
        "limit": limit,
        "total": pagination.total,
        "pages": pagination.pages,
        "results":[
            {
                "file_path": i.file_path,
                "file_name": i.file_name,
                "file_size": i.file_size,
                "depth": i.depth,
                "source_archive": i.source_archive,
                "extracted_at": i.extracted_at.isoformat() if i.extracted_at else None
            }
            for i in pagination.items
        ]
    })

    