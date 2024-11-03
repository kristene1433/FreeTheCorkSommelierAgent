from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the Flask app and OpenAI client
app = Flask(__name__)

# Allow CORS for both your Shopify domain and freethecork.com
CORS(app, resources={r"/ask": {"origins": ["https://freethecork.com", "https://www.freethecork.com", "https://8d1741-3.myshopify.com"]}})


client = OpenAI(api_key=api_key)

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.route('/ask', methods=['POST'])
def get_wine_advice():
    user_input = request.json.get("question")
    app.logger.info(f"Received query: {user_input}")  # Logs the query
    
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
        app.logger.info(f"Generated advice: {advice}")  # Logs the generated advice
        return jsonify({"advice": advice})
    
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")  # Logs any error
        return jsonify({"error": "An error occurred while processing your request. Please try again later."}), 500
    
@app.route("/")
def home():
    return "Welcome to Free the Cork Sommelier!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
