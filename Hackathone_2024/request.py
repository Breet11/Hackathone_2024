import requests as rq

#Global variables for requests
METADATA_EXTRACTOR = "localhost:8989"
CONTENT_EXTRACTOR = "localhost:8988"
CLICKBAIT_EXTRACTOR = "localhost:8987"
ENTITY_EXTRACTOR = "localhost:8986"


def extract(extractor_service_url, request_body):
	resp = rq.post(f"http://{extractor_service_url}/rest/process", json=request_body)
	if resp.status_code == 200:
		return resp.json()