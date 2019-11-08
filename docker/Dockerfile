FROM brunneis/python:3.7
ADD easymongo.tar /
WORKDIR easymongo
RUN pip install -r requirements.txt && python setup.py install
