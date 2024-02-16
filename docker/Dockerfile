FROM python:3.10-alpine as builder
#ENV PYTHONDONTWRITEBYTECODE=1
#ENV PYTHONUNBUFFERED=1

WORKDIR /app/

RUN apk --update --no-cache add binutils

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir kafka-python paho-mqtt pyinstaller pytz

COPY wenglor_to_kafka_producer.py /app/

RUN pyinstaller --onefile wenglor_to_kafka_producer.py

FROM alpine

WORKDIR /app

RUN addgroup --system --gid 1001 appuser
RUN adduser --system --uid 1001 appuser

COPY --from=builder --chown=appuser:appuser /app/dist/wenglor_to_kafka_producer /app/wenglor_to_kafka_producer

USER appuser

ENTRYPOINT ["./wenglor_to_kafka_producer"]