#!/bin/bash

# Debugging output to log the commands and their results
set -x  # Enables command tracing

# Install necessary utilities
apt-get update
apt-get install -y curl wget

# Download and install Tesseract binary
TESSERACT_VERSION="5.0.0-alpha.20210811"
wget https://github.com/tesseract-ocr/tesseract/releases/download/$TESSERACT_VERSION/tesseract-$TESSERACT_VERSION-linux-x86_64.tar.gz
tar -xzvf tesseract-$TESSERACT_VERSION-linux-x86_64.tar.gz
cd tesseract-$TESSERACT_VERSION
make
make install

# Verify the installation
tesseract --version
