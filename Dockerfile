FROM python:3.11-slim

RUN useradd -m -u 1000 user

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN chown -R 1000:1000 /app
USER user
ENV PATH="/home/user/.local/bin:$PATH"

EXPOSE 7860

CMD ["python", "-m", "streamlit", "run", "app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0"]