from flask import Flask, request, jsonify, render_template
from analyze import read_image
import logging
import validators

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__, template_folder="templates")


@app.route("/")
def home():
    """
    Home page with an upload form for testing the API.
    """
    return render_template("index.html")


@app.route("/api/v1/analysis/", methods=["GET"])
def analysis():
    """
    Endpoint for analyzing an image using Azure's OCR API.
    Expects a JSON payload with the "uri" field.
    """
    try:
        # Get and validate JSON payload
        get_json = request.get_json()
        if not get_json or "uri" not in get_json:
            return jsonify({"error": 'Missing or invalid JSON payload. Expected {"uri": "image_url"}.'}), 400

        image_uri = get_json["uri"]
        if not validators.url(image_uri):
            return jsonify({"error": "The provided URI is not a valid URL."}), 400

        # Call analyze.py's read_image function
        logging.info(f"Received URI for analysis: {image_uri}")
        result = read_image(image_uri)

        # Return result
        if "Error" in result:
            return jsonify({"error": result}), 500
        return jsonify({"text": result}), 200

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Unexpected error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)