<p align="center">
  <img src="static/img/logo.svg" alt="Gear Calc Logo" width="200"/>
</p>

# Gear Calc

Gear Calc is a self-hosted application designed for cyclists and mechanics to calculate gear ratios and manage bicycle gear configurations. It helps you visualize and compare different drivetrain setups to find the perfect gear range for your riding style.

## Features

- **Gear Ratio Calculator**: Instantly calculate gear ratios, development, and percentage changes for various chainring and cassette combinations.
- **Configuration Management**: Save, update, and organize different gear setups for multiple bikes or terrain types.
- **Component Library**: Maintain a database of your chainrings and cassettes to quickly build new configurations.
- **Preferences**: Define your custom "optimal" ratio range. The app visually highlights gears that fall within, above, or below your preferred cadence/power zone.
- **Visualizations**: View detailed gear tables with color-coded status indicators and total range percentages.

## How it Works

Gear Calc is a lightweight web application built with:
- **Backend**: FastAPI (Python) for robust and fast API handling.
- **Database**: SQLite for simple, self-contained data storage.
- **Frontend**: Server-side rendered HTML using Jinja2 templates for a fast and responsive user interface without complex client-side frameworks.

## Usage

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/gear-calc.git
    cd gear-calc
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the App

1.  Start the server:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8005 --reload --log-config uvicorn_log_config.ini
    ```

2.  Open your browser and navigate to:
    ```
    http://localhost:8005
    ```

### Docker

You can also run Gear Calc using Docker:

1.  Use the provided script (recommended):
    ```bash
    ./create-container-gearcalc.sh
    ```

2.  Or manually:
    ```bash
    docker build -t gear-calc .
    docker run -d --name=gear-calc -p 8005:8005 -v ~/code/container_data:/app/data gear-calc
    ```

The application will be available at `http://localhost:8005`
