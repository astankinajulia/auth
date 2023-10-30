FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir "cert"
COPY localhost.crt cert/localhost.crt
COPY localhost.key cert/localhost.key

CMD ["nginx", "-c", "/etc/nginx/nginx.conf", "-g", "daemon off;"]