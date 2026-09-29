#ifndef MyAppVersion
  #define MyAppVersion "0.0.2"
#endif

#define MyAppName "Tun2Proxy GUI"
#define MyAppNameShort "Tun2ProxyGUI"
#define MyAppPublisher "tun2proxy-gui"
#define MyAppURL "https://github.com/tun2proxy/tun2proxy"
#define MyAppExeName "Tun2ProxyGUI.exe"

#ifnexist "..\..\dist\Tun2ProxyGUI\Tun2ProxyGUI.exe"
  #error "未找到 dist\Tun2ProxyGUI\Tun2ProxyGUI.exe，请先运行 scripts\build.ps1"
#endif

[Setup]
AppId={{A7C3E9F1-5B2D-4E8A-9C1F-6D4B8A2E3F70}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppNameShort}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\..\dist
OutputBaseFilename={#MyAppNameShort}-Setup-{#MyAppVersion}-windows-x86_64
SetupIconFile=..\..\resources\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=120
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
DisableReadyPage=no
ShowLanguageDialog=no
VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
MinVersion=10.0
CloseApplications=yes
RestartApplications=no
SetupLogging=yes

[Languages]
Name: "chinesesimplified"; MessagesFile: "languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
chinesesimplified.BeveledLabel={#MyAppName} {#MyAppVersion}
english.BeveledLabel={#MyAppName} {#MyAppVersion}
chinesesimplified.WelcomeLabel1=欢迎使用 {#MyAppName} 安装向导
chinesesimplified.WelcomeLabel2=此向导将引导您完成 {#MyAppName} {#MyAppVersion} 的安装。%n%nTun2Proxy 需要管理员权限以创建 TUN 设备并配置系统路由。安装程序将以管理员身份继续。%n%n建议在继续之前关闭其他应用程序。
english.WelcomeLabel1=Welcome to the {#MyAppName} Setup Wizard
english.WelcomeLabel2=This will install {#MyAppName} {#MyAppVersion} on your computer.%n%nTun2Proxy requires administrator privileges to create a TUN device and manage system routing. Setup will continue with elevated rights.%n%nIt is recommended that you close all other applications before continuing.
chinesesimplified.FinishedHeadingLabel=完成 {#MyAppName} 安装向导
chinesesimplified.FinishedLabelNoIcons={#MyAppName} 已安装到您的计算机。%n%n点击「完成」退出安装向导。
english.FinishedHeadingLabel=Completing the {#MyAppName} Setup Wizard

[CustomMessages]
chinesesimplified.CreateDesktopIcon=创建桌面快捷方式
english.CreateDesktopIcon=Create a &desktop shortcut
chinesesimplified.LaunchAfterInstall=安装完成后启动 {#MyAppName}
english.LaunchAfterInstall=&Launch {#MyAppName}
chinesesimplified.EnableAutostart=开机时自动启动（最小化到托盘）
english.EnableAutostart=Start automatically at &logon (minimized to tray)

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "{cm:EnableAutostart}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\..\dist\Tun2ProxyGUI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppNameShort}"; ValueData: """{app}\{#MyAppExeName}"" --minimized"; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchAfterInstall}"; Flags: nowait postinstall skipifsilent runascurrentuser

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel2.AutoSize := False;
end;
