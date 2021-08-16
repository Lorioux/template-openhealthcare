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


RUN mkdir /usr/src/backend
WORKDIR /usr/src/backend

COPY . .

EXPOSE 80 443 8080

CMD [ "python", "server.py" ]




