FROM python:3.9.5-alpine3.13

WORKDIR /usr/src/app

COPY . .

RUN apk add --no-cache postgresql-libs postgresql-dev gcc musl-dev

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./main.py"]
