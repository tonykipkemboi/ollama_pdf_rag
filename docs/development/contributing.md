# Contributing Guide

Thank you for considering contributing to Ollama PDF RAG! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project follows a Code of Conduct that all contributors are expected to adhere to. Please read [CODE_OF_CONDUCT.md](https://github.com/tonykipkemboi/ollama_pdf_rag/blob/main/CODE_OF_CONDUCT.md) before contributing.

## How to Contribute

### Setting Up Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ollama_pdf_rag.git
   cd ollama_pdf_rag
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pre-commit pytest pytest-cov
   ```

5. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Development Workflow

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes
3. Run tests:
   ```bash
   pytest
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request

### Commit Message Guidelines

We follow conventional commits. Format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_document.py
```

### Documentation

- Update documentation for any new features
- Add docstrings to new functions/classes
- Update README.md if needed

## Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings (Google style)
- Keep functions focused and small

## Getting Help

- Open an issue for bugs
- Discuss major changes in issues first
- Join our community discussions

## Release Process

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. Tag the release

## License

By contributing, you agree that your contributions will be licensed under the MIT License. 