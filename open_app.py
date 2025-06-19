import os
import subprocess
import winreg

# Known UWP apps (Microsoft Store apps or system apps)
uwp_apps = {
    "whatsapp": "5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
    "vscode": "Microsoft.VisualStudioCode_8wekyb3d8bbwe!App",
    "camera": "Microsoft.WindowsCamera_8wekyb3d8bbwe!App",
    "photos": "Microsoft.Windows.Photos_8wekyb3d8bbwe!App",
    "paint": "Microsoft.Paint_8wekyb3d8bbwe!App",
    "microsoft edge": "Microsoft.MicrosoftEdge.Stable_8wekyb3d8bbwe!App",
    "edge": "Microsoft.MicrosoftEdge.Stable_8wekyb3d8bbwe!App",
    "microsoft teams": "MSTeams_8wekyb3d8bbwe!MSTeams",
    "teams": "MSTeams_8wekyb3d8bbwe!MSTeams",
}

# -----------------------------------
def open_uwp_app(app_name):
    app_id = uwp_apps.get(app_name.lower())
    if app_id:
        try:
            subprocess.run(f'explorer.exe shell:AppsFolder\\{app_id}', shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    return False

# -----------------------------------
def find_app_with_where(app_name):
    try:
        result = subprocess.check_output(f"where {app_name}", shell=True, text=True)
        return result.strip().split('\n')[0]
    except subprocess.CalledProcessError:
        return None

# -----------------------------------
def find_app_from_registry(app_name):
    try:
        key_path = fr"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{app_name}.exe"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            app_path, _ = winreg.QueryValueEx(key, "")
            return app_path
    except FileNotFoundError:
        return None

# -----------------------------------
def open_app(app_name):
    app_name = app_name.strip().lower()

    # Name aliases for non-UWP apps
    aliases = {
        "vscode": "code",
        "visual studio code": "code",
        "chrome": "chrome",
        "notepad": "notepad",
        "terminal": "wt",
        "microsoft teams": "ms-teams",
        "teams": "ms-teams",
    }

    # Use alias if available, otherwise keep original name
    app_name = aliases.get(app_name, app_name)

    # 1. Try opening as UWP app (if applicable)
    if app_name in uwp_apps:
        if open_uwp_app(app_name):
            return

    # 2. Try using the direct path (for aliases with full paths)
    if app_name in aliases.values() and os.path.exists(app_name):
        try:
            if app_name.endswith("Arduino IDE.exe"):
                # Launch Arduino IDE with output redirected to null
                with open(os.devnull, 'w') as devnull:
                    subprocess.Popen(app_name, stdout=devnull, stderr=devnull, shell=True)
            else:
                os.startfile(app_name)
            return
        except Exception:
            pass

    # 3. Try using 'where' command
    path = find_app_with_where(app_name)
    if path:
        try:
            os.startfile(path)
            return
        except Exception:
            pass

    # 4. Try finding from Windows Registry
    path = find_app_from_registry(app_name)
    if path:
        try:
            os.startfile(path)
            return
        except Exception:
            pass

    # 5. Fallback
    print(f"⚠️ App '{app_name}' not found. Try entering full path to the .exe file.")

# -----------------------------------
if __name__ == "__main__":
    while True:
        app_input = input("\nEnter app name (or 'exit'): ").strip()
        if app_input.lower() == 'exit':
            break
        open_app(app_input)
