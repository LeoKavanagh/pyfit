FROM ubuntu:16.04

RUN adduser -D pyfit

# R pre-requisites
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    fonts-dejavu \
    tzdata \
    gfortran \
    gcc && \
rm -rf /var/lib/apt/lists/*

# Base R
RUN apt-get install r-base-core

# Install an R package (this may not work)
RUN R -e "install.packages('tidyverse')"

WORKDIR /home/pyfit

COPY requirements.txt requirements.txt
RUN python3 -m venv venv
RUN venv/bin/pip install -r requirements.txt

COPY authorise.py authorise.py ./
COPY clean_fitbit_data.r clean_fitbit_data.r ./
COPY clean_google_data.py clean_google_data.py ./
COPY combine_datasets.py combine_datasets.py ./
COPY download_fitbit_data_batch.py download_fitbit_data_batch.py ./
COPY download_fitbit_sleep_data.py download_fitbit_sleep_data.py ./
COPY download_google_data_batch.py download_google_data_batch.py ./
COPY flask_app.py flask_app.py ./
COPY google_fit_utils.py google_fit_utils.py ./
COPY predict.py predict.py ./

COPY boot.sh boot.sh ./
ENV FLASK_APP flask_app.py
RUN chmod +x boot.sh


RUN chown -R pyfit:pyfit ./
USER pyfit

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
