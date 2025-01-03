FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /user/src/app
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
RUN playwright install chromium --with-deps
