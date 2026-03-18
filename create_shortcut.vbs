' Создаёт ярлыки "Spotify Clone" и "Spotify Clone (App)" на рабочем столе
Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

scriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
icoPath = scriptDir & "\spotify-clone-icon.ico"
desktop = WshShell.SpecialFolders("Desktop")

' Ярлык 1: полный запуск (Docker + браузер)
Set s1 = WshShell.CreateShortcut(desktop & "\Spotify Clone.lnk")
s1.TargetPath = scriptDir & "\Spotify Clone.bat"
s1.WorkingDirectory = scriptDir
s1.Description = "Spotify Clone - full start"
s1.IconLocation = icoPath & ",0"
s1.Save

' Ярлык 2: только окно приложения (Docker должен быть уже запущен)
Set s2 = WshShell.CreateShortcut(desktop & "\Spotify Clone (App).lnk")
s2.TargetPath = scriptDir & "\test-app-window.bat"
s2.WorkingDirectory = scriptDir
s2.Description = "Spotify Clone - app window only"
s2.IconLocation = icoPath & ",0"
s2.Save

WScript.Echo "Created: Spotify Clone.lnk, Spotify Clone (App).lnk"
