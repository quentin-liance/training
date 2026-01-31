# Company Margin Analyzer

A Streamlit application for analyzing company margins with detailed income and cost breakdowns.

## Features

- 📊 Interactive dashboard with key metrics
- 💰 Detailed income analysis by category and month
- 💸 Comprehensive cost breakdown
- 📈 Visual charts and trends
- 🔍 Filtering capabilities
- 📥 Data export functionality

## Installation

```bash
pip install -e .
```

## Running the App

```bash
streamlit run src/app.py
```

The app will open in your default browser at `http://localhost:8501`

## Project Structure

```
├── src/
│   ├── app.py                 # Main Streamlit application
│   ├── data/
│   │   └── generator.py       # Fake data generation
│   └── utils/
│       └── calculations.py    # Calculation utilities
├── tests/
│   └── test_calculations.py   # Unit tests
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── pyproject.toml            # Project dependencies and configuration
└── README.md                # This file
```

## Data

The application uses generated fake data for demonstration purposes. Data includes:
- Monthly income across multiple categories
- Monthly costs across various expense categories
- Automatic calculation of margins and percentages

## Development

Install with development dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```
