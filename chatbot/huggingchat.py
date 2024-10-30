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


def generate_response(message: str, context_data: str, station: str = "bassac", forecast_days: int = 5, time_range: str = "1d"):
    """Generate a response to a message"""
    response_queue = ""


    # Build the context with factual information
    context = f"""
    >>> Here is additional factual information you can use as a reference if asked

    {context_data}
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
