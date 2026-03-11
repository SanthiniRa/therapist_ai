#!/usr/bin/env python3
"""
Script to list available Gemini models.
Run this after setting your GOOGLE_API_KEY environment variable.
"""

import google.genai as genai
import os

#api_key = os.getenv("GENAI_API_KEY") or os.getenv("GOOGLE_API_KEY")
api_key = "AIzaSyCbsqht0mYD9-VsWYGJw7w_lHweVzFmvgg"
if not api_key:
    print("Error: Set GENAI_API_KEY or GOOGLE_API_KEY environment variable")
    exit(1)

client = genai.Client(api_key=api_key)

try:
    models = client.models.list()
    print("Available models:")
    for model in models:
        print(f"  - {model.name}")
except Exception as e:
    print(f"Error listing models: {e}")