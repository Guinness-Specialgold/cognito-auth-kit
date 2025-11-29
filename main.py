from dotenv import load_dotenv
load_dotenv()

from app import create_app
import serverless_wsgi

flask_app = create_app()

def lambda_handler(event, context):
    # Normalize Lambda Function URL / HTTP API v2 events into REST-style shape for serverless-wsgi
    # This handles the "version": "2.0" format used by Function URLs.
    if event.get("version") == "2.0" and "httpMethod" not in event:
        rc = event.get("requestContext") or {}
        http = rc.get("http") or {}
        headers = event.get("headers") or {}
        
        # Function URLs don't automatically handle OPTIONS preflight if configured without CORS,
        # so we ensure the event looks like a standard REST API event that Flask can route.
        
        event = {
            "httpMethod": http.get("method", "GET"),
            "path": event.get("rawPath") or http.get("path") or "/",
            "headers": headers,
            "queryStringParameters": event.get("queryStringParameters") or {},
            "body": event.get("body"),
            "isBase64Encoded": event.get("isBase64Encoded", False),
            "requestContext": {
                "identity": {"sourceIp": http.get("sourceIp", "")},
                "stage": rc.get("stage", "$default"),
                # Pass other context if needed
                "accountId": rc.get("accountId"),
                "requestId": rc.get("requestId"),
            },
        }

    return serverless_wsgi.handle_request(flask_app, event, context)


# Optional: local dev
if __name__ == "__main__":
    # For local running: `python main.py`
    flask_app.run(debug=True, host="0.0.0.0", port=5000)
