# Task Tracker API - container image
FROM python:3.12-slim

WORKDIR /app

# Install runtime-only dependencies (no pytest/httpx test tooling) so this
# layer is cached unless requirements-docker.txt changes.
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy only the backend application code. Frontend, tests, and docs are not
# needed to run the API in production and are excluded via .dockerignore.
COPY app/ ./app/

# Run as a non-root user rather than the default root user inside the image.
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8000

# No .env file, secrets, or credentials are copied into the image (see
# .dockerignore). Configuration should be supplied at runtime via
# environment variables (e.g. `docker run -e KEY=value ...`) if the app
# is extended to need any in the future.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
