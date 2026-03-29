; 脚本由 Inno Setup 脚本向导生成。
; 有关创建 Inno Setup 脚本文件的详细信息，请参阅帮助文档！

#define MyAppName "Useless Subtitle Player-无用字幕播放器"
#define MyAppVersion "1.0"
#define MyAppPublisher "ttwe77"
#define MyAppURL "https://github.com/ttwe77/UselessSubtitlePlayer"
#define MyAppExeName "main.py"

[Setup]
; 注意：AppId 的值唯一标识此应用程序。不要在其他应用程序的安装程序中使用相同的 AppId 值。
; (若要生成新的 GUID，请在 IDE 中单击 "工具|生成 GUID"。)
AppId={{4A5E1A6F-D32D-4DA1-934B-8A79CEC2C4A9}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=G:\Windows11\0Tools\0Project\音乐弹窗\UselessSubtitlePlayer\LICENSE
InfoBeforeFile=G:\Windows11\0Tools\0Project\音乐弹窗\UselessSubtitlePlayer\hint.txt
InfoAfterFile=G:\Windows11\0Tools\0Project\音乐弹窗\UselessSubtitlePlayer\README.md
; 移除以下行以在管理安装模式下运行 (为所有用户安装)。
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
OutputDir=G:\Windows11\0Tools\0Project\音乐弹窗\UselessSubtitlePlayer
OutputBaseFilename=UselessSubtitlePlayer
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "chinesetraditional"; MessagesFile: "compiler:Languages\ChineseTraditional.isl"
Name: "english"; MessagesFile: "compiler:Languages\English.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "G:\Windows11\0Tools\0Project\音乐弹窗\UselessSubtitlePlayer\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "G:\Windows11\0Tools\0Project\音乐弹窗\UselessSubtitlePlayer\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "G:\Windows11\0Tools\0Project\音乐弹窗\UselessSubtitlePlayer\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "G:\Windows11\0Tools\0Project\音乐弹窗\UselessSubtitlePlayer\res\Sihan,三Z-STUDIO,HOYO-MiX - DAMIDAMI\srt.srt"; \
    DestDir: "{app}\res\Sihan,三Z-STUDIO,HOYO-MiX - DAMIDAMI"; \
    Flags: ignoreversion
; 注意：不要在任何共享系统文件上使用 "Flags: ignoreversion" 

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: shellexec postinstall skipifsilent

