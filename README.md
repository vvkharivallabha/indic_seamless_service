---
title: Indic Seamless Speech-to-Text
emoji: 🎤
colorFrom: blue
colorTo: purple
sdk: fastapi
sdk_version: 0.110.0
app_file: app.py
pinned: false
license: apache-2.0
hardware: cpu-basic
---

# 🎤 Indic-Seamless Speech-to-Text Service

A powerful multilingual speech-to-text service supporting 100+ languages using the `ai4bharat/indic-seamless` model.

## 🌟 Features

- **100+ Languages**: Support for major world languages including Indic languages
- **High Accuracy**: State-of-the-art AI4Bharat model
- **REST API**: Easy-to-use FastAPI endpoints
- **Multiple Formats**: Support for WAV, MP3, FLAC, M4A, OGG audio files
- **Real-time Processing**: Fast inference with optimized model loading

## 🚀 API Endpoints

- **Health Check**: `GET /health` - Service status and supported languages
- **Speech-to-Text**: `POST /speech-to-text` - Convert audio to text
- **Supported Languages**: `GET /supported-languages` - List all supported languages
- **Documentation**: `GET /docs` - Interactive API documentation

## 📝 Usage Example

```python
import requests

# Upload audio file for transcription
files = {"audio": open("audio.wav", "rb")}
data = {"target_lang": "English"}

response = requests.post(
    "https://your-space-name.hf.space/speech-to-text",
    files=files,
    data=data
)

result = response.json()
print(f"Transcription: {result['transcription']}")
```

## 🎯 Supported Languages

The service supports 100+ languages including:

- **Indic Languages**: Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Urdu, Assamese, Odia, and more
- **European Languages**: English, French, German, Spanish, Italian, Portuguese, Dutch, Russian, and more
- **Asian Languages**: Chinese, Japanese, Korean, Thai, Vietnamese, Indonesian, and more
- **African Languages**: Swahili, Yoruba, Igbo, Amharic, and more

## 🔧 Technical Details

- **Model**: `ai4bharat/indic-seamless` - A state-of-the-art multilingual speech model
- **Framework**: FastAPI with async support
- **Audio Processing**: Librosa and SoundFile for optimal audio handling
- **Memory Optimized**: Efficient model loading for cloud deployment

## 📊 Model Information

This service uses the AI4Bharat Indic-Seamless model, which is specifically designed for:

- High-quality speech recognition across diverse languages
- Robust performance on various audio qualities
- Optimized inference for production use
- Support for both formal and colloquial speech patterns

## 🛠️ Development

The service is built with:

- **Backend**: FastAPI (Python)
- **ML Framework**: PyTorch + Transformers
- **Audio Processing**: Librosa, SoundFile
- **Deployment**: Hugging Face Spaces

## 📄 License

Apache 2.0 License - see LICENSE file for details.

---

Built with ❤️ using AI4Bharat's Indic-Seamless model
