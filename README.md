
Demonstration : 
![sl3_final_bookstore](https://github.com/user-attachments/assets/5622946f-1f0f-4789-a3fa-ce8805fd4912)


# Bookstore Management System (Django Assignment 1)

## Project Overview

A simple web application built with Django for managing a bookstore. Users can browse books, view details, register, login/logout, and add books to a session-based shopping cart. A custom admin panel allows staff users to add, edit, and delete books from the inventory.

This project adheres to specific constraints, including using only Class-Based Views and manual HTML forms (no Django Forms or built-in Admin for book management).

## Tech Stack Used

*   **Backend:** Python, Django
*   **Frontend:** HTML, CSS, Bootstrap 5 (via CDN)
*   **Database:** SQLite (default for development)
*   **DevOps:** Docker, Docker Compose, Jenkins (configuration included)
*   **Version Control:** Git, GitHub

## Setup & Run Instructions

### Prerequisites

*   Python 3.8+
*   Pip (Python package installer)
*   Git
*   Docker & Docker Compose (Recommended)
*   Jenkins (Optional, for CI/CD pipeline)

### Option 1: Running with Docker Compose (Recommended)

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd bookstore-project # Or your repo name
    ```
2.  **Create Environment File:**
    Create a `.env.dev` file in the root directory (copy from `.env.example` if provided, or create manually):
    ```dotenv
    SECRET_KEY=your_strong_random_secret_key
    DEBUG=True
    ```
    *(Ensure `.env.dev` is in your `.gitignore`)*
3.  **Build and Run:**
    ```bash
    docker-compose up --build -d
    ```
    The `--build` flag ensures the image is built. `-d` runs it in detached mode.
4.  **Apply Migrations (First time or after model changes):**
    Run migrations inside the running container:
    ```bash
    docker-compose exec web python manage.py migrate
    ```
5.  **Create Superuser (for Admin Panel Access):**
    Run this command inside the container:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```
    Follow the prompts to create an admin user.
6.  **Access the Application:**
    Open your web browser and navigate to `http://localhost:8000` or `http://127.0.0.1:8000`.
    Access the custom admin panel at `http://localhost:8000/manage/books/` (login with your superuser).

### Option 2: Running Locally without Docker

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd bookstore-project # Or your repo name
    ```
2.  **Create Virtual Environment:**
    ```bash
    python -m venv venv
    # Activate:
    # Windows: .\venv\Scripts\activate
    # macOS/Linux: source venv/bin/activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Apply Migrations:**
    ```bash
    python manage.py migrate
    ```
5.  **Create Superuser:**
    ```bash
    python manage.py createsuperuser
    ```
6.  **Run the Development Server:**
    ```bash
    python manage.py runserver
    ```
7.  **Access the Application:**
    Open your web browser and navigate to `http://127.0.0.1:8000`.
    Access the custom admin panel at `http://127.0.0.1:8000/manage/books/`.

## Screenshots

*(Insert screenshots of key pages here if available/required)*

*   Home Page
*   Book List
*   Book Detail
*   Shopping Cart
*   Login Page
*   Registration Page
*   Custom Admin Book List

## Docker and Jenkins Usage Notes

*   **Docker:** The `Dockerfile` sets up the Python environment and copies the application code. `docker-compose.yml` defines the `web` service to run the Django application and manages a volume for the SQLite database persistence. Environment variables like `SECRET_KEY` and `DEBUG` can be managed via the `.env.dev` file for local development.
*   **Jenkins:** The `Jenkinsfile` provides a basic declarative pipeline structure for CI/CD. It includes placeholder stages for Checkout, Build (using Docker Compose), Test (requires test implementation), and Deploy (requires specific deployment scripts/configuration). You will need to configure Jenkins with appropriate plugins (Docker, Pipeline, Git, SSH Agent if needed) and potentially set up credentials for Docker Hub or deployment targets. Run tests using `docker-compose run --rm web python manage.py test bookstore` (after writing tests).

---
