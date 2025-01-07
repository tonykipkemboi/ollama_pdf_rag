# LLM Manager API

This page documents the Language Model management components.

## LLMManager

```python
class LLMManager:
    """Manages Ollama language model interactions."""
    
    def __init__(self, model_name: str = "llama2"):
        """Initialize LLM manager with model name."""
```

### Methods

#### list_models
```python
def list_models() -> List[str]:
    """List available Ollama models."""
```

Returns:
- List of model names

#### get_model
```python
def get_model(self, model_name: str) -> LLM:
    """Get an instance of the specified model."""
```

Parameters:
- `model_name`: Name of the Ollama model

Returns:
- LLM instance

#### generate
```python
def generate(self, prompt: str, **kwargs) -> str:
    """Generate text using the current model."""
```

Parameters:
- `prompt`: Input text
- `**kwargs`: Additional generation parameters

Returns:
- Generated text

## Usage Example

```python
# Initialize manager
manager = LLMManager(model_name="llama2")

# List available models
models = manager.list_models()

# Generate text
response = manager.generate(
    prompt="Explain RAG in simple terms",
    temperature=0.7,
    max_tokens=500
)
```

## Model Parameters

Configure model behavior with:

- `temperature`: Creativity (0.0-1.0)
- `max_tokens`: Response length
- `top_p`: Nucleus sampling
- `frequency_penalty`: Repetition control

## Error Handling

The manager handles:

- Model loading errors
- Generation timeouts
- Resource constraints
- API communication issues

## Best Practices

1. **Model Selection**
   - Match model to task
   - Consider resource usage
   - Test performance

2. **Parameter Tuning**
   - Adjust temperature
   - Control response length
   - Balance quality/speed
``` 