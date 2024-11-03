import os
import logging
from flask import Flask, request, jsonify
from openai import OpenAI, error  # Import error handling for OpenAI API
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set OPENAI_API_KEY in the environment.")

# Initialize the Flask app and OpenAI client
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
client = OpenAI(api_key=api_key)

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for detailed output

@app.route('/ask', methods=['POST'])
def get_wine_advice():
    user_input = request.json.get("query")
    app.logger.debug(f"Received query: {user_input}")  # Logs the query at debug level

    if not user_input:
        app.logger.error("No input provided")
        return jsonify({"error": "No input provided"}), 400

    try:
        # Generate the response from the OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a wine expert specializing in providing wine advice and food pairing recommendations."},
                {"role": "user", "content": user_input}
            ]
        )
        advice = completion.choices[0].message.content.strip()
        app.logger.debug(f"Generated advice: {advice}")  # Logs the generated advice
        return jsonify({"advice": advice})

    except error.OpenAIError as e:
        app.logger.error(f"OpenAI API error occurred: {e}")  # Log specific OpenAI errors
        return jsonify({"error": "An error occurred with the AI service. Please try again later."}), 500

    except Exception as e:
        app.logger.error(f"Unexpected error occurred: {e}")  # Logs any other errors
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

@app.route("/")
def home():
    return "Welcome to Free the Cork Sommelier!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
