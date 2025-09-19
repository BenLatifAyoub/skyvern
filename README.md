# Skyvern

<!-- Badges: A great way to show the status of your project. You can generate these from services like shields.io -->
<!-- Replace `<your-username>/<your-repo>` with your actual GitHub username and repository name -->
<p align="center">
  <img src="https://img.shields.io/badge/python-3.12-blue.svg" alt="Python 3.12">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <a href="https://github.com/<your-username>/<your-repo>/actions">
    <img src="https://github.com/<your-username>/<your-repo>/actions/workflows/ci.yml/badge.svg" alt="CI Status">
  </a>
</p>

<!-- Project Logo or GIF: A visual representation of your project can be very effective. -->
<!-- Replace the src URL with a link to your own logo or a GIF demonstrating the project -->
<p align="center">
  <img src="https://via.placeholder.com/600x300.png?text=Skyvern+Project+Demo" alt="Skyvern Demo">
</p>

A brief but compelling description of what Skyvern does, who it's for, and the main problem it solves. This should be your "elevator pitch" to potential users and contributors.

---

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have the following installed on your system:

*   **Python 3.12:** [Download Python](https://www.python.org/downloads/)
*   **PostgreSQL:** A running instance of a PostgreSQL database.
*   **Docker & Docker Compose:** For running the application in a containerized environment. [Install Docker](https://docs.docker.com/get-docker/)
*   **LLM API Key:** An API key from a provider like OpenAI, Anthropic, etc.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/BenLatifAyoub/skyvern.git
    cd skyvern
    ```

2.  **Install dependencies:**
    It's recommended to use a virtual environment to avoid conflicts with other projects.
    ```bash
    # Create a virtual environment
    python -m venv venv
    
    # Activate the virtual environment
    # On macOS/Linux:
    source venv/bin/activate
    # On Windows:
    # venv\Scripts\activate
    
    # Install the required packages
    pip install -r requirements.txt
    ```

3.  **Initialize Skyvern:**
    This script will guide you through the initial configuration.
    ```bash
    python fix_init.py init
    ```
    You will be prompted to:
    *   Choose `Local` for the environment.
    *   Set up the PostgreSQL database.
    *   Enter your LLM API key.

    > **Note:** If you prefer manual setup, you can copy `.env.example` to `.env` and update the database credentials and API keys there.

---

## 🐳 Running with Docker

Once the installation and initialization are complete, you can start the Skyvern server using Docker Compose.

1.  **Build and start the services:**
    The `-d` flag runs the containers in detached (background) mode.
    ```bash
    docker compose up -d --build
    ```

2.  **Verify the server is running:**
    You can check the logs to ensure everything started correctly. First, find the container ID.
    ```bash
    docker ps
    ```
    Then, view its logs.
    ```bash
    docker logs <container_id>
    ```

---

## 🧪 Running the Test Script

To confirm that Skyvern is functioning as expected, run the provided test script. This will execute a sample workflow to validate your setup.

```bash
python test.py