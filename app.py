import os
import logging
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the Flask app and OpenAI client
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://8d1741-3.myshopify.com", "https://www.freethecork.com", "https://freethecork.com"]}})
client = OpenAI(api_key=api_key)

# Set up logging
logging.basicConfig(level=logging.INFO)

def is_wine_related(query):
    """Classify if the query is about wine or food pairings."""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Determine if the following query is about wine or food pairings. Respond with 'Yes' or 'No'."},
            {"role": "user", "content": query}
        ]
    )
    answer = response.choices[0].message.content.strip().lower()
    return 'yes' in answer

@app.route('/ask', methods=['POST'])
def get_wine_advice():
    # Check if request JSON contains "query" key
    if not request.json or "query" not in request.json:
        app.logger.error("No input provided or 'query' missing in request.")
        return jsonify({"error": "No input provided"}), 400

    user_input = request.json.get("query")
    app.logger.info(f"Received query: {user_input}")  # Logs the query

    if not user_input:
        app.logger.error("Query is empty.")
        return jsonify({"error": "No input provided"}), 400

    try:
        if is_wine_related(user_input):
            # Generate the response from the OpenAI API
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a wine expert specializing in providing wine advice and food pairing recommendations. Only answer questions related to wine and food pairings. If asked about anything else, politely inform the user that you can only assist with wine and food pairing inquiries."},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7
            )
            advice = completion.choices[0].message.content.strip()
            app.logger.info(f"Generated advice: {advice}")  # Logs the generated advice
            return jsonify({"advice": advice})
        else:
            # Return a polite message
            advice = "I'm sorry, but I can only assist with questions related to wine and food pairings."
            app.logger.info(f"Non-related query response: {advice}")
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
