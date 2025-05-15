
# from voice_assistant import VoiceAssistant

# def main():
#     assistant = VoiceAssistant()
#     assistant.start()

# if __name__ == "__main__":
#     main()

from voice_assistant import VoiceAssistantGUI  # Import VoiceAssistantGUI instead of VoiceAssistant

def main():
    assistant_gui = VoiceAssistantGUI()  # Create an instance of VoiceAssistantGUI
    assistant_gui.run()  # Run the GUI

if __name__ == "__main__":
    main()


