SET scriptpath=%~dp0
SET scriptfolder=%scriptpath:~0,-1%
cd %scriptfolder%
cd ..
python -m mailservice.mail
