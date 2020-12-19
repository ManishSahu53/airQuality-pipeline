# import joblib
import os
import json
from osgeo import gdal
import numpy as np

import logging
import boto3
from botocore.exceptions import ClientError


# Loading model
def load_model(path_model):
    model = joblib.load(path_model)
    return model


# Saving model
def save_model(model, path_output):
    """Saving any model to PKL file
    Args:
        model: (object)
        path_output: (string) path of output
    """

    joblib.dump(model, path_output)
    print('Model saved to %s' % (path_output))


# check directory if exist else create directory
def check_dir(path_output):
    """Checking directory and creating
    folder if doesn't exist
    Args:
        path_output: (string) directory
    """
    if not os.path.exists(path_output):
        os.makedirs(path_output)


# Loading json
def load_json(path_model):
    """Loads json object to dict
    Args:
        path_model: (string) path of input
    """
    with open(path_model) as f:
        data = json.load(f)
    return data


# Saving json
def save_json(model, path_output):
    """Saves dictionary to json object.
    
    Args:
        model: (Dict object)
        path_output: (string) path of output
    """
    # Saving keyword and keyword atc
    with open(path_output, 'w') as f:
        json.dump(model, f)


# Saving vocab to txt file
def save_vocab_to_txt_file(vocab, txt_path):
    """Writes one token per line, 0-based line id corresponds to
    the id f the token.
    Args:
        vocab: (iterable object) yields token
        txt_path: (string) path to vocab file
    """
    with open(txt_path, 'w') as f:
        for token in vocab:
            f.write(str(token) + '\n')


# Loading txt as list
def load_txt(path_txt):
    with open(path_txt, encoding='utf-8') as f:
        vocab = f.read().splitlines()
    return vocab


# Setting logging
def set_logger(path_log):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Logging to a file
        file_handler = logging.FileHandler(path_log)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s : %(levelname)s : %(message)s'))
        logger.addHandler(file_handler)

        # Logging to console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(stream_handler)


# Get list of files inside this folder
def list_list(path, extension):
    path_data = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                path_data.append(os.path.join(root, file))

    return path_data


# get file name
def get_file_name(path_data):
    return os.path.splitext(os.path.basename(path_data))[0]


# Upload file to S3
def upload_file(file_name, bucket, object_name):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True




# Reading raster dataset
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
def write_tif(path_tif, array, geotransform, geoprojection, size):
    dim_array = array.shape
    if len(dim_array) > 2:
        depth = dim_array[2]
    else:
        depth = 1

    driver = gdal.GetDriverByName("GTiff")
    outdata = driver.Create(
        path_tif, size[0], size[1], depth, gdal.GDT_Float32)

    # sets same geotransform as input
    outdata.SetGeoTransform(geotransform)
    outdata.SetProjection(geoprojection)  # sets same projection as input
    for i in range(depth):
        try:
            arr = array[:, :, i]
        except Exception as e:
            arr = array[:, :]
        arr = cv2.resize(arr, size)
        outdata.GetRasterBand(i+1).WriteArray(arr)
    # outdata.GetRasterBand(1).SetNoDataValue(-9999)##if you want ... \
    # ...\ these values transparent
    outdata.FlushCache()  # saves to disk!!

