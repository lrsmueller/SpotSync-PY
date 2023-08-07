# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-alpine

LABEL org.opencontainers.image.description "Add your last 100 liked songs on Spotify to a playlist"

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URI=sqlite:////data/project.db \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install pip requirements and copy app
WORKDIR /
COPY /app /app
COPY requirements.txt .

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN python -OO -m pip install --no-cache-dir -r requirements.txt --only-binary=:all: && \
    mkdir /data && \ 
    adduser -u 5678 --disabled-password --gecos "" appuser && \
    chown -R appuser /app /data
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:create_app()"]
