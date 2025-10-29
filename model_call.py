import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def azure_model_rest_api_call(body_dict: dict):
    """
    Call the Azure ML online endpoint using credentials from .env.

    .env must contain:
      model_url=https://endpoint-rfmodel22.eastus2.inference.ml.azure.com/score
      model_api_key=YOUR_KEY

    body_dict must look like:
    {
        "data": [
            {
                "AccountWeeks": ...,
                "ContractRenewal": ...,
                "DataPlan": ...,
                "DataUsage": ...,
                "CustServCalls": ...,
                "DayMins": ...,
                "DayCalls": ...,
                "MonthlyCharge": ...,
                "OverageFee": ...,
                "RoamMins": ...,
                "AvgCallDuration": ...,
                "CostPerUsage": ...
            }
        ]
    }

    Returns whatever the endpoint returns.
    Expected successful shape:
    {
        "predictedOutcomes": [0 or 1],
        "inputFeatures": [ { ...same features... } ]
    }
    """

    model_url = os.getenv("model_url")
    api_key = os.getenv("model_api_key")

    if not model_url or not api_key:
        raise RuntimeError(
            "Missing model_url or model_api_key in .env. "
            "Add them and restart Streamlit.\n"
            "Example:\n"
            "model_url=https://endpoint-rfmodel22.eastus2.inference.ml.azure.com/score\n"
            "model_api_key=Af3wfHarZHDlvgZoYzDZjcZ23b4FNwWMFRAZML4bzd"
        )

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    try:
        resp = requests.post(
            model_url,
            headers=headers,
            data=json.dumps(body_dict),
            timeout=30,
        )
    except requests.exceptions.RequestException as e:
        # covers DNS issues, network issues, timeout, etc.
        raise RuntimeError(
            f"Network error calling Azure endpoint:\n{e}"
        )

    # Handle HTTP errors (400s, 500s, etc.)
    if resp.status_code == 401:
        raise RuntimeError(
            "Unauthorized (401).\n\n"
            "Azure rejected the key you're sending.\n"
            "Make sure model_api_key in .env matches the key from the Azure ML 'Consume' tab "
            "for this exact endpoint."
        )

    if resp.status_code >= 400:
        raise RuntimeError(
            f"Endpoint returned HTTP {resp.status_code}.\n\n"
            f"Response text from Azure:\n{resp.text}\n\n"
            "This usually means:\n"
            "- The request body format didn't match what the service expects (check that we're sending 'data': [ {...} ])\n"
            "- Or the model is throwing an error internally."
        )

    # Parse successful JSON
    try:
        return resp.json()
    except ValueError:
        raise RuntimeError(
            f"Endpoint returned non-JSON response:\n{resp.text}"
        )
