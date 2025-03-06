# build.sh
#!/bin/bash

# Install Tesseract and its dependencies
apt-get update
apt-get install -y tesseract-ocr libtesseract-dev
