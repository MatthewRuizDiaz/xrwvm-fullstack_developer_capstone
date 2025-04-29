# restapis.py
import requests
# import json # F401: Unused import json
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")


def get_request(endpoint, **kwargs):
    params = ""
    if kwargs:
        for key, value in kwargs.items():
            params = params + key + "=" + value + "&"

    request_url = backend_url + endpoint + "?" + params

    print(f"GET from {request_url} ")
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        # If any error occurs during the request
        print(f"Network exception occurred: {e}")
        return None  # Indicate failure
    except Exception as err:
        # Handle potential JSON decoding errors or other issues
        print(f"An error occurred: {err}")
        return None


def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url + "/analyze/" + text
    print(f"Analyzing sentiment for: {request_url}")
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Network exception occurred during sentiment analysis: {e}")
        return None
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print("Error during sentiment analysis.")
        return None


def post_review(data_dict):
    request_url = backend_url + "/insert_review"
    try:
        response = requests.post(request_url, json=data_dict)
        print(f"Review POST Status Code: {response.status_code}")
        print(f"Review POST Response Body: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Network exception occurred posting review: {e}")
        return None
    except Exception as err:
        print(f"Error posting review: {err}")
        return None