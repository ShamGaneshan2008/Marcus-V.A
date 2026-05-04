import os
import re
import subprocess
import platform
import webbrowser


def handle(text: str) -> str:
    lower = text.lower()

    # Volume control
    if "volume" in lower:
        return _handle_volume(lower)

    # Shutdown
    if "shutdown" in lower or "shut down" in lower:
        os.system("shutdown /s /t 5")
        return "Shutting down in 5 seconds."

    # Restart
    if "restart" in lower or "reboot" in lower:
        os.system("shutdown /r /t 5")
        return "Restarting in 5 seconds."

    # Sleep
    if "sleep" in lower or "hibernate" in lower:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Going to sleep."

    # Lock
    if "lock" in lower:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "Workstation locked."

    # Notepad
    if "notepad" in lower:
        subprocess.Popen("notepad.exe")
        return "Opening Notepad."

    # Task manager
    if "task manager" in lower:
        subprocess.Popen("taskmgr.exe")
        return "Opening Task Manager."

    # Calculator
    if "calculator" in lower or "calc" in lower:
        subprocess.Popen("calc.exe")
        return "Opening Calculator."

    # File explorer
    if "explorer" in lower or "file manager" in lower or "my files" in lower:
        subprocess.Popen("explorer.exe")
        return "Opening File Explorer."

    # Open specific apps by name
    app_result = _open_app(lower)
    if app_result:
        return app_result

    return "I can handle shutdown, restart, lock, sleep, volume, and app launching."


def _handle_volume(lower: str) -> str:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        # Mute / unmute
        if "mute" in lower:
            volume.SetMute(1, None)
            return "Muted."
        if "unmute" in lower:
            volume.SetMute(0, None)
            return "Unmuted."

        # Set to specific level
        match = re.search(r'(\d+)', lower)
        if match:
            level = max(0, min(100, int(match.group(1))))
            volume.SetMasterVolumeLevelScalar(level / 100, None)
            return f"Volume set to {level}%."

        # Increase / decrease
        current = volume.GetMasterVolumeLevelScalar()
        if any(k in lower for k in ["up", "increase", "louder", "raise"]):
            new = min(1.0, current + 0.1)
            volume.SetMasterVolumeLevelScalar(new, None)
            return f"Volume increased to {int(new * 100)}%."
        if any(k in lower for k in ["down", "decrease", "lower", "quieter"]):
            new = max(0.0, current - 0.1)
            volume.SetMasterVolumeLevelScalar(new, None)
            return f"Volume decreased to {int(new * 100)}%."

        return f"Current volume is {int(current * 100)}%."

    except ImportError:
        # Fallback using nircmd or system keys
        if "mute" in lower:
            os.system("nircmd.exe mutesysvolume 1")
            return "Muted."
        match = re.search(r'(\d+)', lower)
        if match:
            level = max(0, min(65535, int(int(match.group(1)) * 655.35)))
            os.system(f"nircmd.exe setsysvolume {level}")
            return f"Volume adjusted."
        return "Install pycaw for precise volume control: pip install pycaw comtypes"
    except Exception as e:
        return f"Volume control failed: {e}"


def _open_app(lower: str) -> str | None:
    """Try to open a named app."""
    apps = {
        "vs code": "code",
        "vscode": "code",
        "visual studio code": "code",
        "chrome": "chrome",
        "google chrome": "chrome",
        "firefox": "firefox",
        "spotify": "spotify",
        "discord": "discord",
        "telegram": "telegram",
        "whatsapp": "whatsapp",
        "pycharm": "pycharm64",
        "terminal": "wt",  # Windows Terminal
        "cmd": "cmd",
        "powershell": "powershell",
        "word": "winword",
        "excel": "excel",
        "paint": "mspaint",
        "vlc": "vlc",
        "steam": "steam",
    }

    for name, cmd in apps.items():
        if name in lower:
            try:
                subprocess.Popen(cmd, shell=True)
                return f"Opening {name.title()}."
            except Exception:
                return f"Couldn't find {name.title()} — is it installed?"

    return None