import time
import keyboard
import threading
import speech_recognition
import pyttsx3
import tkinter as tk


class SpeechRecognizer:
    def __init__(self, callback=None):
        self.recording = False
        self.recognizer = speech_recognition.Recognizer()
        self.process_text = callback

    def running_function(self):
        self.recording = True
        with speech_recognition.Microphone() as mic:
            self.recognizer.adjust_for_ambient_noise(mic, duration=0.3)
            print("Listening...")
            audio_frames = []

            try:
                frame = self.recognizer.listen(mic, timeout=1, phrase_time_limit=5)
                audio_frames.append(frame)
            except Exception as e:
                print(e)

        combined_audio_data = b''.join([frame.get_raw_data() for frame in audio_frames])
        sample_rate = audio_frames[0].sample_rate if audio_frames else 16000
        sample_width = audio_frames[0].sample_width if audio_frames else 2
        audio = speech_recognition.AudioData(combined_audio_data, sample_rate, sample_width)

        self.recording = False
        print("Listen successful")
        print("Processing audio")
        try:
            text = self.recognizer.recognize_google(audio, language="en-US")
            self.process_text(text)
        except speech_recognition.UnknownValueError:
            print("Could not understand audio")
            self.process_text("Could not understand audio")
        except speech_recognition.RequestError:
            self.process_text(f'Could not request results; check your network connection')

    def start_function(self):
        if not self.recording:
            return threading.Thread(target=self.running_function).start()
        else:
            self.recording = False
