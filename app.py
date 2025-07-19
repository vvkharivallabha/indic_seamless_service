"""
Hugging Face Spaces deployment for Indic-Seamless Speech-to-Text Service
Uses Gradio to wrap FastAPI for HF Spaces compatibility
"""

import os
import threading
import time

import gradio as gr
import requests
import uvicorn

from src.api.app import create_app

# Set environment variables for HF Spaces
os.environ.setdefault("HOST", "0.0.0.0")
os.environ.setdefault("PORT", "7860")
os.environ.setdefault("MODEL_NAME", "ai4bharat/indic-seamless")
os.environ.setdefault("DEBUG", "false")

# Create FastAPI app
fastapi_app = create_app()

# Global variable to track FastAPI server
fastapi_server = None


def start_fastapi_server():
    """Start FastAPI server in background thread"""
    global fastapi_server
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="info")


def transcribe_audio(audio_file, target_language="English"):
    """
    Transcribe audio using the FastAPI backend
    """
    if audio_file is None:
        return "Please upload an audio file."

    try:
        # Wait for FastAPI server to be ready
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get("http://127.0.0.1:8000/health", timeout=5)
                if response.status_code == 200:
                    break
            except Exception:
                if i == 0:
                    return (
                        "🔄 Starting model (this may take a few minutes "
                        "on first run)..."
                    )
                time.sleep(10)
        else:
            return "❌ Service failed to start. Please try again."

        # Make transcription request
        files = {"audio": open(audio_file, "rb")}
        data = {"target_lang": target_language}

        response = requests.post(
            "http://127.0.0.1:8000/speech-to-text", files=files, data=data, timeout=300
        )

        if response.status_code == 200:
            result = response.json()
            return (
                f"**Transcription ({target_language}):**\n\n{result['transcription']}"
            )
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return f"❌ Error: {error_detail}"

    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_supported_languages():
    """Get list of supported languages from the API"""
    try:
        response = requests.get("http://127.0.0.1:8000/supported-languages", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return list(data["languages"].values())
    except Exception:
        pass

    # Fallback list of common languages
    return [
        "English",
        "Hindi",
        "Bengali",
        "Tamil",
        "Telugu",
        "Marathi",
        "Gujarati",
        "Kannada",
        "Malayalam",
        "Punjabi",
        "Urdu",
        "Spanish",
        "French",
        "German",
        "Chinese",
        "Japanese",
        "Korean",
    ]


# Start FastAPI server in background
threading.Thread(target=start_fastapi_server, daemon=True).start()

# Create Gradio interface
with gr.Blocks(
    title="🎤 Indic-Seamless Speech-to-Text",
    theme=gr.themes.Soft(),
) as demo:
    gr.Markdown(
        """
    # 🎤 Indic-Seamless Speech-to-Text Service
    
    Convert speech to text in 100+ languages using the AI4Bharat Indic-Seamless model.
    
    **Supported formats:** WAV, MP3, FLAC, M4A, OGG
    """
    )

    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(
                sources=["upload", "microphone"],
                type="filepath",
                label="Upload Audio File or Record",
            )
            language_dropdown = gr.Dropdown(
                choices=get_supported_languages(),
                value="English",
                label="Target Language",
                interactive=True,
            )
            transcribe_btn = gr.Button("🎯 Transcribe Speech", variant="primary")

        with gr.Column():
            output_text = gr.Textbox(
                label="Transcription Result",
                lines=10,
                placeholder="Your transcription will appear here...",
            )

    # Event handlers
    transcribe_btn.click(
        fn=transcribe_audio,
        inputs=[audio_input, language_dropdown],
        outputs=output_text,
    )

    gr.Markdown(
        """
    ---
    ### 📚 API Documentation
    
    For programmatic access, use these endpoints:
    - **Health Check:** `/health` - Service status
    - **Transcribe:** `/speech-to-text` - Upload audio for transcription
    - **Languages:** `/supported-languages` - Get all supported languages
    - **API Docs:** `/docs` - Interactive API documentation
    
         ### 🌍 Supported Languages
     This service supports 100+ languages including all major Indic languages
     (Hindi, Bengali, Tamil, Telugu, etc.), European languages 
     (English, Spanish, French, German, etc.), and many others.
    
    Built with ❤️ using AI4Bharat's Indic-Seamless model.
    """
    )

# Launch the Gradio app
if __name__ == "__main__":
    print("🎤 Starting Indic-Seamless Speech-to-Text Service on HF Spaces...")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
