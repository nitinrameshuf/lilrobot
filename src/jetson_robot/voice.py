#!/usr/bin/env python3
"""
Reliable Jarvis Voice Assistant - Simplified approach that works
Focus on reliability over complexity
"""

import whisper
import sounddevice as sd
import numpy as np
import pyttsx3
import torch
import time
from datetime import datetime
import threading

class ReliableJarvis:
    def __init__(self):
        print("Initializing Reliable Jarvis...")
        
        # System info
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
        
        # Configure ReSpeaker
        self.respeaker_device = self.setup_respeaker()
        
        # Load models
        print("Loading Whisper models...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.wake_model = whisper.load_model("tiny", device=self.device)
        self.command_model = whisper.load_model("base", device=self.device)
        
        # Pre-warm models
        dummy_audio = np.zeros(8000, dtype=np.float32)  # 0.5 second dummy
        self.wake_model.transcribe(dummy_audio, fp16=True, language="en")
        self.command_model.transcribe(dummy_audio, fp16=True, language="en")
        print("Models ready")
        
        # Initialize TTS
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 170)
        
        # Simple, reliable audio settings
        self.sample_rate = 16000
        self.wake_chunk_duration = 1.0  # 1 second chunks
        self.command_duration = 4.0     # 4 seconds for commands
        
        # Wake words
        self.wake_words = ["jarvis", "bot", "hey jarvis"]
        
        # State management
        self.is_running = True
        self.processing_command = False
        
        # Performance tracking
        self.wake_detections = 0
        self.commands_processed = 0
        
        print("Reliable Jarvis ready!")
        self.speak("Reliable voice assistant ready. Say Jarvis to activate.")
    
    def setup_respeaker(self):
        """Find ReSpeaker and test basic functionality"""
        devices = sd.query_devices()
        
        for i, device in enumerate(devices):
            if 'respeaker' in device['name'].lower() or 'xvf3800' in device['name'].lower():
                if device['max_input_channels'] > 0:
                    try:
                        # Simple test recording
                        test_audio = sd.rec(
                            int(0.5 * 16000),
                            samplerate=16000,
                            channels=1,
                            device=i,
                            dtype=np.float32
                        )
                        sd.wait()
                        print(f"ReSpeaker device {i} test successful")
                        return i
                    except Exception as e:
                        print(f"ReSpeaker device {i} test failed: {e}")
                        continue
        
        print("Using default audio device")
        return None
    
    def speak(self, text):
        """Simple, reliable text-to-speech"""
        print(f"Jarvis: {text}")
        self.tts.say(text)
        self.tts.runAndWait()
        time.sleep(0.2)  # Brief pause
    
    def detect_wake_word(self, text):
        """Simple wake word detection"""
        if not text:
            return False
        
        text_lower = text.lower().strip()
        return any(wake_word in text_lower for wake_word in self.wake_words)
    
    def listen_for_wake_word(self):
        """Listen for wake word with simple chunked approach"""
        try:
            # Record audio chunk
            audio_chunk = sd.rec(
                int(self.wake_chunk_duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                device=self.respeaker_device
            )
            sd.wait()
            
            # Check if there's meaningful audio
            audio_level = np.abs(audio_chunk).mean()
            if audio_level < 0.002:
                return False, ""
            
            # Process with wake word model
            start_time = time.time()
            with torch.cuda.device(0):
                result = self.wake_model.transcribe(
                    audio_chunk.flatten(),
                    fp16=True,
                    language="en",
                    no_speech_threshold=0.6,
                    temperature=0.0,
                    beam_size=1
                )
            
            detection_time = time.time() - start_time
            text = result["text"].strip()
            
            if text and self.detect_wake_word(text):
                print(f"Wake word detected: '{text}' ({detection_time:.2f}s)")
                return True, text
            
            return False, text
            
        except Exception as e:
            print(f"Wake word detection error: {e}")
            return False, ""
    
    def listen_for_command(self):
        """Listen for command after wake word"""
        try:
            print("Listening for command...")
            
            # Record command
            command_audio = sd.rec(
                int(self.command_duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                device=self.respeaker_device
            )
            sd.wait()
            
            # Process command
            start_time = time.time()
            with torch.cuda.device(0):
                result = self.command_model.transcribe(
                    command_audio.flatten(),
                    fp16=True,
                    language="en",
                    task="transcribe",
                    no_speech_threshold=0.3,
                    temperature=0.0,
                    beam_size=1
                )
            
            processing_time = time.time() - start_time
            command_text = result["text"].strip()
            
            if command_text and len(command_text) > 2:
                print(f"Command: '{command_text}' ({processing_time:.2f}s)")
                return command_text
            else:
                print("No clear command detected")
                return ""
                
        except Exception as e:
            print(f"Command processing error: {e}")
            return ""
    
    def process_command(self, command):
        """Process voice commands"""
        command = command.lower()
        
        if any(word in command for word in ["time", "clock"]):
            current_time = datetime.now().strftime("%I:%M %p")
            return f"It's {current_time}"
        
        elif any(word in command for word in ["date", "day", "today"]):
            current_date = datetime.now().strftime("%A, %B %d")
            return f"Today is {current_date}"
        
        elif any(word in command for word in ["hello", "hi", "hey"]):
            return "Hello! What can I do for you?"
        
        elif any(word in command for word in ["status", "performance"]):
            return f"System running. Wake detections: {self.wake_detections}, Commands: {self.commands_processed}"
        
        elif any(word in command for word in ["shutdown", "goodbye", "exit", "stop"]):
            self.is_running = False
            return "Shutting down reliable voice assistant. Goodbye!"
        
        elif "who are you" in command:
            return "I'm Jarvis, your reliable voice assistant."
        
        elif any(word in command for word in ["vision", "camera"]):
            return "Vision systems ready."
        
        elif any(word in command for word in ["robot", "motor"]):
            return "Robotics systems ready."
        
        elif "weather" in command:
            return "Weather data not available yet."
        
        elif "help" in command:
            return "I can tell you the time, date, system status, or help with basic commands."
        
        else:
            return f"I heard: {command}. How can I help with that?"
    
    def run(self):
        """Main execution loop - simple and reliable"""
        print("\n" + "="*60)
        print("RELIABLE JARVIS VOICE ASSISTANT")
        print("Simple chunked processing for maximum reliability")
        print("Say 'Jarvis', 'Bot', or 'Hey Jarvis' to activate")
        print("="*60 + "\n")
        
        try:
            while self.is_running:
                if not self.processing_command:
                    # Listen for wake word
                    wake_detected, wake_text = self.listen_for_wake_word()
                    
                    if wake_detected:
                        self.wake_detections += 1
                        self.processing_command = True
                        
                        # Immediate response
                        self.speak("Yes?")
                        
                        # Get command
                        command = self.listen_for_command()
                        
                        if command:
                            self.commands_processed += 1
                            response = self.process_command(command)
                            self.speak(response)
                        
                        self.processing_command = False
                        print("Ready for next wake word...")
                
                # Brief pause to prevent overwhelming the system
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nShutdown requested")
            self.is_running = False
        except Exception as e:
            print(f"System error: {e}")
        finally:
            print(f"\nSession Summary:")
            print(f"- Wake word detections: {self.wake_detections}")
            print(f"- Commands processed: {self.commands_processed}")
            print("- Architecture: Simple chunked processing")
            
            self.speak("Voice assistant shutting down.")

if __name__ == "__main__":
    # GPU optimization
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    jarvis = ReliableJarvis()
    jarvis.run()
