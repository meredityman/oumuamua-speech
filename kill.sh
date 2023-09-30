#!/bin/bash

docker  kill $(docker ps -q) > /dev/null 2>&1
