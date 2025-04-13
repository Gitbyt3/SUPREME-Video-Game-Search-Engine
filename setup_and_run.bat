@echo off
echo ========================
echo Starting Search Engine...
echo ========================

echo Starting frontend (game-search-app)...
cd game-search-app
call npm install
start cmd /k "npm start"
cd ..

echo Starting backend (game-search-server)...
cd game-search-server
call npm install
start cmd /k "npm start"
cd ..

echo All services started in new terminals. Close this window to stop them.
pause