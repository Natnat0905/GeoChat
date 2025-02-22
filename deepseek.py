import os
import requests
import logging

# Set the DeepSeekMath API URL.
# You can set this URL via an environment variable or hard-code it here.
DEEPSEEKMATH_API_URL = os.getenv("DEEPSEEKMATH_API_URL", "https://api.deepseek.com/math")

def call_deepseek_math(math_query: str) -> str:
    """
    Sends the math query to the DeepSeekMath API and returns the computed result.
    """
    try:
        response = requests.post(DEEPSEEKMATH_API_URL, json={"query": math_query}, timeout=30)
        if response.status_code == 200:
            json_data = response.json()
            return json_data.get("result", "No result returned from DeepSeekMath.")
        else:
            logging.error(f"DeepSeekMath API error: {response.status_code} - {response.text}")
            return "Error retrieving result from DeepSeekMath."
    except Exception as e:
        logging.error(f"Exception when calling DeepSeekMath: {e}")
        return "Exception occurred when contacting DeepSeekMath."
