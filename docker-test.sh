#!/bin/bash

# This script, while completely optional, will build and run this project entirely in [Docker](https://www.docker.com/).

set -e
docker build .
docker run --rm -it -p 9876:9876 $(docker build -q .)
