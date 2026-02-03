[Setup]

AppName=Ingressos Abrolhos GRU
AppVersion=1.0
DefaultDirName={localappdata}\Ingressos Abrolhos
DefaultGroupName=Ingressos Abrolhos GRU
AppPublisher=Alberto Rodrigues
AppPublisherURL=https://github.com/skavazza/ingressos_abrolhos_gru
AppSupportURL=https://github.com/skavazza/ingressos_abrolhos_gru
AppUpdatesURL=https://github.com/skavazza/ingressos_abrolhos_gru
OutputDir=.\OUTPUT
OutputBaseFilename=Igressos_AbrolhosGRU_Setup
SetupIconFile=F:\GRU\ABROLHOS_ INGRESSOS\dist\assets\icon.ico
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
Compression=lzma2
SolidCompression=yes
WizardStyle=classic

[Files]
Source: "F:\GRU\ABROLHOS_ INGRESSOS\dist\abrolhos_ingressos.db"; DestDir: "{app}"; Flags: ignoreversion
Source: "F:\GRU\ABROLHOS_ INGRESSOS\dist\AbrolhosIngressos.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "F:\GRU\ABROLHOS_ INGRESSOS\dist\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
; Atalho do Menu Iniciar
Name: "{group}\Ingressos Abrolhos"; Filename: "{app}\AbrolhosIngressos.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\icon.ico"
; Atalho no Desktop
Name: "{userdesktop}\Ingressos Abrolhos"; Filename: "{app}\AbrolhosIngressos.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\icon.ico"
