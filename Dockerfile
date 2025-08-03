FROM python:3.11-slim

WORKDIR /opt/render/project/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p Data

EXPOSE 10000

CMD ["python", "app.py"]