FROM python:3.9-alpine as base                                                                                                
                                                                                                                              
FROM base as builder                                                                                                          
                                                                                                                              
RUN mkdir /install                                                                                                            
RUN apk update && apk add --no-cache --virtual .build-deps \
    postgresql-dev \
    g++ \ 
    musl-dev                                                           
WORKDIR /install                                                                                                              
COPY requirements.txt /requirements.txt                                                                                       
RUN pip install --prefix=/install -r /requirements.txt
RUN apk del --no-cache .build-deps

FROM base

COPY --from=builder /install /usr/local
RUN apk --no-cache add libpq
# FROM python:3.9-alpine3.14

RUN mkdir /usr/src/backend
WORKDIR /usr/src/backend

COPY . .

# RUN apk add --no-cache --virtual .build-deps \
#     g++ \
#     musl-dev \
#     postgresql-dev \
#     # && pip install --no-cache-dir psycopg2 \
#     && python -m pip install --upgrade pip \
#     && pip install --no-cache -r requirements.txt \
#     && apk del --no-cache .build-deps

EXPOSE 80 443 8080

CMD [ "python", "server.py" ]




