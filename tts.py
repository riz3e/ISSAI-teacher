import pyttsx3

engine = pyttsx3.init()

voices = engine.getProperty('voices')
for idx, voice in enumerate(voices):
    print(f"Voice {idx}:")
    print(f"  ID: {voice.id}")
    print(f"  Name: {voice.name}")
    print(f"  Languages: {voice.languages}")
    print(f"  Gender: {voice.gender}")
    print(f"  Age: {voice.age}")

desired_voice_id = voices[1].id
engine.setProperty('voice', desired_voice_id)

engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

text = "Hello, this is a test of the pyttsx3 text to speech API. YOO This is Kakashi Nagasaki, I am the MOST great ninja around here!"

engine.say(text)
engine.runAndWait()

engine.stop()
