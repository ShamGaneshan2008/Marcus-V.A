import webbrowser
import urllib.parse


def handle(text: str) -> str:
    lower = text.lower()

    # YouTube
    if "youtube" in lower:
        query = ""
        for trigger in ["search for", "search", "look up", "find", "play"]:
            if trigger in lower:
                query = lower.split(trigger, 1)[-1].strip()
                break

        if query:
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            webbrowser.open(url)
            return f"Searching YouTube for '{query}'."
        else:
            webbrowser.open("https://www.youtube.com")
            return "YouTube is open."

    # Google search
    if any(k in lower for k in ["search for", "google", "look up", "search"]):
        query = ""
        for trigger in ["search for", "look up", "google", "search"]:
            if trigger in lower:
                query = lower.split(trigger, 1)[-1].strip()
                break

        if query:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(url)
            return f"Searching Google for '{query}'."
        else:
            webbrowser.open("https://www.google.com")
            return "Google is open."

    # News
    if "news" in lower:
        webbrowser.open("https://news.google.com")
        return "Opening Google News."

    # Wikipedia / what is / who is
    if any(k in lower for k in ["what is", "who is"]):
        for trigger in ["what is", "who is"]:
            if trigger in lower:
                query = lower.split(trigger, 1)[-1].strip()
                url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
                webbrowser.open(url)
                return f"Looking up '{query}'."

    # Generic open website
    if "open" in lower:
        sites = {
            "github": "https://github.com",
            "reddit": "https://reddit.com",
            "twitter": "https://twitter.com",
            "instagram": "https://instagram.com",
            "gmail": "https://mail.google.com",
            "google": "https://google.com",
        }
        for name, url in sites.items():
            if name in lower:
                webbrowser.open(url)
                return f"Opening {name.capitalize()}."

    return "What do you want me to search for?"