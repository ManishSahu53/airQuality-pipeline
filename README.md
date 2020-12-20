# AirQuality_pipeline
This repo is used to Processing Daily AirQuality data

## Layers
There are 2 layers whic are to be added
1. >arn:aws:lambda:us-east-1:552188055668:layer:geolambda:4
2. >arn:aws:lambda:us-east-1:552188055668:layer:geolambda-python:3

## How to deploy
0. Use python 3.7 with geolambda4 layer only, 3.6 and 3.8 doesn't work
1. Create Zip using Docker
    * `docker build -t silam .`
    * `docker run --name lambda -w /var/task -itd silam:latest bash`
    * Check the ID of container
    * `docker cp lambda:/tmp/package.zip notebook/silam-package.zip`
    * Finally upload zip to S3
    * `aws s3 cp notebook/silam-package.zip s3://temp-test-gdal-bucket`

2. Manually add cogconverter, wget library to the package
