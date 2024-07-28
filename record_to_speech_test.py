import time
# import whisper
import pyaudio
import wave
import threading
import keyboard
import speech_recognition

FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 44100
CHUNK = 512
OUTPUTFILE = "audio.wav"

audio = pyaudio.PyAudio()

stream = audio.open(format=FORMAT,channels=CHANNEL,rate=RATE
                    ,frames_per_buffer=CHUNK,input=True)
# model = whisper.load_model("base")
record = False
recognizier = speech_recognition.Recognizer()
def recording():
    print("recording......")
    global stream
    global audio
    frames = []
    while record == True:
        data = stream.read(CHUNK,exception_on_overflow=False)
        frames.append(data)
    print("recording stopped")
    process_data(frames)

def stop_recording():
    print("alt has been released stopping recording")
    global stream
    global audio
    global record
    record = False
    stream.stop_stream()
    stream.close()
    audio.terminate()

def start_recording():
    print("alt has been pressed starting recording")
    global record
    record = True
    threading.Thread(target=recording).start()

def process_data(audio_file):
    # print(audio_file)
    print("audio frames received processing....")
    global audio
    wavefile = wave.open(OUTPUTFILE,'wb')
    wavefile.setnchannels(CHANNEL)
    wavefile.setsampwidth(audio.get_sample_size(FORMAT))
    wavefile.setframerate(RATE)
    wavefile.writeframes(b''.join(audio_file))
    wavefile.close()
    process_audio()

def process_audio():
    print("processing data............")
    with speech_recognition.AudioFile(OUTPUTFILE) as source:
        audio = recognizier.record(source)
        print(recognizier.recognize_google(audio,language="en"))








keyboard.on_press_key("alt",lambda _:start_recording())
keyboard.on_release_key("alt",lambda _:stop_recording() if record==True else print("wait till it shows starting recording"))

keyboard.wait("esc")