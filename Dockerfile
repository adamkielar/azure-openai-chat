###########
# BUILDER #
###########
FROM python:3.11-slim-bullseye as builder

RUN apt-get -y update --allow-releaseinfo-change && apt-get install -y build-essential g++ unixodbc-dev gnupg curl && \
    apt-get clean

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./app/requirements.txt .

RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #
#########
FROM python:3.11-slim-bullseye

RUN mkdir -p /home/app

RUN addgroup --system app && adduser --system --group app

ENV HOME=/home/app
WORKDIR $HOME

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update --allow-releaseinfo-change && apt-get install -y build-essential g++ unixodbc-dev gnupg curl && \
    apt-get clean

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

COPY ./app ./app

RUN chown -R app:app $HOME

USER app

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--theme.primaryColor=#4F318D", "--theme.backgroundColor=#4F318D", "--theme.base=dark", "--client.toolbarMode=minimal"]