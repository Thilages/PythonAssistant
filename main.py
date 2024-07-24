import time
import keyboard
import threading
import speech_recognition
import pyttsx3
# import pyaudio

recording = False
recognizer = speech_recognition.Recognizer()




def running_function():
    global recording
    recording = True
    with speech_recognition.Microphone() as mic:
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(mic,duration=0.3)
        print("Listening...")
        # Listen for audio
        audio_frames = []
        while recording:
            try:
                frame = recognizer.listen(mic,timeout=1,phrase_time_limit=5)
                audio_frames.append(frame)
            except Exception as e:
                print(e)
                continue
    combined_audio_data = b''.join([frame.get_raw_data() for frame in audio_frames])
    sample_rate = audio_frames[0].sample_rate if audio_frames else 16000
    sample_width = audio_frames[0].sample_width if audio_frames else 2
    audio_data = speech_recognition.AudioData(combined_audio_data, sample_rate, sample_width)


    recording = False
    print("Listen successfull")
    process_audio(audio_data)

def process_audio(audio):
    print("processing audio")
    try:
        text = recognizer.recognize_google(audio,language="en-US")
        print(text)
    except speech_recognition.UnknownValueError:
        print(Exception)
    except speech_recognition.RequestError:
        print("WTF is wrong with you")

def start_function():
    global recording
    if recording == False:
        threading.Thread(target=running_function).start()
    else:
        recording = False

print("ready")
keyboard.on_press_key("alt",lambda _:start_function())



keyboard.wait("esc")