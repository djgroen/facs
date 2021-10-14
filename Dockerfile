FROM python:3.9-slim

RUN mkdir -p /FACS_app/facs
ENV PYTHONPATH "${PYTHONPATH}:/FACS_app"


COPY requirements.txt /FACS_app/

RUN apt-get update &&\
    apt-get install -y --no-install-recommends git gcc tree libopenmpi-dev &&\
    pip3 install --no-cache-dir -U pip pip setuptools wheel &&\
    pip3 install --no-cache-dir -r /FACS_app/requirements.txt &&\
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}



COPY facs /FACS_app/facs/
COPY run.py /FACS_app/
COPY validate.py /FACS_app/
COPY validate.py /FACS_app/

RUN mkdir -p /FACS_app/config_files
WORKDIR /FACS_app/config_files

ENTRYPOINT ["python3", "/FACS_app/run.py"]


