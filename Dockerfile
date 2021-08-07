FROM python:3.9-alpine

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

COPY . .

RUN python -m pip install --upgrade pip &&\
    pip install -r requirements.txt

# make database migrations
RUN make migrations

EXPOSE 80 432 8080

CMD [ "python", "server.py" ]




