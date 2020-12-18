import os
import datetime
import wget
import logging
import gdal
import osr
import config
import numpy as np

from src import util

import cogconverter as cog


class ProcessingNC:
    def __init__(self):
        self.epsg = 4326
        self.srs = osr.SpatialReference()
        self.srs.ImportFromEPSG(self.epsg)
        self.geo_transform = (-179.9000030568469,
                              0.2000000101781806,
                              0.0,
                              89.6999984724181,
                              0.0,
                              -0.1999999965940203)

    def convert_to_cog(self, path_nc, path_output):
        ds = gdal.Open(path_nc)

        # Setting projections
        geo_projection = self.srs.ExportToWkt()
        geo_transform = self.geo_transform

        depth = ds.RasterCount
        arr = ds.ReadAsArray()
        arr = np.moveaxis(arr, 0, 2)

        arr = arr[::-1]
        size = arr.shape

        new_ds = self.write_tif(path_output, arr, geo_transform, geo_projection, (size[1], size[0]))

        new_ds = cog.converter.convert2blocksize(new_ds, path_output)

        # Flusing data to disk
        new_ds.FlushCache()


    # Reading raster dataset
    @staticmethod
    def read_tif(path_tif:str):
        """
        Input: TIF image path
        Output: geoTransform, geoProjection, size, arr
        """
        #    array = cv2.imread(tif_file)
        #    driver = gdal.GetDriverByName("GTiff")
        ds = gdal.Open(path_tif)
        num_band = ds.RasterCount
        col = ds.RasterXSize
        row = ds.RasterYSize
        array = np.zeros([row, col, num_band])
        for i in range(num_band):
            band = ds.GetRasterBand(i+1)
            arr = band.ReadAsArray()
            no_data = band.GetNoDataValue()
            arr[arr==no_data] = 0
            array[:, :, i] = arr
        
        size = arr.shape
        geotransform = ds.GetGeoTransform()
        geoprojection = ds.GetProjection()
        return geotransform, geoprojection, (size[1], size[0]), array


    # Writing raster dataset
    @staticmethod
    def write_tif(path_tif, array, geotransform, geoprojection, size):
        dim_array = array.shape
        if len(dim_array) > 2:
            depth = dim_array[2]
        else:
            depth = 1

        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(
            path_tif, size[0], size[1], depth, gdal.GDT_Float32, 
                                               ['NUM_THREADS=ALL_CPUS',
                                                'COMPRESS=LZW'])

        # sets same geotransform as input
        outdata.SetGeoTransform(geotransform)
        outdata.SetProjection(geoprojection)  # sets same projection as input
        for i in range(depth):
            arr = array[:, :, i]
            # arr = cv2.resize(arr, size)
            outdata.GetRasterBand(i+1).WriteArray(arr)
        # outdata.GetRasterBand(1).SetNoDataValue(-9999)##if you want ... \
        # ...\ these values transparent
        # outdata.FlushCache()  # saves to disk!!
        return outdata
