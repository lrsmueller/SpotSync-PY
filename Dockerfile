FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /

COPY requirements.txt /
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY /app /app

# DEBUG BUILD
FROM builder AS debug

RUN <<EOF
apk update
apk add git
EOF

RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF
# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8000", "--debug"]

# PRODUCTION BUILD
FROM builder AS production

RUN pip3 install gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0" ,"app:create_app()"]

#TODO TESTING BUILD