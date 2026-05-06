[Setup]
AppName=Marcus AI Assistant
AppVersion=1.0
AppPublisher=DedSec
DefaultDirName={autopf}\Marcus
DefaultGroupName=Marcus
OutputDir=installer_output
OutputBaseFilename=Marcus_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\Marcus\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Marcus"; Filename: "{app}\Marcus.exe"
Name: "{group}\Uninstall Marcus"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Marcus"; Filename: "{app}\Marcus.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Marcus.exe"; Description: "Launch Marcus"; Flags: nowait postinstall skipifsilent