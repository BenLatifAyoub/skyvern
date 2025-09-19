# Skyvern Project Setup Instructions

# Prerequisites
# - Python 3.12
# - PostgreSQL
# - Docker & Docker Compose
# - LLM API key (OpenAI, Anthropic, etc.)

# Step 1: Clone the repository
RUN git clone <your-repo-url> && cd <your-repo-folder>

# Step 2: Install dependencies
RUN pip install -r requirements.txt

# Step 3: Initialize Skyvern (Windows example)
RUN python fix_init.py init
# - Choose Local
# - Create PostgreSQL database
# - Provide your LLM API key

# Step 4: Start Skyvern server with Docker
RUN docker compose up -d --build

# Step 5: Run the test script
RUN python test.py
# (This executes the second method described in the provided email)

# Notes:
# - Ensure PostgreSQL is running and accessible
# - Update .env with API keys and DB credentials if needed
# - Check Docker logs for troubleshooting: docker logs <container_id>
