#!/bin/bash

# Install Tesseract OCR and its dependencies
apt-get update
apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev
