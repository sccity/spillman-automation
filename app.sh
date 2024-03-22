#!/bin/bash

docker_compose="docker-compose -f docker-compose.yaml"

if [[ $1 = "start" ]]; then
  echo "Starting Spillman Automation..."
	$docker_compose up -d
elif [[ $1 = "stop" ]]; then
	echo "Stopping Spillman Automation..."
	$docker_compose stop
elif [[ $1 = "restart" ]]; then
	echo "Restarting Spillman Automation..."
  $docker_compose down
  $docker_compose start
elif [[ $1 = "down" ]]; then
	echo "Tearing Down Spillman Automation..."
	$docker_compose down
elif [[ $1 = "rebuild" ]]; then
	echo "Rebuilding Spillman Automation..."
	$docker_compose down --remove-orphans
	$docker_compose build --no-cache
elif [[ $1 = "update" ]]; then
	echo "Updating Spillman Automation..."
	$docker_compose down --remove-orphans
	git pull origin prod
elif [[ $1 = "shell" ]]; then
	echo "Entering Spillman Automation Shell..."
	docker exec -it spillman-automation bash
else
	echo "Unkown or missing command..."
fi