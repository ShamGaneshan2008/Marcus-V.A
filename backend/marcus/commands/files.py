import os
import subprocess
import platform
from backend.marcus.commands.base import BaseCommand


def handle(text: str) -> str:
    """Main entry point called by router."""
    lower = text.lower()

    if any(k in lower for k in ["list files", "show files"]):
        return _list_files()

    if "read file" in lower:
        return _read_file(text)

    if "open file" in lower:
        return OpenFile().execute(text)

    if "delete file" in lower:
        return DeleteFile().execute(text)

    if any(k in lower for k in ["create file", "make file"]):
        return CreateFile().execute(text)

    if any(k in lower for k in ["clipboard", "what did i copy", "read clipboard", "summarise clipboard"]):
        return _read_clipboard()

    return "I can list, open, read, create, or delete files. What do you need?"


def _list_files() -> str:
    files = os.listdir("")
    if not files:
        return "Nothing in the current directory."
    return "Files here: " + ", ".join(files[:20])


def _read_file(text: str) -> str:
    filename = text.lower().replace("read file", "").strip()
    if not filename:
        return "Which file should I read?"
    if not os.path.exists(filename):
        return f"Can't find '{filename}'."
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read(2000)
        return f"Here's what's in {filename}: {content}"
    except Exception as e:
        return f"Couldn't read that file: {e}"


def _read_clipboard() -> str:
    try:
        import pyperclip
        content = pyperclip.paste()
        if not content or not content.strip():
            return "Clipboard is empty."
        return f"Clipboard says: {content[:500]}"
    except ImportError:
        return "Install pyperclip for clipboard access: pip install pyperclip"
    except Exception as e:
        return f"Couldn't read clipboard: {e}"


class ListFiles(BaseCommand):
    name = "list_files"
    triggers = ["list files", "show files"]

    def execute(self, command: str) -> str:
        return _list_files()


class OpenFile(BaseCommand):
    name = "open_file"
    triggers = ["open file"]

    def execute(self, command: str) -> str:
        filename = command.lower().replace("open file", "").strip()
        if not filename:
            return "Which file should I open?"
        if not os.path.exists(filename):
            return f"File '{filename}' not found."
        try:
            if platform.system() == "Windows":
                os.startfile(filename)
            elif platform.system() == "Darwin":
                subprocess.call(["open", filename])
            else:
                subprocess.call(["xdg-open", filename])
            return f"Opening {filename}."
        except Exception as e:
            return f"Couldn't open that: {e}"


class DeleteFile(BaseCommand):
    name = "delete_file"
    triggers = ["delete file"]

    def execute(self, command: str) -> str:
        filename = command.lower().replace("delete file", "").strip()
        if not filename:
            return "Which file should I delete?"
        if not os.path.exists(filename):
            return f"File '{filename}' not found."
        try:
            os.remove(filename)
            return f"Deleted {filename}."
        except Exception as e:
            return f"Couldn't delete that: {e}"


class CreateFile(BaseCommand):
    name = "create_file"
    triggers = ["create file", "make file"]

    def execute(self, command: str) -> str:
        for trigger in self.triggers:
            command = command.lower().replace(trigger, "").strip()
        if not command:
            return "What should I name the file?"
        try:
            with open(command, "w") as f:
                f.write("")
            return f"Created file: {command}."
        except Exception as e:
            return f"Couldn't create that file: {e}"