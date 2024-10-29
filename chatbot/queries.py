import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch variables from the .env file
PREDICT_API_URL = os.getenv("PREDICT_API_URL")
FLOOD_ALERT_API_URL = os.getenv("FLOOD_ALERT_API_URL")
FLOOD_ALERT_IMAGE_API_URL  = os.getenv("FLOOD_ALERT_IMAGE_API_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def predict_water_level(forward_days=5):
    """
    Predict water levels for a given number of forward days.
    """
    # Define the input data
    input_data = {"forward": forward_days}

    try:
        # Make a GET request to the prediction API
        response = requests.get(PREDICT_API_URL, json=input_data)
        
        # Check the response status code
        if response.status_code == 200:
            # Return the response data
            return response.json()
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred: {e}"

def fetch_measurement(station, time_range, measurement, token=ACCESS_TOKEN):
    """
    Fetch measurement data from the flood alert API.
    """
    params = {
        "station": station,
        "range": time_range,
        "measurement": measurement
    }
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        # Make the GET request to fetch measurement data
        response = requests.get(FLOOD_ALERT_API_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def fetch_image(station, time_range, token=ACCESS_TOKEN):
    """
    Fetch an image related to water level data from the flood alert API.
    """
    # Define the query parameters and headers
    params = {
        "station": station,
        "range": time_range
    }
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        # Make the GET request to fetch the image
        response = requests.get(FLOOD_ALERT_IMAGE_API_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    
def fetch_metadata(token=ACCESS_TOKEN):
    return [ "Phnom Penh (Bassac)", "Siem Reap", "Battambang"]