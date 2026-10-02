# syntax=docker/dockerfile:1
# Silente landing page: static site built with Python, served by nginx as an
# unprivileged user on port 8080 (spec §3.3, §8). Versions pinned (rule 4).

FROM python:3.14.8-alpine3.24 AS build
WORKDIR /src
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY VERSION build.py ./
COPY tools/ tools/
COPY src/templates/ src/templates/
COPY src/css/ src/css/
COPY src/img/ src/img/
COPY legal/ legal/
COPY brand/ brand/
COPY fonts/ fonts/
# build.py refuses to build with placeholders or without a date in legal/.
RUN python3 build.py --out /site

FROM nginxinc/nginx-unprivileged:1.30.5-alpine3.24
USER root
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/security-headers.conf /etc/nginx/security-headers.conf
COPY --from=build /site /usr/share/nginx/html
USER 101
EXPOSE 8080
