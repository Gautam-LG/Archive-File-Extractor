from app.extraction import is_archive, extract_archive, process_archive

import zipfile

def test_is_archive_zip():
    assert is_archive("file.zip") is True

def test_is_archive_txt():
    assert is_archive("file.txt") is False

def test_extract_zip(tmp_path):
    zpath = tmp_path / "test.zip"
    with zipfile.ZipFile(zpath, "w") as zf:
        zf.writestr("hello.txt", "world")
    dest = tmp_path / "out"
    dest.mkdir()
    extract_archive(str(zpath), str(dest))
    assert (dest / "hello.txt").read_text() == "world"

def test_process_archive_flat(app,sample_zip):
    from app.models import db, ExtractionResult, ExtractionJob

    job_id = "test_flat"
    with app.app_context():
        job = ExtractionJob(id=job_id, pattern="*.json")
        db.session.add(job)
        db.session.commit()

        matches = process_archive(app, sample_zip, "*.json", job_id, "sample.zip")
        assert matches == 2

        results = ExtractionResult.query.filter_by(job_id=job_id).all()
        assert len(results) == 2
        names = {r.file_name for r in results}
        assert names == {"b.json", "c.json"}

def test_process_archive_nested(app, nested_zip):
    from app.models import db, ExtractionResult, ExtractionJob

    job_id = "test_nested"
    with app.app_context():
        db.session.add(ExtractionJob(id=job_id, pattern="*.json"))
        db.session.commit()

        matches = process_archive(app, nested_zip, "*.json", job_id, "nested.zip")
        assert matches == 2

        results = ExtractionResult.query.filter_by(job_id=job_id).all()
        depths = {r.file_name: r.depth for r in results}
        assert depths["top.json"] == 0
        assert depths["deep.json"] == 1