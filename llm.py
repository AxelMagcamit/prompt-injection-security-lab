import requests

from config import OLLAMA_URL, MODEL


def ask_llm(prompt):

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0
        }
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "")

    except requests.exceptions.ConnectionError:

        return (
            "ERROR: Could not connect to Ollama. "
            "Make sure Ollama is running."
        )

    except requests.exceptions.Timeout:

        return "ERROR: LLM request timed out."

    except Exception as e:

        return f"ERROR: {str(e)}"