FROM nginx:latest

RUN mkdir "cert"
COPY localhost.crt cert/localhost.crt
COPY localhost.key cert/localhost.key

CMD ["nginx", "-g", "daemon off;"]