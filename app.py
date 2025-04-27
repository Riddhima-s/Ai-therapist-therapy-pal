from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
import time
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get API key from environment variables
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBysD0Y8IIxdWKPpiwnnQMjPdgYC6h6gjs")

# Configure Gemini AI
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-pro")
    logger.info("Gemini AI model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini AI: {str(e)}")
    raise

@app.route("/", methods=["GET"])
def home():
    """Home page endpoint"""
    return """
    <html>
        <head><title>TherapyPal API</title></head>
        <body>
            <h1>Welcome to TherapyPal API!</h1>
            <p>The server is running.</p>
            <p>Use POST /chat with {"message": "your message"} to interact with the API.</p>
            <p>Check <a href="/health">health status</a></p>
        </body>
    </html>
    """

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route("/chat", methods=["POST"])
def chat():
    """Main endpoint for interacting with Gemini"""
    try:
        # Get the request data
        data = request.json
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' field in request"}), 400
            
        user_input = data["message"]
        logger.info(f"Received message: {user_input[:50]}...")
        
        # Generate response with retry mechanism
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = model.generate_content(user_input)
                
                # Return the response
                return jsonify({
                    "response": response.text,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                retry_count += 1
                logger.warning(f"Attempt {retry_count} failed: {str(e)}")
                if retry_count < max_retries:
                    time.sleep(1)  # Wait before retrying
                else:
                    raise
                
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "error": "Failed to generate response",
            "details": str(e)
        }), 500

# Handle 404 errors
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 5000))
    
    # Set debug based on environment
    debug = os.environ.get("FLASK_ENV") == "development"
    
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)