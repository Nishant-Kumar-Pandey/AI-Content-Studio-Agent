/**
 * Audio Service for Web Speech API (Text-to-Speech)
 */

class AudioService {
  constructor() {
    this.synth = window.speechSynthesis;
    this.utterance = null;
    this.voices = [];
    
    // Load voices
    this._loadVoices();
    if (this.synth.onvoiceschanged !== undefined) {
      this.synth.onvoiceschanged = () => this._loadVoices();
    }
  }

  _loadVoices() {
    this.voices = this.synth.getVoices();
  }

  speak(text) {
    this.stop(); // Stop any current speech
    
    // Clean markdown for speech
    const cleanText = text.replace(/[*#_[\]()]/g, '').replace(/https?:\/\/\S+/g, '');

    this.utterance = new SpeechSynthesisUtterance(cleanText);
    
    // Suggest a professional "Nova" voice (prefers female-sounding voices for this persona if available)
    const preferredVoices = this.voices.filter(v => 
      v.name.includes('Google') || v.name.includes('Female') || v.name.includes('Samantha')
    );
    if (preferredVoices.length > 0) {
      this.utterance.voice = preferredVoices[0];
    }

    this.utterance.pitch = 1.1; // Slightly higher energy
    this.utterance.rate = 1.0;  // Natural speed
    
    this.synth.speak(this.utterance);
  }

  stop() {
    if (this.synth.speaking) {
      this.synth.cancel();
    }
  }
}

export const audioService = new AudioService();
