FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libmagic1 gettext libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN pip install --upgrade pip \
    && pip install -r requirements/base.txt \
    && if [ -f requirements/development.txt ]; then pip install -r requirements/development.txt; fi

# Cache-bust the code layer per commit. Without this, BuildKit's gha cache can
# serve a stale `COPY . .` layer and ship an image without the latest code
# (this is what made a release image miss its own fix). The git SHA changes
# every commit, so the COPY below (and everything after) is always rebuilt,
# while the heavy apt/pip layers above stay cached.
ARG GIT_SHA=dev
LABEL org.opencontainers.image.revision="${GIT_SHA}"

COPY . .

EXPOSE 8000

CMD ["bash", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60"]
