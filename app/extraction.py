import os
import zipfile
import tarfile
import tempfile
import shutil
import fnmatch
from .config import MAX_DEPTH
from app import app

ARCHIVE_EXTENTIONS = ('.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2')

def is_archive(filename):
    lower = filename.lower()
    for ext in ARCHIVE_EXTENTIONS:
        if lower.endswith(ext):
            return True
    return False

def extract_archive(archive_path, dest_folder):
    lower = archive_path.lower()
    if lower.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zf:
            zf.extractall(dest_folder)
    elif lower.endswith(('.tar.gz', '.tgz')):
        with tarfile.open(archive_path, 'r:gz') as tf:
            tf.extractall(dest_folder)
    elif lower.endswith('.tar.bz2'):
        with tarfile.open(archive_path, 'r:bz2') as tf:
            tf.extractall(dest_folder)
    elif lower.endswith('.tar'):
        with tarfile.open(archive_path, 'r:') as tf:
            tf.extractall(dest_folder)
    else:
        raise ValueError(f"Unsupported archive: {archive_path}")

def process_archive(archive_path, pattern, job_id, source_archive, parent_path="", depth=0):
    if depth > MAX_DEPTH:
        return 0

    from .models import db, ExtractionResult

    matches = 0
    temp_dir = tempfile.mkdtemp()

    try:
        extract_archive(archive_path, temp_dir)

        for root, dirs, files in os.walk(temp_dir):
            results_to_add = []
            archives_to_recurse = []

            for filename in files:
                full_disk_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_disk_path, temp_dir)

                if parent_path:
                    logical_path = f"{parent_path}/{rel_path}"
                else:
                    logical_path = f"{source_archive}/{rel_path}"

                if fnmatch.fnmatch(filename, pattern):
                    file_size = os.path.getsize(full_disk_path)
                    results_to_add.append(ExtractionResult(
                        job_id=job_id,
                        file_path=logical_path,
                        file_name=filename,
                        file_size=file_size,
                        depth=depth,
                        source_archive=source_archive
                    ))

                if is_archive(filename):
                    archives_to_recurse.append((full_disk_path, logical_path))

            with app.app_context():
                try:
                    db.session.add_all(results_to_add)
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    raise

            matches += len(results_to_add)

            for nested_archive_path, nested_logical_path in archives_to_recurse:
                matches += process_archive(
                    nested_archive_path, pattern, job_id,
                    source_archive, nested_logical_path, depth + 1
                )
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return matches