# ARCHIVE EXTRACTOR

## Docker command to build and run app:

```bash
docker-compose up --build -d
```

## Docker command to stop and remove container:

```bash
docker-compose down
```

## CURL API TEST

**NOTE:** `input.zip` is added in repo which was used for testing the routes and app logic

```bash
curl -X POST http://localhost:8080/extractions -F "archive=@input.zip" -F "pattern=*.txt"

curl http://localhost:8080/extractions/<job_id>

curl http://localhost:8080/extractions/<job_id>/results

curl "http://localhost:8080/extractions/<job_id>/results?page=2"

curl "http://localhost:8080/extractions/<job_id>/results?limit=2"

curl "http://localhost:8080/extractions/<job_id>/results?page=2&limit=2"

curl http://localhost:8080/extractions/<id>/results?page=2&limit=5

curl http://localhost:8080/health
```


## Command to run UT:

```bash
python -m pytest -v
```

## API Documentation

### `GET /health`

Health check endpoint.

#### Response `200 OK`

```json
{
  "status": "ok"
}
```

---

### `POST /extractions`

Creates a new extraction job.

#### Request

Content-Type:

```http
multipart/form-data
```

Form fields:

| Field | Type | Required | Description |
|---|---|---|---|
| archive | file | Yes | Archive file to extract |
| pattern | string | Yes | Pattern to match files |

#### Example Request

```http
POST /extractions
Content-Type: multipart/form-data
```

```text
archive: file.zip
pattern: *.txt
```

#### Response `202 Accepted`

```json
{
  "job_id": "uuid-job-id"
}
```

#### Error Responses

##### `400 Bad Request`

```json
{
  "error": "Missing 'archive' file"
}
```

```json
{
  "error": "No file selected"
}
```

```json
{
  "error": "Missing 'Pattern' field"
}
```

##### `500 Internal Server Error`

```json
{
  "error": "Extraction Job Failed, please retry"
}
```

---

### `GET /extractions/{job_id}`

Gets extraction job status.

#### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| job_id | string | Yes | Extraction job ID |

#### Response `200 OK`

```json
{
  "job_id": "uuid-job-id",
  "status": "pending",
  "pattern": "*.txt",
  "match_count": 5,
  "submitted_at": "2026-06-18T10:30:00",
  "completed_at": null,
  "error": null
}
```

#### Error Response `404 Not Found`

```json
{
  "error": "Job not found"
}
```

---

### `GET /extractions/{job_id}/results`

Gets paginated extraction results.

#### Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| job_id | string | Yes | Extraction job ID |

#### Query Parameters

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| page | integer | No | 1 | Page number |
| limit | integer | No | 10 | Results per page |

#### Example

```http
GET /extractions/uuid-job-id/results?page=1&limit=10
```

#### Response `200 OK`

```json
{
  "job_id": "uuid-job-id",
  "page": 1,
  "limit": 10,
  "total": 25,
  "pages": 3,
  "results": [
    {
      "file_path": "folder/file.txt",
      "file_name": "file.txt",
      "file_size": 1234,
      "depth": 1,
      "source_archive": "archive.zip",
      "extracted_at": "2026-06-18T10:35:00"
    }
  ]
}
```

#### Error Response `404 Not Found`

```json
{
  "error": "Job not found"
}
```

## Design Choices and Assumptions

### Archive Upload Method: `multipart/form-data` vs. URL/Path Reference

This application uses `multipart/form-data` to receive archive files directly from the client. This approach assumes that the uploaded archive files are reasonably sized and available locally on the user’s machine.

This choice was made because it keeps the implementation simple, avoids additional dependencies such as external storage or file-fetching services, and provides a straightforward upload flow for users.

### Use of `ThreadPoolExecutor`

The application uses `ThreadPoolExecutor` to run extraction jobs asynchronously in the background.

This decision is based on the assumption that most operations in this service are I/O-bound, including archive extraction, reading file metadata, matching file names against patterns, and writing matching results to the database. For this type of workload, using threads is a practical and efficient choice.

## Assumptions

- Data models remain unchanged, eliminating the need for database migrations.

## Future Roadmaps

- Transition to Gunicorn as the WSGI server.