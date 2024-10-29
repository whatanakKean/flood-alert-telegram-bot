import os
import requests
from chatbot.queries import fetch_measurement, predict_water_level
from hugchat import hugchat
from hugchat.login import Login
from dotenv import load_dotenv

load_dotenv()

if os.getenv("HF_EMAIL") and os.getenv("HF_PASSWORD"):
    sign = Login(os.getenv("HF_EMAIL"), os.getenv("HF_PASSWORD"))
    cookies = sign.login()
else:
    cookies = requests.get("https://huggingface.co/chat/").cookies

# Create a ChatBot
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())


def generate_response(message: str, station: str = "PPB", forecast_days: int = 5, time_range: str = "15d"):
    """Generate a response to a message"""
    response_queue = ""

    forecast_data = predict_water_level(forward_days=forecast_days)
    water_level = fetch_measurement(station=station, time_range=time_range, measurement="water_level")
    rainfall = fetch_measurement(station=station, time_range=time_range, measurement="rainfall")
    water_flow = fetch_measurement(station=station, time_range=time_range, measurement="water_flow")

    # Check if data was successfully retrieved, providing default text if unavailable
    forecast_info = forecast_data if forecast_data else "Forecast data is unavailable."
    water_level_info = water_level if water_level else "Water Level data is unavailable."
    rainfall_info = rainfall if rainfall else "Rainfall data is unavailable."
    water_flow_info = water_flow if water_flow else "Water Flow data is unavailable."

    # Build the context with factual information
    context = f"""
    >>> Here is additional factual information you can use as a reference if asked

    + Water Level Forecast (Next {forecast_days} days): {forecast_info}
    + Current Water Level Data for {station} (Last {time_range}): {water_level_info}
    + Current Rainfall Data for {station} (Last {time_range}): {rainfall_info}
    + Current Water Flow Data for {station} (Last {time_range}): {water_flow_info}
    """
    
    for resp in chatbot.chat(
        f"{context} \n\n >>> User prompt: {message}",
        _stream_yield_all=True
    ):
        if resp:
            if "token" in resp:
                response_queue += resp["token"]
        if len(response_queue) > 100:
            yield response_queue
            response_queue = ""
    yield response_queue
