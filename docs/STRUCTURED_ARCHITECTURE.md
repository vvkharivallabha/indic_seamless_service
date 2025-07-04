# Structured Architecture Guide

## Overview

The Indic-Seamless Service now offers a structured, modular architecture that promotes maintainability, scalability, and code organization. This guide explains the new structure and how to use it.

## Architecture Overview

The Indic-Seamless Service uses a **structured modular architecture** with the following components:

### **Current Architecture (`start_service.py` + `src/`)**
```
start_service.py - Production service launcher with health checks
src/
├── config/          - Configuration management
├── types/           - Type definitions and schemas
├── utils/           - Utility functions
└── api/             - API layer and routes
```

## Module Structure

### 📁 `src/config/` - Configuration Management
- **`settings.py`** - Application settings with environment variable support
- **`languages.py`** - Language enum and mappings (98 languages)
- **`__init__.py`** - Module exports

**Key Features:**
- Environment variable configuration
- Centralized settings management
- Language code to name mappings
- FastAPI dropdown-friendly language enum

### 📁 `src/types/` - Type Definitions
- **`schemas.py`** - Pydantic request/response models
- **`models.py`** - Internal data structures (ModelState)
- **`__init__.py`** - Module exports

**Key Features:**
- Type-safe API contracts
- Model state management
- JSON schema examples for API docs

### 📁 `src/utils/` - Utility Functions
- **`audio.py`** - Audio processing utilities
- **`model.py`** - Model loading and token decoding
- **`logging.py`** - Logging configuration
- **`__init__.py`** - Module exports

**Key Features:**
- Reusable audio processing functions
- Safe model loading with error handling
- Centralized logging setup

### 📁 `src/api/` - API Layer
- **`app.py`** - FastAPI application factory (src/api/app.py)
- **`routes.py`** - API endpoint definitions
- **`__init__.py`** - Module exports

**Key Features:**
- Clean separation of concerns
- Application factory pattern
- Modular route organization

## Usage

### Running the Application

```bash
# Using Makefile
make deploy-local

# Direct execution
python start_service.py

# With environment variables
LOG_LEVEL=DEBUG python start_service.py

# With custom port
python start_service.py --port 8001
```

### Environment Configuration

Create a `.env` file from the template:
```bash
cp env.example .env
```

Configure your settings:
```env
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
MODEL_NAME=ai4bharat/indic-seamless
```

### Importing Modules

```python
# Configuration
from src.config.settings import settings
from src.config import TargetLanguage, SUPPORTED_LANGUAGES

# Types
from src.types import STTResponse, HealthResponse, ModelState

# Utilities
from src.utils import preprocess_audio, load_model, setup_logging

# API
from src.api import create_app
```

## Benefits

### 🔧 **Maintainability**
- **Separation of Concerns** - Each module has a single responsibility
- **Modular Design** - Easy to modify individual components
- **Clear Dependencies** - Explicit imports and module boundaries

### 📈 **Scalability**
- **Extensible Architecture** - Easy to add new features
- **Reusable Components** - Utilities can be shared across modules
- **Configuration Management** - Environment-based configuration

### 🧪 **Testability**
- **Unit Testing** - Each module can be tested independently
- **Mocking** - Easy to mock dependencies
- **Integration Testing** - Clear API contracts

### 👥 **Developer Experience**
- **Code Organization** - Logical file structure
- **Type Safety** - Comprehensive type definitions
- **Documentation** - Self-documenting code structure

## Development Guide

### Working with the Structured Architecture

The service uses a clean, modular structure that makes development and maintenance straightforward:

1. **Configuration** - All settings are managed in `src/config/`
2. **Type Safety** - Request/response models are defined in `src/types/`
3. **Utilities** - Reusable functions are organized in `src/utils/`
4. **API Layer** - Routes and application factory are in `src/api/`

### Configuration Migration

**Before (Hardcoded):**
```python
app = FastAPI(title="My App", port=8000)
```

**After (Environment-based):**
```python
from src.config.settings import settings
app = FastAPI(title=settings.title, port=settings.port)
```

### Model Loading Migration

**Before (Inline):**
```python
model = load_model_function()
```

**After (Structured):**
```python
from src.types import ModelState
from src.utils import load_model

model_state = ModelState()
load_model(model_state)
```

## Best Practices

### 🎯 **Configuration**
- Use environment variables for deployment-specific settings
- Keep sensitive data in environment variables
- Provide sensible defaults

### 🏗️ **Code Organization**
- Keep modules focused and cohesive
- Use clear naming conventions
- Document module purposes

### 🔒 **Type Safety**
- Use Pydantic models for API contracts
- Define internal data structures
- Leverage Python type hints

### 📝 **Error Handling**
- Centralize error handling in utilities
- Use structured logging
- Provide meaningful error messages

## Performance

The structured architecture has minimal performance overhead:

- **Import Time** - Slightly higher due to module imports
- **Runtime Performance** - Identical to monolithic version
- **Memory Usage** - Same memory footprint
- **Model Loading** - Same loading time and efficiency

## Future Enhancements

The structured architecture enables:

- **Plugin System** - Easy to add new language processors
- **Caching Layer** - Modular caching for models and results
- **Monitoring** - Structured metrics and health checks
- **API Versioning** - Clean API version management
- **Microservices** - Easy to split into microservices if needed

## Conclusion

The structured architecture provides a solid foundation for long-term development while maintaining compatibility with the existing monolithic approach. Choose the approach that best fits your deployment needs and development preferences. 