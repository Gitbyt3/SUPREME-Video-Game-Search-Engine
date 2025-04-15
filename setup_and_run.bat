@echo off
echo ========================
echo Starting Search Engine...
echo ========================

:: Activate Anaconda environment (py312)
CALL C:\\Path\\To\\Anaconda3\\Scripts\\activate.bat your_env_name

:: Start frontend (React app)
echo Launching Frontend (game-search-app)...
cd game-search-app
call npm install
start "" cmd /k "CALL C:\\Path\\To\\Anaconda3\\Scripts\\activate.bat your_env_name"
cd ..

:: Start backend (Node.js server)
echo Launching Backend (game-search-server)...
cd game-search-server
call npm install
start "" cmd /k "CALL C:\\Path\\To\\Anaconda3\\Scripts\\activate.bat your_env_name"
cd ..

echo ========================
echo All services launched!
echo ========================
pause
