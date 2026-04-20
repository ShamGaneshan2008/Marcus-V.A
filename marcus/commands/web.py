import webbrowser

def open_google():
    webbrowser.open("https://www.google.com")
    return "Opening Google"

def open_youtube():
    webbrowser.open("https://www.youtube.com")
    return "Opening YouTube"

def search_google(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Searching Google for {query}"