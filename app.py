import json
import os
import boto3
import datetime

from src import util
from src import converter

import config


s3 = boto3.client('s3')
path_temp = 'tmp'

bucket_output = 'silam-air-quality'
path_output_s3 = 'geotif'

def silam_air_quality_process(event, context):
    print('Triggered Lambda function')

    msg = event['Records'][0]['Sns']['Message']
    # msg = json.loads(msg)

    to_s3 = msg['Records'][0]['s3']
    bucket_input = to_s3['bucket']['name']
    key_input = to_s3['object']['key']
    size = to_s3['object']['size']

    timestamp = msg['Records'][0]['eventTime']
    eventName = msg['Records'][0]['eventName']
    print('eventName: {}'.format(eventName))

    if eventName != "ObjectCreated:Put":
        response = {
            "statusCode": 200,
            "body": "EvenName ObjectCreated:Put not found. Found: {}".format(eventName)
        }
        return response
    
    else:
        path_data = os.path.join(path_temp, util.get_file_name(key_input))
        temp_path_tif = path_data + '.tif'

        print('Dowloading data from s3 bucket: {}, key: {} to local :{}'.format(bucket_input, key_input, path_data))
        s3.download_file(bucket_input, key_input, path_data)

        # Parsing timestamp and dates
        timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
    
        date_name = str(timestamp.date().year) + str(timestamp.date().month) + str(timestamp.date().day)       
        """
            Spliting with date(20201118) because v5_7 can change anytime
            silam_glob_v5_7_1_20201118_CO_d0.nc 
         """
        split_name = date_name + '_'
        pollutant_name = key_input.split(split_name)[1]
        pollutant_name = util.get_file_name(pollutant_name)
        
        print('Pollutant name: {}'.format(pollutant_name))
        path_output_key = os.path.join('global', date_name, pollutant_name + '.tif')

        # Convertng nc to cog tif
        print('Converting to COG')
        nc_to_cog = converter.ProcessingNC()
        nc_to_cog.convert_to_cog(path_data, temp_path_tif)

        # Upload file to S3
        temp_key_output = os.path.join(path_output_s3, path_output_key)
        print('Uploading COG to s3 bucket: {}, key: {}'.format(bucket_output, temp_key_output))
        util.upload_file(temp_path_tif, bucket=bucket_output, object_name=temp_key_output)

        response = {
            "statusCode": 200,
            "body": json.dumps({
                "remark": 'completed successfully',
                "key": temp_key_output,
                "bucket": bucket_output,
                "timestamp": date_name
            })
        }

        return response
"""
temp_date = str(datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ').date())
"""

path_json = 'notebook/silam.json'
event = util.load_json(path_json)
silam_air_quality_process(event, '')