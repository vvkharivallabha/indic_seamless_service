"""
Hugging Face Spaces deployment for Indic-Seamless Speech-to-Text Service
"""

import os

import uvicorn

from src.api.app import create_app

# Set environment variables for HF Spaces
os.environ.setdefault("HOST", "0.0.0.0")
os.environ.setdefault("PORT", "7860")  # HF Spaces default port
os.environ.setdefault("MODEL_NAME", "ai4bharat/indic-seamless")
os.environ.setdefault("DEBUG", "false")

# Create FastAPI app
app = create_app()

if __name__ == "__main__":
    # Get port from environment (HF Spaces uses 7860)
    port = int(os.environ.get("PORT", 7860))

    print("🎤 Starting Indic-Seamless Speech-to-Text Service on HF Spaces...")
    print(f"🌐 Service will be available on port {port}")

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
