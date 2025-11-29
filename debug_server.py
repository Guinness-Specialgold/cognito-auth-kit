from main import flask_app

if __name__ == "__main__":
    try:
        print("Starting Flask app...")
        flask_app.run(debug=False, host="0.0.0.0", port=5000)
    except Exception as e:
        print(f"Error running app: {e}")
