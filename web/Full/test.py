import queue
import sys
import sounddevice as sd
import keyboard  # Requires `pip install keyboard`
from vosk import Model, KaldiRecognizer
import requests

q = queue.Queue()
recording = False

GPT_CHAT_URL = "http://127.0.0.1:5000/gpt"


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    global recording 
    if status:
        print(status, file=sys.stderr)
        
    if recording:
        q.put(bytes(indata))

conversation_history = [
    {
        "role": "system",
        "content": """
        USE ONLY ENGLISH LANGUAGE. You are an avatar named Rakhat in the role of a teacher, you should inroduce yourself first to user. DON'T USE IN ANSWERS SYMBOLS LIKE \\n. 
        You do not know anything except the texts below. You must not answer offtopic questions like "Who's the president of the USA". 
        Answer in teaching manner. Answer in JSON format like {"resp_user": "HERE YOU SHOULD PUT THE ANSWER TO USER", "context": "HERE YOU SHOULD PUT THE SUMMARY OF THE TEXTS AND SUMMARY OF CONVERSATION, SO YOU WON'T FORGET, ALSO YOU SHOULD TYPE THE THINGS YOU WOULD SAY ABOUT NEXT, IT IS ESSENTIAL"}. 
        START YOUR LECTURE STARTING FROM THIS MESSAGE. START RETELLING THESE TEXTS AND YOU SHOULD LEAD THE CONVERSATION, NOT THE USER. AFTER YOU HAVE TOLD SOME INFORMATION, YOU SHOULD ASK QUESTIONS BASED ON THE INFORMATION YOU JUST TOLD. 
        YOU ARE A TEACHER, HAVING A LECTURE ABOUT THESE TEXTS. USE WORDS INSTEAD OF NUMBERS, DO NOT TYPE NUMBERS LIKE TWENTY, USE WORDS. DO NOT ANSWER OUTSIDE OF JSON. 
        AND DO NOT ADD ANY OTHER THING IN JSON FORMAT, ONLY "resp_user" and "context", not any kind of "questions"
        The texts: 
        Lake Balkhash is located in the southeast, its length is 614 km and its width is 74 km. It is drained by the rivers Ile, Lepsi, Ayacoz, Bakanas, Karatal, Mointa. In recent years, the lake area has decreased by 2000 square meters, the level has fallen by 3 meters, salinity has increased, and the number of fish has decreased. Lake Balkhash is very important for our country, the government needs to pay attention. Lake Balkhash is a national and natural wealth for Kazakhstan. (101 words) **Language is a treasure** Linguist Oliver Weidel Holmes says that every language is a sacred temple, the basis of culture. Language is the foundation of culture. Scholar Edward Saurnik explains that thousands of generations have lost their language, and that the history of the people is equal to the history of the mother tongue. Professor Yohan Vanmor Grave explains that the language is the basis of the culture.
        The Happiness Map** Modern people need not only wealth to be happy, but also health and education. According to the Happiness Map, created by researchers at the University of Leicester, Denmark is the happiest country in the world. The study surveyed 80,000 people in 178 countries. The happiest countries include the richest and smartest. Health care, poverty, and access to education all affect happiness. Low-population, strong social cohesion countries performed best. Asian countries performed poorly. **Tutankhamun Treasures** Tutankhamun is the son-in-law of Nefertiti, a pharaoh who ascended the throne at age 12 and died before the age of twenty. In 1923, Howard Carter discovered Tutankhamun's burnt-out tomb in a gold jar. 10 treasures in the Cairo Egyptian Museum
        Benefits of bee milk Bee milk has many benefits. Its Latin name is "Apilax", and in Russian it is called "maternal milk". Bee milk contains many enzymes, nucleic and amino acids, vitamins, fats and trace minerals. Bee milk is used in scientific medicine, pharmaceuticals to prepare the drug "Apilax" and in the manufacture of perfumes. The substances in bee milk help to prolong life, youth and improve health. For example, freshly extracted milk helps to stop the spread of microbes in the body. Bee milk reduces high blood pressure, dilates blood vessels, slows heart disease, improves sleep and improves mood. Research shows that low levels of Arin in the blood and improve blood sugar content.
        """
    }
]


def get_gpt_response(user_input, conversation_history):
    print("AAAAAAAAAAAAAAAAAAAA", conversation_history)
    conversation_history.append({
        "role": "user",
        "content": user_input
    })
        
    try:
        response = requests.post(GPT_CHAT_URL, json={'user_input': user_input, 'conversation_history': conversation_history})
        response.raise_for_status()
        gpt_response = response.json().get('response')
        conversation_history = response.json().get('conversation_history')
    except Exception as e:
        print("Error in GPT request: ", e)

    if gpt_response is None:
        gpt_response = "No response from GPT"  # Provide a default response in case of failure
    conversation_history.append({
        "role": "assistant",
        "content": gpt_response
    })
    # print(conversation_history)
    return gpt_response
    # conversation_history.append({
    #     "role": "assistant",
    #     "content": gpt_message
    # })
    
    # gpt_response = json.loads(gpt_message)
    
    # return jsonify({
    #     "response": gpt_message,
    #     "conversation_history": conversation_history
    # })

def main():
    global recording
    
    # Initialize the Vosk model
    vosk_model = Model(r"web\Full\utils\vosk\vosk-model-kz-0.15")
    
    # Set the sampling rate and other audio parameters
    samplerate = 16000  # You can set it to the desired sampling rate
    device = None  # Use the default input device

    def toggle_recording():
        global recording
        recording = not recording
        print("Recording" if recording else "Stopped recording")

    # Attach the space key to toggle recording
    keyboard.on_press_key("num 9", lambda _: toggle_recording())

    with sd.RawInputStream(samplerate=samplerate, 
                           blocksize=8000, 
                           device=device,
                           dtype="int16", 
                           channels=1, 
                           callback=callback):
        vosk_rec = KaldiRecognizer(vosk_model, samplerate)

        print("Press the numpad 9 key to start/stop recording.")

        while True:
            try:
                vosk_data = q.get(timeout=1000)  # Adjust timeout as needed
                if vosk_rec.AcceptWaveform(vosk_data):
                    vosk_output = vosk_rec.Result().split('"')[-2]
                    
                    if vosk_output:
                        print(f"Recognized Text: {vosk_output}")
                        print(get_gpt_response(vosk_output, conversation_history))

                else:
                    vosk_output = vosk_rec.PartialResult().split('"')[-2]
                    print(f"Partial Result: {vosk_output}")
            except queue.Empty:
                pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        sys.exit(type(e).__name__ + ": " + str(e))