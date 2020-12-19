FROM lambgeo/lambda-gdal:3.2-al2 as gdal

# We use lambci docker image for the runtime
FROM lambci/lambda:build-python3.8

# Bring C libs from lambgeo/lambda-gdal image
COPY --from=gdal /opt/lib/ /opt/lib/
COPY --from=gdal /opt/include/ /opt/include/
COPY --from=gdal /opt/share/ /opt/share/
COPY --from=gdal /opt/bin/ /opt/bin/
ENV \
  GDAL_DATA=/opt/share/gdal \
  PROJ_LIB=/opt/share/proj \
  GDAL_CONFIG=/opt/bin/gdal-config \
  GEOS_CONFIG=/opt/bin/geos-config \
  PATH=/opt/bin:$PATH

# Set some useful env
ENV \
  LANG=en_US.UTF-8 \
  LC_ALL=en_US.UTF-8 \
  CFLAGS="--std=c99"

ENV PACKAGE_PREFIX=/var/task

# Copy any local files to the package
COPY . ${PACKAGE_PREFIX}/

RUN pip install -r requirements.txt

RUN ["python3", "package.py" ]

# Move some files around
RUN cp -r /var/lang/lib/python3.8/site-packages/* ${PACKAGE_PREFIX}/
RUN rm -rf /var/lang/lib/

# Create package.zip
RUN cd $PACKAGE_PREFIX && zip -r9q /tmp/package.zip *
