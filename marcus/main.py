from marcus.utils.listener import listen
from marcus.utils.speech import speak
from marcus.core.router import route_command


def main():
    speak("Marcus is online.")

    while True:
        command = listen()

        if command:
            response = route_command(command)
            speak(response)


if __name__ == "__main__":
    main()