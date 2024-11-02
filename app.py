import os
import logging
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from flask_cors import CORS  # Import CORS

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the Flask app and OpenAI client
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
client = OpenAI(api_key=api_key)

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.route('/get_wine_advice', methods=['POST'])
def get_wine_advice():
    try:
        # Retrieve the user query
        user_input = request.json.get("query")
        app.logger.info("Received request at /get_wine_advice")

        # Check if query was provided
        if not user_input:
            app.logger.warning("No input provided in request")
            return jsonify({"error": "No input provided"}), 400

        # Log the user query
        app.logger.info(f"User query: {user_input}")

        # Attempt to get response from OpenAI API
        try:
            app.logger.info("Sending request to OpenAI API")
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a wine expert specializing in providing wine advice and food pairing recommendations."},
                    {"role": "user", "content": user_input}
                ]
            )
            app.logger.info("Received response from OpenAI API")

            # Extract advice from response
            if 'choices' in completion and len(completion.choices) > 0:
                advice = completion.choices[0].message.content.strip()
                app.logger.info(f"Generated advice: {advice}")
                return jsonify({"advice": advice})
            else:
                app.logger.error("No choices found in OpenAI API response")
                return jsonify({"error": "Unexpected response format from OpenAI API"}), 500

        except Exception as api_error:
            app.logger.error(f"Error while calling OpenAI API: {api_error}")
            return jsonify({"error": "Failed to retrieve advice from the AI service. Please try again later."}), 500

    except Exception as general_error:
        app.logger.error(f"Unexpected error in /get_wine_advice endpoint: {general_error}")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

@app.route("/")
def home():
    return "Welcome to Free the Cork Sommelier!"

# Health check endpoint to verify the server is running
@app.route("/check", methods=["GET"])
def check():
    return jsonify({"status": "Server is running"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
