@echo off
cd /D "%~dp0"
:: startgoagent.inc.bat
:: Step2 - Start GoAgent
echo Starting GoAgent...
cd goagent-local
ver | find "5.0." > NUL &&  start goagent.exe   
ver | find "5.1." > NUL &&  start goagent.exe  
ver | find "5.2." > NUL &&  start goagent.exe    
ver | find "6.0." > NUL &&  start goagent.exe  
ver | find "6.1." > NUL &&  start goagent.exe 
ver | find "6.2." > NUL &&  start goagent-win8.exe
cd..

:: startfirefox.inc.bat
:: Step3 - Start PortableBroswer
echo Starting PortableBroswer...
python27.exe startbroswer.py

pause

exit