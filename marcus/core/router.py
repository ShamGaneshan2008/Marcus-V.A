from marcus.commands import system, web, files


def route_command(command: str):
    command = command.lower()

    # =========================
    # 🖥️ SYSTEM COMMANDS
    # =========================
    if "open notepad" in command:
        return system.open_notepad()

    elif "shutdown" in command:
        return system.shutdown()

    elif "restart" in command:
        return system.restart()

    # =========================
    # 🌐 WEB COMMANDS
    # =========================
    elif "open google" in command:
        return web.open_google()

    elif "open youtube" in command:
        return web.open_youtube()

    elif "search" in command:
        query = command.replace("search", "").strip()
        return web.search_google(query)

    # =========================
    # 📁 FILE COMMANDS
    # =========================
    elif "list files" in command:
        return files.list_files()

    # =========================
    # ❌ UNKNOWN COMMAND
    # =========================
    else:
        return "Sorry, I didn't understand that command."