FROM bitnami/python:3.9.5-prod

# Don't use cached python packages
ENV PIP_NO_CACHE_DIR 1

# Installing Required Packages
RUN apt update && apt upgrade -y && \
    apt install --no-install-recommends -y \
    bash \
    python3-dev \
    python3-lxml \
    make

# Make image lighter
RUN rm -rf /var/lib/apt/lists /var/cache/apt/archives /tmp

# Enter Workplace
WORKDIR /app/

# Copy folder
COPY . .

# Install dependencies
RUN pip3 install --upgrade pip
RUN rm -r /opt/bitnami/python/lib/python3.9/site-packages/setuptools*
RUN pip3 install --upgrade setuptools

# Install poetry
RUN pip3 install --upgrade poetry==1.1.6

# Disable poetry virtualenv
RUN poetry config virtualenvs.create false

# Install requirements without dev requirements and without interaction
RUN poetry install --no-dev --no-interaction
