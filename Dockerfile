FROM python:3.10-slim

# Set working directory
WORKDIR /allycat

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 


# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    curl \
    git \
    netcat-traditional \
    procps \
    wget \
    tree  \
    vim \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Neo4j
RUN curl -fsSL https://debian.neo4j.com/neotechnology.gpg.key | gpg --dearmor -o /usr/share/keyrings/neo4j.gpg \
    && echo 'deb [signed-by=/usr/share/keyrings/neo4j.gpg] https://debian.neo4j.com stable latest' | tee /etc/apt/sources.list.d/neo4j.list \
    && apt-get update \
    && apt-get install -y neo4j=5.15.0 \
    && rm -rf /var/lib/apt/lists/*

# Set up Neo4j configuration
RUN sed -i 's/#dbms.security.auth_enabled=false/dbms.security.auth_enabled=true/' /etc/neo4j/neo4j.conf \
    && sed -i 's/#dbms.default_listen_address=0.0.0.0/dbms.default_listen_address=0.0.0.0/' /etc/neo4j/neo4j.conf

# Copy requirements file
COPY requirements-docker.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-docker.txt


## Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy project files
COPY . .
RUN chmod +x ./docker-startup.sh

# Create a non-root user and switch to it
# RUN adduser --disabled-password --gecos '' appuser
# RUN chown -R appuser:appuser /app  
# USER appuser

# Expose the port for webapp
EXPOSE 8080  
# Expose the port for Ollama
EXPOSE 11434

# Expose ports for Neo4j
EXPOSE 7474  # Neo4j HTTP
EXPOSE 7687  # Neo4j Bolt

# CMD ["python", "app.py"]
# CMD ["./docker-startup.sh"]
ENTRYPOINT ["./docker-startup.sh"]
