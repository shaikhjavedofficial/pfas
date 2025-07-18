FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000 8080 80 8000 5001
CMD ["python", "app.py"]