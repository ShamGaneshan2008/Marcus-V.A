import os

def open_notepad():
    os.system("notepad")
    return "Opening Notepad"

def shutdown():
    os.system("shutdown /s /t 5")
    return "Shutting down the system"

def restart():
    os.system("shutdown /r /t 5")
    return "Restarting the system"