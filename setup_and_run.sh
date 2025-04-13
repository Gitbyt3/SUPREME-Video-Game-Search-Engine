#!/bin/bash

# Navigate to game-search-app, install dependencies, and start the app
cd game-search-app
npm install

# Navigate to game-search-server and install dependencies
cd ../game-search-server
npm install

# Start the app and server
cd ../game-search-app
npm start &
pid1=$!

cd ../game-search-server
npm start & 
pid2=$!

trap 'kill "$pid1" "$pid2"' EXIT
wait