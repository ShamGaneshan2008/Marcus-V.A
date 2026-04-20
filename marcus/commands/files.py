import os

def list_files(path="."):
    try:
        files = os.listdir(path)
        return "Files: " + ", ".join(files)
    except Exception as e:
        return f"Error: {str(e)}"