FROM rocker/shiny-verse:latest

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# Copy files from S3 inside docker
RUN aws s3 cp s3://${MY_S3_BUCKET} /datasets/google_training_data

COPY app.r app.r ./

EXPOSE 8888
CMD ["/usr/bin/shiny-server.sh"]
