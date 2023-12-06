set scriptfolder=%~dp0
set batfile=run.bat
set "runbatpath=%scriptfolder%%batfile%"
schtasks /create /tn "Send Consultations Email" /tr %runbatpath% /sc weekly /d WED /st 13:34
