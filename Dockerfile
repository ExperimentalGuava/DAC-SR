FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir fastapi uvicorn[standard] pydantic aiohttp httpx pandas numpy
COPY src ./src
EXPOSE 8080
CMD ["uvicorn", "src.io.api:app", "--host", "0.0.0.0", "--port", "8080"]