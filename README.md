# northflow
A mindfulness/gratitude check-in app, created as the final project for CSC-6302 Database Principles

## Setup

### Prerequisites
- Python 3.8 or higher
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/adamlacasse/northflow.git
cd northflow
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Copy the example environment file and configure:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Development

#### Linting
Run linters for Python and SQL:
```bash
invoke lint          # Lint both Python and SQL
invoke lint-python   # Lint Python only
invoke lint-sql      # Lint SQL only
```
