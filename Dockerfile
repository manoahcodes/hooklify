# syntax=docker/dockerfile:1.4

# --- Base Python image ---
    ARG PYTHON_VERSION=3.13.0
    FROM python:${PYTHON_VERSION}-slim
    
    # --- Virtual Environment Setup ---
    ENV VIRTUAL_ENV=/opt/venv
    RUN python -m venv $VIRTUAL_ENV
    ENV PATH="$VIRTUAL_ENV/bin:$PATH"
    
    # --- Python Environment Settings ---
    ENV PYTHONDONTWRITEBYTECODE=1
    ENV PYTHONUNBUFFERED=1
    
    # --- System Dependencies ---
    RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        libjpeg-dev \
        libcairo2 \
        gcc \
        && apt-get clean && rm -rf /var/lib/apt/lists/*
    
    # --- Create app directory ---
    WORKDIR /code
    
    # --- Install Python Requirements ---
    COPY requirements.txt .
    RUN pip install --upgrade pip \
        && pip install -r requirements.txt
    
    # --- Copy Application Code ---
    COPY ./src /code
    
    # --- Django Settings from Build ARGs ---
    ARG DJANGO_SECRET_KEY
    ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
    
    ARG DJANGO_DEBUG=0
    ENV DJANGO_DEBUG=${DJANGO_DEBUG}
    
    # --- App Specific Settings ---
    ARG PROJ_NAME="backend"
    ENV PROJ_NAME=${PROJ_NAME}
    
    # --- Runtime Entrypoint ---
    COPY ./entrypoint.sh /entrypoint.sh
    RUN chmod +x /entrypoint.sh
    
    # --- Default Command ---
    CMD ["/entrypoint.sh"]    