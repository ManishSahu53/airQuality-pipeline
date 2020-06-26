import os
import datetime
import wget
import logging

import config

from src import util


class SilamDataset:
    """
    This class is used to download dataset
    """
    def __init__(self):
        self.path_base = 'http://s3-eu-west-1.amazonaws.com/fmi-opendata-silam-surface-netcdf/global'
        self.base_date = datetime.datetime.strptime('2000-01-01', '%Y-%m-%d')
        self.paramter =  ['CO', 'NO2', 'NO', 'O3', 'PM10', 'PM25', 'SO2', 'airdens']
        self.forecast_day = [0, 1, 2, 3, 4]

    def _date_to_silam_path(self, day_interval, parameter='CO', forecast_day=0):
        """
            day_interval = 20 , Number of days after 2000-01-01
            parameter = ['CO', 'NO2', 'NO', 'O3', 'PM10', 'PM25', 'SO2', 'airdens']
            day = [0, 1, 2, 3, 4]

            return  silam_glob_v5_6_20200523_CO_d0.nc
        """
        if parameter not in self.paramter:
            raise Exception('Invalid paramter passed: {}, possible paramters: {}'.format(parameter, self.paramter))
        
        if forecast_day not in self.forecast_day:
            raise Exception('Invalid forecast_day passed: {}, possible forecast_day: {}'.format(forecast_day, self.forecast_day)) from None

        date = self.base_date + datetime.timedelta(days = day_interval)
        year = date.year
        month = '{}{}'.format(0, date.month) if date.month <10 else '{}'.format(date.month)
        day = '{}{}'.format(0, date.day) if date.day <10 else '{}'.format(date.day)

        date = '{}{}{}'.format(year, month, day)

        suffix = 'd{}'.format(forecast_day)
        prefix = 'silam_glob_v5_6_{}_{}_{}.nc'.format(date, parameter, suffix)
        
        s3_path = os.path.join(self.path_base, date, prefix)
        return s3_path

    def download(self, path_output, path_forecast, start_date='2020-05-01', end_date='2020-05-10', parameter_list=['PM25'], forecast_day_list = [0, 1, 2, 3, 4]):

        assert type(parameter_list) == list,  'parameter_list should be of "list" type, given: {}'.format(type(parameter_list))
        assert type(forecast_day_list) == list,  'forecast_day_list should be of "list" type, given: {}'.format(type(forecast_day_list))

        for parameter in parameter_list:
            if parameter not in self.paramter:
                raise('Invalid paramter passed: {}, possible paramters: {}'.format(parameter, self.paramter))
        
        for forecast_day in forecast_day_list:
            if forecast_day not in self.forecast_day:
                raise('Invalid forecast_day passed: {}, possible forecast_day: {}'.format(forecast_day, self.forecast_day))


        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        # Number of days after 2000-01-01
        start_day = (start_date - self.base_date).days
        end_day = (end_date - self.base_date).days

        # Since we want to include last day also
        for day_interval in range(start_day, end_day + 1):
            temp_date = self.base_date + datetime.timedelta(days = day_interval)
            temp_year = temp_date.year
            temp_month = temp_date.month
            temp_day = temp_date.day

            temp_path_output = os.path.join(path_output, str(temp_year), str(temp_month), str(temp_day))
            temp_path_forecast = os.path.join(path_forecast, str(temp_year), str(temp_month), str(temp_day))

            util.check_dir(temp_path_output)
            util.check_dir(temp_path_forecast)

            for parameter in parameter_list:
                for forecast_day in forecast_day_list:
                    path_file = self._date_to_silam_path(day_interval, parameter=parameter, forecast_day=forecast_day)

                    if forecast_day == 0:
                        _temp_path_output = os.path.join(temp_path_output, os.path.basename(path_file))
                    else:
                        _temp_path_output = os.path.join(temp_path_forecast, os.path.basename(path_file))

                    logging.info('Downloading {}'.format(path_file))
                    if os.path.isfile(_temp_path_output):
                        logging.warning('File NC already present. So Skipping!')
                        continue
                    
                    if os.path.isfile(util.get_file_name(_temp_path_output) + '.tif'):
                        logging.warning('File TIF already present. So Skipping!')
                        continue

                    try:    
                        wget.download(path_file, _temp_path_output)
                    except Exception as e:
                        logging.warning('Unable to download data. Error: {}'.format(e))
                        continue




