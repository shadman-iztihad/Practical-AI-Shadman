import os
import logging
import time
from dotenv import load_dotenv
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Retrieve credentials from environment variables
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_KEY1")

if not AZURE_ENDPOINT or not AZURE_KEY:
    raise EnvironmentError("Azure endpoint and key must be set in environment variables")

# Initialize Azure Computer Vision client
client = ComputerVisionClient(
    endpoint=AZURE_ENDPOINT,
    credentials=CognitiveServicesCredentials(AZURE_KEY)
)


def read_image(uri):
    """
    Reads and processes an image from a given URI using Azure's OCR capabilities.
    """
    try:
        logging.info("Submitting image URI for analysis.")
        number_of_chars_in_operation_id = 36
        max_retries = 10

        # Make initial API call
        response = client.read(uri, language="en", raw=True)
        operation_location = response.headers.get("Operation-Location")
        if not operation_location:
            raise ValueError("Failed to retrieve operation location from response headers.")

        operation_id = operation_location[-number_of_chars_in_operation_id:]

        # Poll for results
        for _ in range(max_retries):
            result = client.get_read_result(operation_id)
            if result.status.lower() not in ["notstarted", "running"]:
                break
            time.sleep(1)
        else:
            return "OCR process took too long to complete."

        if result.status == OperationStatusCodes.succeeded:
            extracted_text = " ".join([line.text for line in result.analyze_result.read_results[0].lines])
            logging.info("Text extraction succeeded.")
            return extracted_text
        else:
            logging.error("OCR process failed.")
            return "OCR process failed."

    except Exception as e:
        logging.error(f"Error during image analysis: {str(e)}")
        return f"Error: {str(e)}"