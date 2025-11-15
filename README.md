# Chemical Equipment Parameter Visualizer (Hybrid Web + Desktop App)

This project provides a hybrid web and desktop application for visualizing and analyzing chemical equipment parameters. Users can upload CSV files containing equipment data, which is then processed by a Django backend. Both a React-based web frontend and a PyQt5-based desktop frontend consume the backend API to display data tables, charts, and summary statistics.

## Project Overview

The application allows users to:
- Upload CSV files with equipment data (Equipment Name, Type, Flowrate, Pressure, Temperature).
- View data summaries and visualizations (charts).
- Manage a history of the last 5 uploaded datasets.
- Generate PDF reports of the analysis.
- Authenticate users for secure access.

## Tech Stack

| Layer             | Technology                  | Purpose                               |
| :---------------- | :-------------------------- | :------------------------------------ |
| Frontend (Web)    | React.js + Chart.js         | Data visualization and user interface |
| Frontend (Desktop)| PyQt5 + Matplotlib          | Data visualization and user interface |
| Backend           | Python Django + Django REST Framework | Common API for both frontends         |
| Data Handling     | Pandas                      | Reading CSV and analytics             |
| Database          | SQLite                      | Store last 5 uploaded datasets        |
| Version Control   | Git & GitHub                | Collaboration & submission            |

## Key Features

-   **CSV Upload:** Upload CSV files via both web and desktop applications.
-   **Data Summary API:** Backend API provides total counts, averages, and equipment type distribution.
-   **Visualization:** Interactive charts using Chart.js (Web) and Matplotlib (Desktop).
-   **History Management:** Stores and displays the last 5 uploaded datasets.
-   **PDF Report Generation:** Create PDF reports of the analyzed data.
-   **User Authentication:** Basic user login and registration.

## Setup Instructions

Follow these steps to set up and run the application locally.

### Prerequisites

-   Python 3.8+
-   Node.js and npm (or yarn)

### 1. Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd e:\Hybrid app(fossee)\backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser (optional, for Django admin access):**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the Django development server:**
    ```bash
    python manage.py runserver
    ```
    The backend will be accessible at `http://127.0.0.1:8000/`.

### 2. Web Frontend Setup

1.  **Open a new terminal and navigate to the web frontend directory:**
    ```bash
    cd e:\Hybrid app(fossee)\frontend
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    # or
    yarn install
    ```

3.  **Start the React development server:**
    ```bash
    npm start
    # or
    yarn start
    ```
    The web application will open in your browser, usually at `http://localhost:3000/`.

### 3. Desktop Frontend Setup

1.  **Open a new terminal and navigate to the desktop application directory:**
    ```bash
    cd e:\Hybrid app(fossee)\desktop_app
    ```

2.  **Ensure Python dependencies are installed (from backend setup):**
    If you haven't already, activate the virtual environment from the backend setup and install `PyQt5` and `requests` if they are not already installed:
    ```bash
    cd e:\Hybrid app(fossee)\backend
    .venv\Scripts\activate
    pip install PyQt5 requests
    ```
    Then navigate back to the desktop app directory:
    ```bash
    cd e:\Hybrid app(fossee)\desktop_app
    ```

3.  **Run the desktop application:**
    ```bash
    python main.py
    ```
    The desktop application window should appear.

## Usage

-   **Register/Login:** Create an account or log in using the provided authentication forms.
-   **Upload CSV:** Use the upload functionality in either the web or desktop app to submit your chemical equipment data.
-   **View Data:** Explore the data summaries, tables, and charts.
-   **History:** Access your upload history to revisit previous datasets.
-   **Generate PDF:** Create a PDF report of your analysis.
