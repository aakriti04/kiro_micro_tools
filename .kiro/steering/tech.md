# Technology Stack

## Core Technologies

- **Python**: 3.8+ (3.10+ recommended)
- **GUI Framework**: PyQt6 >= 6.4.0
- **Encoding Detection**: chardet >= 5.0.0

## Testing Stack

- **Unit Testing**: pytest >= 7.0.0
- **Property-Based Testing**: hypothesis >= 6.0.0

## Development Tools (Optional)

- **Code Formatting**: black >= 22.0.0
- **Linting**: pylint >= 2.15.0
- **Type Checking**: mypy >= 0.990

## Common Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python main.py
```

### Testing
```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run property-based tests
pytest tests/property/

# Run integration tests
pytest tests/integration/
```

### Development
```bash
# Format code
black .

# Lint code
pylint src/ tests/

# Type check
mypy src/
```

## Build System

No build system required - pure Python application with direct execution via `python main.py`.
