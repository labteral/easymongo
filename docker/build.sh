#!/bin/bash
tar cf /tmp/easymongo.tar ../../
mv /tmp/easymongo.tar .
docker build -t easymongo .
rm -f easymongo.tar
