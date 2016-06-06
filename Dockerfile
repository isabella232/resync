# Dockerfile
#
# Build the Resydes application.
#
FROM python:3

MAINTAINER henk.van.den.berg at dans.knaw.nl

LABEL description="ehribranch of the resync library" \
    origin="https://github.com/resync/resync" \
    this_version="https://github.com/EHRI/resync/releases/tag/v1.0.1"

COPY resync /resync/resync/
COPY setup.py /resync/

RUN pip install /resync

RUN rm -R resync