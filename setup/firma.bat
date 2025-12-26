X:\firma\signtool.exe sign /fd sha256 /td SHA256 /f "X:\Certificati\tuxxle.pfx" /p 01811365 /tr http://timestamp.digicert.com "X:\GitHub\remote-control\dist\RemoteControlServer.exe"
pause
X:\firma\signtool.exe sign /fd sha256 /td SHA256 /f "X:\Certificati\tuxxle.pfx" /p 01811365 /tr http://timestamp.digicert.com "X:\GitHub\remote-control\dist\RemoteControlClient.exe"