# CURL API TEST

curl -X POST http://localhost:8080/extractions -F "archive=@input.zip" -F "pattern=*.txt"


curl http://localhost:8080/extractions/<job_id>


curl http://localhost:8080/extractions/<job_id>/results

curl "http://localhost:8080/extractions/<job_id>/results?page=2"

curl "http://localhost:8080/extractions/<job_id>/results?limit=2"

curl "http://localhost:8080/extractions/<job_id>/results?page=2&limit=2"

http://localhost:8080/extractions/<id>/results?page=2&limit=5

curl http://localhost:8080/health