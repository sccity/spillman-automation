#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

VERSION=$1

docker build --platform linux/x86_64 -t sccity/spillman-automation:$VERSION --push .