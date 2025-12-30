# What talon lite does
*This is documentation for how Talon Lite works step by step. This is intended for technical users. If you just want to see what talon lite does refer to the other documentation.*
## Edge 
### Files

- Uninstalls edge via the setup.exe in the application folder
- Removes start menu shortcuts, browser data in appdata, and updater for all users.

### Registry 
- Removes all keys related sto edge from the registry


### Updater
- Removes built in updater located in ProgramFiles(x86)\Microsoft\EdgeUpdate\MicrosoftEdgeUpdate.exe that will reinstall edge if you delete it 

### Uninstaller
- Force uninstalls edge again
- Creates folders in the location where edge previously was installed to block windows from installing it in the future.


## Updates
- Modifies the registry where Windows Updates are configured and sets it to only recive security updates to prevent microsoft from adding more bs in the future. 


## Tweaks 
- Disables the delay for showing menus and submenus
- Disables window size change animations
- Enables instant previews when you hover over a taskbar icon
- Sets file explorer to show extentions.
## External Scripts
*Refer to the documentation provided by these scripts if you want more details*
- https://github.com/ChrisTitusTech/winutil
- https://github.com/Raphire/Win11Debloat
