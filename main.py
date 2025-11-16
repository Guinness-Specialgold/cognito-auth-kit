from app import create_app  # or from app import app
import awsgi

# Lambda will reuse this instance between invocations
flask_app = create_app()

def lambda_handler(event, context):
    """
    AWS Lambda entrypoint.
    API Gateway or Lambda Function URL will send events here.
    """
    return awsgi.response(flask_app, event, context)

# Optional: local dev
if __name__ == "__main__":
    # For local running: `python main.py`
    flask_app.run(debug=True, host="0.0.0.0", port=5000)
