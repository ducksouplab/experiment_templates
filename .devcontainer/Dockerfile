FROM node:current-slim

RUN apt-get update && apt-get upgrade -y

RUN apt-get update && apt-get install -y python3-pip git
RUN apt-get update && apt-get install -y libpq-dev
RUN apt-get update && apt-get install -y python3-venv
# RUN python3 -m venv .venv
# RUN source .venv/bin/activate

ENV VIRTUAL_ENV=/workspaces/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip3 install -U python-dotenv