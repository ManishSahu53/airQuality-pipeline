import site
import gdal
import os

path = os.path.abspath(gdal.__file__)
print(site.getsitepackages())
print(path)