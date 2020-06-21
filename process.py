import os

from src import util
from src import download
import config

# Logging training
util.set_logger(os.path.join(config.path_logs, 'process.log'))

data = download.SilamDataset()

path_output = 'data'
data.download(path_output=path_output, 
              start_date='2020-05-20', 
              end_date='2020-06-10', 
              parameter_list=['PM25', 'PM10'], 
              forecast_day_list = [0, 1, 2, 3, 4]
              )