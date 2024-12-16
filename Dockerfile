FROM python:3.12.8-slim-bullseye

WORKDIR /PyAirLink

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

EXPOSE 10103

CMD ["/bin/bash", "start.sh"]
