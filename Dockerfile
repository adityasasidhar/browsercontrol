# Container image for running BrowserControl (also used by Glama's build check).
# Streamable HTTP on port 8000 by default; override with CMD or BROWSER_* variables.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    BROWSER_HEADLESS=true \
    BROWSER_USER_DATA_DIR=/data/user_data

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY browsercontrol ./browsercontrol

# Playwright's bundled Node needs libatomic1, which slim images lack; without it
# `playwright install` exits 127 ("libatomic.so.1: cannot open shared object file").
RUN apt-get update \
    && apt-get install -y --no-install-recommends libatomic1 \
    && pip install . \
    && playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /data

VOLUME /data
EXPOSE 8000

ENTRYPOINT ["browsercontrol"]
CMD ["--transport", "http", "--host", "0.0.0.0", "--port", "8000"]
