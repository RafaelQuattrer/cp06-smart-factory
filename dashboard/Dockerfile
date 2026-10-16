FROM python:3.12.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home appuser
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser templates ./templates
COPY --chown=appuser:appuser static ./static
USER appuser
EXPOSE 5001
CMD ["python", "app.py"]
