import React, { useState } from 'react';

const VoiceInput = ({ onTranscript }) => {
  const [isListening, setIsListening] = useState(false);

  const handleToggleListen = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      alert("Your browser does not support Speech Recognition. Try Chrome.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript);
    };

    if (isListening) {
      recognition.stop();
    } else {
      recognition.start();
    }
  };

  return (
    <button 
      className={`voice-btn ${isListening ? 'listening' : ''}`} 
      onClick={handleToggleListen}
      title="Talk to AI"
    >
      {isListening ? '🛑' : '🎤'}
    </button>
  );
};

export default VoiceInput;
