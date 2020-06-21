import os
import datetime
import wget
import logging
import gdal
import osr
import config

from src import util

import cogconverter as cog


class ProcessingNC:
    def __init__(self):
        self.epsg = 4326
        self.srs = osr.SpatialReference()
        self.srs.ImportFromEPSG(self.epsg)
    
    def convert_to_cog(self, path_nc, path_output):
        ds = gdal.Open(path_nc)

        # Setting projections
        ds.SetProjection(self.srs.ExportToWkt())

        ds = cog.converter.convert2blocksize(ds, path_output)

        # Flusing data to disk
        ds.FlushCache()