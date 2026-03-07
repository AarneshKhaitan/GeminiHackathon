#!/usr/bin/env python3
"""List available Gemini models"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

load_dotenv(dotenv_path="../.env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY not set in .env file")
    exit(1)

print("=" * 60)
print("Available Gemini Models")
print("=" * 60)

# Configure the API
genai.configure(api_key=api_key)

try:
    # List all available models
    models = genai.list_models()

    print("\n📋 All available models:\n")
    for model in models:
        # Only show models that support generateContent
        if 'generateContent' in model.supported_generation_methods:
            print(f"✓ {model.name}")
            print(f"  Display name: {model.display_name}")
            print(f"  Description: {model.description}")
            print(f"  Input token limit: {model.input_token_limit:,}")
            print(f"  Output token limit: {model.output_token_limit:,}")
            print()

except Exception as e:
    print(f"❌ Error listing models: {e}")

print("\n" + "=" * 60)
print("Recommended for this project: gemini-1.5-pro or gemini-1.5-flash")
print("=" * 60)
