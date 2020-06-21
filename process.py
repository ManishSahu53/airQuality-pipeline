import os
import logging

from src import util
from src import download
from src import converter
import config

# Logging training
util.set_logger(os.path.join(config.path_logs, 'process.log'))
logging.info('################## Starting Data ####################')
path_output = 'data'

# Download data
data = download.SilamDataset()
data.download(path_output=path_output, 
              start_date='2020-05-22', 
              end_date='2020-06-10', 
              parameter_list=['CO', 'NO2', 'NO', 'O3', 'PM10', 'PM25', 'SO2'], 
              forecast_day_list = [0, 1, 2, 3, 4]
              )

# Convertng nc to cog tif
nc_to_cog = converter.ProcessingNC()
path_data = util.list_list(path=path_output, extension='nc')


for i, d in enumerate(path_data):
    logging.info('Procesing {}, {} out of {}'.format(os.path.basename(d), i, len(path_data)))
    temp_path_tif = os.path.join(os.path.dirname(d), util.get_file_name(d) + '.tif')
    nc_to_cog.convert_to_cog(d, temp_path_tif)
    
    logging.info('Conversion completed, deleteing NC file')
    os.remove(d)