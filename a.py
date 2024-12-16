from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

try:
    # List available models
    print("Available models:")
    models = client.models.list()
    for model in models.data:  # Access the `.data` attribute to iterate over models
        print(model.id)  # Print the model ID
except Exception as e:
    print(f"Error retrieving models: {str(e)}")