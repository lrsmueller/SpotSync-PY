# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-alpine

EXPOSE 8000

# Enviroment Variables
ENV PYTHONDONTWRITEBYTECODE=1 \ 
    PIP_DISABLE_PIP_VERSION_CHECK=1 \ 
    PYTHONUNBUFFERED=1 \
    DATABASE_URI=sqlite:////data/project.db

WORKDIR /

# Install pip requirements
COPY requirements.txt . 
COPY /app /app

RUN python -OO -m pip wheel --no-cache-dir --wheel-dir=/root/wheels -r /requirements.txt && \
    python -OO -m pip install --no-cache --no-index /root/wheels/*

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && mkdir /data && chown -R appuser /app /data && apk update && apk upgrade --no-cache && rm -rf /root/wheels
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:create_app()"]
