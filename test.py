import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def refresh_access_token(username, password, refresh_token):
    url = os.getenv('LOGIN_URL')  # Get the login URL from environment variable
    
    # Prepare the headers
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Prepare the data payload
    data = {
        'grant_type': 'password',
        'refresh_token': refresh_token,
        'username': username,  # Include username
        'password': password,  # Include password
        'client_id': 'string',  # Replace with actual client_id if needed
        'client_secret': ''      # Replace with actual client_secret if needed
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

def fetch_measurement(station="bassac", range_period="15d", measurement="water_level"):
    url = os.getenv('INFLUX_URL')  # Get the influx URL from environment variable
    token = os.getenv('TOKEN')  # Retrieve access token from environment variable

    headers = {
        'accept': 'application/json',
        'Authorization': f"Bearer {token}"
    }
    
    params = {
        'station': station,
        'range': range_period,
        'measurement': measurement
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()  # Return the JSON response
    elif response.status_code == 401:  # Unauthorized, possibly token expired
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

def fetch_image_data(station="bassac", range_period="15d"):
    url = os.getenv('IMAGE_URL')  # Get the image URL from environment variable
    token = os.getenv('TOKEN')  # Retrieve access token from environment variable
    
    headers = {
        'accept': 'application/json',
        'Authorization': f"Bearer {token}"
    }
    
    params = {
        'station': station,
        'range': range_period
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()  # Return the JSON response
    elif response.status_code == 401:  # Unauthorized, possibly token expired
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

# Example usage
if __name__ == "__main__":
    # Access the environment variables
    print(fetch_measurement())
