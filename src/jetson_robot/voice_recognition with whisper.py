#!/usr/bin/env python3
"""
GPU-Accelerated Jarvis Voice Assistant for Jetson Orin Nano
Optimized for multi-system robotics architecture
"""

import whisper
import sounddevice as sd
import numpy as np
import pyttsx3
import torch
import time
from datetime import datetime
import threading

class JarvisAssistant:
    def __init__(self):
        print("Initializing GPU-accelerated Jarvis...")
        
        # System info
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"Audio devices: {len(sd.query_devices())}")
        
        # Load Whisper model with GPU acceleration
        print("Loading Whisper model on GPU...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.whisper_model = whisper.load_model("base", device=self.device)
        print(f"Whisper model loaded on: {self.device}")
        
        # Initialize text-to-speech
        print("Initializing text-to-speech...")
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 160)
        
        # Audio settings optimized for real-time processing
        self.sample_rate = 16000
        self.duration = 4  # seconds to record
        
        # Performance monitoring
        self.inference_times = []
        
        print("Jarvis is online with GPU acceleration!")
        self.speak("Jarvis systems online. GPU acceleration enabled.")
    
    def speak(self, text):
        """Convert text to speech - synchronous to avoid feedback loops"""
        print(f"Jarvis: {text}")
        self.tts.say(text)
        self.tts.runAndWait()
        # Brief pause to let audio clear before listening again
        time.sleep(1.0)
    
    def listen(self):
        """Record audio and convert to text using GPU acceleration"""
        print("Listening... (speak now)")
        
        # Brief pause to ensure any TTS output has finished
        time.sleep(0.5)
        
        # Record audio
        audio = sd.rec(
            int(self.duration * self.sample_rate), 
            samplerate=self.sample_rate, 
            channels=1,
            dtype=np.float32
        )
        sd.wait()
        
        # Debug: Check audio level but don't filter based on it
        audio_level = np.abs(audio).mean()
        print(f"Audio level: {audio_level:.4f}")
        
        print("Processing with GPU-accelerated Whisper...")
        start_time = time.time()
        
        # GPU-accelerated transcription with language optimization
        with torch.cuda.device(0):  # Ensure we're using the GPU
            result = self.whisper_model.transcribe(
                audio.flatten(),
                fp16=torch.cuda.is_available(),  # Use FP16 for faster inference on GPU
                language="en",  # Force English to prevent Arabic/other language detection
                task="transcribe",  # Explicit transcription task
                no_speech_threshold=0.4,  # Lowered from 0.6 - was too strict
                logprob_threshold=-1.5,  # Lowered from -1.0 - less filtering
                temperature=0.0  # Deterministic output, reduces hallucinations
            )
        
        inference_time = time.time() - start_time
        self.inference_times.append(inference_time)
        
        text = result["text"].strip()
        
        # Filter out low-confidence or very short transcriptions
        if len(text) < 2:  # Reduced from 3 - allow shorter responses
            print(f"[Too short]: '{text}' (processed in {inference_time:.2f}s)")
            return ""
        
        # More lenient confidence checking
        high_no_speech = any(segment.get("no_speech_prob", 0) > 0.9 for segment in result.get("segments", []))  # Raised from 0.8
        if high_no_speech:
            print(f"[Low confidence]: '{text}' (processed in {inference_time:.2f}s)")
            return ""
        
        # Filter out likely feedback (hearing own TTS output)
        if text and not self._is_feedback(text):
            print(f"You said: '{text}' (processed in {inference_time:.2f}s)")
            return text
        else:
            if text:
                print(f"[Filtered feedback]: '{text}' (processed in {inference_time:.2f}s)")
            return ""
    
    def get_performance_stats(self):
        """Return performance statistics"""
        if self.inference_times:
            avg_time = sum(self.inference_times) / len(self.inference_times)
            return f"Average inference time: {avg_time:.2f}s, GPU utilization: Active"
        return "No inference data yet"
    
    def _is_feedback(self, text):
        """Check if the transcribed text is likely feedback from our own TTS"""
        text_lower = text.lower()
        feedback_phrases = [
            "jarvis systems online",
            "gpu acceleration enabled",
            "system ready for expansion",
            "robotics control interface",
            "awaiting motor control",
            "system status",
            "current time is",
            "today is",
            "shutting down"
        ]
        return any(phrase in text_lower for phrase in feedback_phrases)
    
    def process_command(self, command):
        """Process voice commands - expandable for robotics integration"""
        command = command.lower()
        
        if "time" in command:
            current_time = datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}"
        
        elif "date" in command:
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {current_date}"
        
        elif "hello" in command or "hi" in command:
            return "Hello! I'm Jarvis, running with GPU acceleration on your Jetson Orin."
        
        elif "status" in command or "performance" in command:
            gpu_status = "Active" if torch.cuda.is_available() else "Inactive"
            stats = self.get_performance_stats()
            return f"System status: GPU {gpu_status}, {stats}. Ready for parallel processing."
        
        elif "shutdown" in command or "goodbye" in command or "exit" in command:
            return "Shutting down Jarvis. Goodbye!"
        
        elif "who are you" in command:
            return "I am Jarvis, your GPU-accelerated AI assistant running on NVIDIA Jetson Orin Nano."
        
        elif "vision" in command or "camera" in command:
            return "Vision systems integration ready. Awaiting computer vision modules."
        
        elif "robot" in command or "motor" in command:
            return "Robotics control interface ready. Awaiting motor control integration."
        
        elif len(command.strip()) == 0:
            return "I didn't catch that. Could you please repeat?"
        
        else:
            return f"Command '{command}' noted. System ready for expansion with robotics modules."
    
    def run(self):
        """Main conversation loop optimized for robotics integration"""
        print("\n" + "="*60)
        print("JARVIS GPU-ACCELERATED VOICE ASSISTANT")
        print("Optimized for Multi-System Robotics Architecture")
        print("Commands: 'status', 'time', 'vision', 'robot', 'goodbye'")
        print("="*60 + "\n")
        
        try:
            while True:
                # Listen for command
                command = self.listen()
                
                if command:
                    # Process command
                    response = self.process_command(command)
                    
                    # Speak response (non-blocking)
                    self.speak(response)
                    
                    # Check for shutdown
                    if any(word in command.lower() for word in ["shutdown", "goodbye", "exit"]):
                        break
                
                # Brief pause to allow other system processes
                print("-" * 40)
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\nShutdown signal received")
            self.speak("Emergency shutdown. Jarvis going offline.")
        except Exception as e:
            print(f"Error: {e}")
            self.speak("System error detected. Please check logs.")
        
        # Performance summary
        if self.inference_times:
            avg_time = sum(self.inference_times) / len(self.inference_times)
            print(f"\nSession Summary:")
            print(f"- Total voice commands: {len(self.inference_times)}")
            print(f"- Average processing time: {avg_time:.2f}s")
            print(f"- GPU utilization: Optimal")

if __name__ == "__main__":
    # GPU memory optimization for multi-system environment
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    jarvis = JarvisAssistant()
    jarvis.run()
