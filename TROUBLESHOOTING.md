# Troubleshooting Guide

This guide helps you resolve common issues with the Indic-Seamless Model Service.

## Common Issues and Solutions

### 1. Model Loading Issues

**Problem**: Model fails to load or service crashes on startup.

**Solutions**:
- Ensure you have sufficient RAM (at least 8GB recommended)
- Check if CUDA is available for GPU acceleration
- Verify internet connection for model download
- Try running the model loading test:

```bash
python test_model_loading.py
```

### 2. Linter Errors

**Problem**: Type checker shows errors about missing stubs.

**Solutions**:
- Install type stubs for better linter support:

```bash
python install_stubs.py
```

- These errors are typically not critical and don't affect functionality
- ML libraries like PyTorch and Transformers often don't have complete type stubs

### 3. Token Decoding Errors

**Problem**: `TypeError: int() argument must be a string, a bytes-like object or a real number, not 'list'` or `argument 'ids': 'list' object cannot be interpreted as an integer`

**Solutions**:
- This has been fixed in the latest version with the improved `safe_decode_tokens` function
- The error occurs when the model returns unexpected token formats (list of lists vs single list)
- The updated function now properly handles batch outputs and single sequences
- Restart the service to use the updated code
- Debug with: `python debug_tokens.py`

### 4. Model Generation Errors

**Problem**: `KeyError: 'inputs'` or `SeamlessM4TFeatureExtractor.__call__() missing 1 required positional argument: 'raw_speech'`

**Solutions**:
- Fixed by using the correct model classes and generation methods
- **Text processing**: Use `tokenizer()` instead of `processor()`
- **Audio processing**: Use `processor()` (feature extractor) for audio
- **Generation**: Use `model.generate(**inputs, tgt_lang=target_lang)` for SeamlessM4Tv2
- Test with: `python test_comprehensive.py`

### 5. Vocoder Overflow Errors

**Problem**: `RuntimeError: Storage size calculation overflowed with sizes=[9223372036854774023]`

**Solutions**:
- This error occurs when the model tries to use the vocoder for text generation
- Fixed by using proper generation parameters: `do_sample=False`, `max_length=512`, `num_beams=1`
- The error typically happens in text translation when the model incorrectly uses speech generation
- Restart the service to use the updated generation parameters
- Test with: `python test_translation.py`

### 6. Language Code Issues

**Problem**: "Unsupported language" errors.

**Solutions**:
- Use the correct language codes from the indic-seamless model
- Check supported languages: `GET /supported-languages`
- Common codes: `eng` (English), `hin` (Hindi), `ben` (Bengali), etc.

### 7. Audio Processing Issues

**Problem**: Audio files not processed correctly.

**Solutions**:
- Ensure audio files are in supported formats: wav, mp3, flac, m4a, ogg
- Check file size (max 50MB)
- Verify audio quality and sample rate

### 8. Memory Issues

**Problem**: Out of memory errors.

**Solutions**:
- Use CPU instead of GPU: Set `CUDA_VISIBLE_DEVICES=""`
- Reduce batch size or input length
- Increase system RAM or use swap space
- Use model quantization for lower memory usage

### 9. Network/Connection Issues

**Problem**: Service not accessible or slow responses.

**Solutions**:
- Check if service is running: `curl http://localhost:8000/health`
- Verify port configuration (default: 8000)
- Check firewall settings
- Monitor network connectivity

## Testing and Debugging

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Model Loading Test
```bash
python test_model_loading.py
```

### 3. Language Code Test
```bash
python test_languages.py
```

### 4. Client Example
```bash
python client_example.py
```

## Performance Optimization

### 1. GPU Acceleration
- Ensure CUDA is installed and available
- Monitor GPU memory usage
- Use mixed precision for faster inference

### 2. Model Optimization
- Use model quantization (INT8/FP16)
- Enable model caching
- Implement request batching

### 3. System Resources
- Monitor CPU and memory usage
- Use SSD storage for faster I/O
- Optimize network configuration

## Logs and Monitoring

### 1. Service Logs
- Check application logs for errors
- Monitor model loading status
- Track request/response times

### 2. System Monitoring
- Monitor system resources (CPU, RAM, GPU)
- Check disk space and I/O
- Monitor network usage

### 3. Error Tracking
- Common error patterns:
  - Model loading failures
  - Token decoding issues
  - Audio processing errors
  - Language validation failures

## Getting Help

If you encounter issues not covered in this guide:

1. Check the service logs for detailed error messages
2. Run the test scripts to isolate the problem
3. Verify your environment and dependencies
4. Check the GitHub issues for similar problems
5. Create a detailed bug report with:
   - Error messages and logs
   - Environment details
   - Steps to reproduce
   - Expected vs actual behavior

## Environment Requirements

### Minimum Requirements
- Python 3.8+
- 8GB RAM
- 10GB disk space
- Internet connection for model download

### Recommended Requirements
- Python 3.10+
- 16GB+ RAM
- GPU with CUDA support
- SSD storage
- High-speed internet

### Dependencies
- See `env/requirements.txt` for complete list
- Key dependencies: torch, transformers, fastapi, librosa 