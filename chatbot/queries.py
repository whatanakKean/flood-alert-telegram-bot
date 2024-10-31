import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(override=True)

# Fetch variables from the .env file
PREDICT_API_URL = os.getenv("PREDICT_API_URL")
TOKEN = os.getenv("TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
TOKEN_REFRESH_URL = os.getenv("TOKEN_REFRESH_URL")

def predict_water_level(forward_days=5):
    """
    Predict water levels for a given number of forward days.
    """
    # Define the request parameters
    params = {"forward": forward_days}

    try:
        # Make a GET request to the prediction API with query parameters
        response = requests.get(PREDICT_API_URL, params=params)

        # Check the response status code
        if response.status_code == 200:
            return response.json()  # Return the JSON response
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred: {e}"

def refresh_access_token(username, password):
    url = os.getenv('LOGIN_URL')  # Get the login URL from environment variable

    if not url:
        print("Error: LOGIN_URL environment variable is not set.")
        return None
    
    # Prepare the headers
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'  # Mimic a browser
    }
    
    # Prepare the data payload
    data = {
        'grant_type': 'password',
        'username': username,  # Include username
        'password': password,  # Include password
        'scope': '',  # Optional, remove if not needed
        'client_id': None,  # Remove if not required
        'client_secret': None  # Remove if not required
    }
    
    # Send the POST request
    response = requests.post(url, headers=headers, data=data)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response JSON
        response_json = response.json()
        new_access_token = response_json.get('access_token')
        return new_access_token
    else:
        # Handle errors if needed
        print(f"Error: {response.status_code} - {response.text}")
        return None

def fetch_measurement(station="bassac", range="15d", measurement="water_level"):
    url = os.getenv('INFLUX_URL')  # Get the influx URL from environment variable
    token = os.getenv('TOKEN')  # Retrieve access token from environment variable

    headers = {
        'accept': 'application/json',
        'Authorization': f"Bearer {token}"
    }
    
    params = {
        'station': station,
        'range': range,
        'measurement': measurement
    }
    
    response = requests.get(url, headers=headers, params=params)
    from urllib.parse import urlencode
    full_url = f"{url}?{urlencode(params)}"
    print("Full URL:", full_url)
    print(response.status_code)
    print(headers)
    exit()
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 403: 
        username = os.getenv('USERNAME')
        password = os.getenv('PASSWORD')
        refresh_token = os.getenv('REFRESH_TOKEN')

        # Try refreshing the token
        token = refresh_access_token(username, password, refresh_token)
        
        if token:  # Check if we got a new token
            headers['Authorization'] = f"Bearer {token}"
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()  # Return the new JSON response
            else:
                raise Exception(f"Error after refreshing token: {response.status_code}, {response.text}")
        else:
            raise Exception("Failed to refresh token.")
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

def fetch_image_data(station="bassac", range="15d"):
    url = os.getenv('IMAGE_URL')  # Get the image URL from environment variable
    token = os.getenv('TOKEN')  # Retrieve access token from environment variable
    
    headers = {
        'accept': 'application/json',
        'Authorization': f"Bearer {token}"
    }
    
    params = {
        'station': station,
        'range': range
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()  # Return the JSON response
    elif response.status_code == 403:  # Unauthorized, possibly token expired
        # Retrieve credentials from environment variables
        username = os.getenv('USERNAME')
        password = os.getenv('PASSWORD')
        refresh_token = os.getenv('REFRESH_TOKEN')

        # Try refreshing the token
        token = refresh_access_token(username, password, refresh_token)
        
        if token:  # Check if we got a new token
            headers['Authorization'] = f"Bearer {token}"
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()  # Return the new JSON response
            else:
                raise Exception(f"Error after refreshing token: {response.status_code}, {response.text}")
        else:
            raise Exception("Failed to refresh token.")
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

def fetch_metadata():
    """
    Mock function to fetch metadata. This can be expanded to call an API
    if metadata fetching from the API is required.
    """
    return ["bassac"]

if __name__ == "__main__":
    # Access the environment variables
    # print(fetch_measurement()['data'][-1])
    print(refresh_access_token("nak", "nak"))
