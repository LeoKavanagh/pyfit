FROM ubuntu:16.04

RUN useradd -ms /bin/bash pyfit

# R pre-requisites
RUN apt-get update && \
    apt-get install -y \
    python3-pip python3-dev python3-venv \
    r-base-core \
    fonts-dejavu \
    tzdata \
    apt-utils \
    gfortran \
    gcc && \
rm -rf /var/lib/apt/lists/*

# Install an R package (this may not work)
RUN R -e "install.packages('tidyverse', repos='https://ftp.heanet.ie/mirrors/cran.r-project.org/')"

WORKDIR /home/pyfit

COPY requirements.txt requirements.txt
RUN /usr/bin/python3 -m venv venv
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
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN chmod +x boot.sh


RUN chown -R pyfit:pyfit ./
USER pyfit

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
