/**
 * AudioPlayer.jsx
 * Uses browser-native SpeechSynthesis API (Web Speech API) to read
 * the diagnosis + remedy aloud. No backend dependency.
 */
import { useState, useEffect, useRef } from 'react'

export default function AudioPlayer({ crop, disease, explanation, remedy, isHealthy }) {
  const [isSpeaking, setIsSpeaking] = useState(false)
  const utteranceRef = useRef(null)

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel()
      }
    }
  }, [])

  // Build the full speech script
  const buildScript = () => {
    const statusLine = isHealthy
      ? `Your ${crop} crop appears to be healthy.`
      : `${crop} crop diagnosed with ${disease}.`

    const explanationPart = explanation
      ? `Here's what this means: ${explanation}`
      : ''

    const remedyPart = remedy
      ? `What you should do: ${remedy.replace(/^\d+\.\s*/gm, '').replace(/\n/g, '. ')}`
      : ''

    return [statusLine, explanationPart, remedyPart]
      .filter(Boolean)
      .join(' ... ')
  }

  const handlePlay = () => {
    if (!window.speechSynthesis) {
      alert('Text-to-speech is not supported in your browser. Try Chrome or Edge.')
      return
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel()

    const script = buildScript()
    const utterance = new SpeechSynthesisUtterance(script)

    // Voice settings
    utterance.rate   = 0.88   // slightly slower for clarity
    utterance.pitch  = 1.0
    utterance.volume = 1.0
    utterance.lang   = 'en-IN' // Indian English accent (falls back to en)

    // Try to pick a natural-sounding voice
    const voices = window.speechSynthesis.getVoices()
    const preferredVoice = voices.find(v =>
      v.lang.includes('en-IN') || v.lang.includes('en-GB') || v.lang.includes('en-AU')
    ) || voices.find(v => v.lang.includes('en'))

    if (preferredVoice) utterance.voice = preferredVoice

    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend   = () => setIsSpeaking(false)
    utterance.onerror = () => setIsSpeaking(false)

    utteranceRef.current = utterance
    window.speechSynthesis.speak(utterance)
  }

  const handleStop = () => {
    window.speechSynthesis.cancel()
    setIsSpeaking(false)
  }

  const isTTSSupported = 'speechSynthesis' in window

  if (!isTTSSupported) {
    return (
      <div className="audio-section">
        <span className="audio-label">🔇 Text-to-speech not supported in this browser</span>
      </div>
    )
  }

  return (
    <div className="audio-section">
      {!isSpeaking ? (
        <button
          className="audio-btn"
          onClick={handlePlay}
          id="tts-play-btn"
          aria-label="Play diagnosis and remedy as audio"
        >
          🔊 Play Diagnosis Aloud
        </button>
      ) : (
        <>
          <button
            className="audio-btn speaking"
            onClick={handlePlay}
            aria-label="Replaying audio"
          >
            🔊 Playing
            <span className="loading-dots">
              <span /><span /><span />
            </span>
          </button>
          <button
            className="audio-stop-btn"
            onClick={handleStop}
            id="tts-stop-btn"
            aria-label="Stop audio"
          >
            ⏹ Stop
          </button>
        </>
      )}
      <span className="audio-label">Powered by browser speech synthesis</span>
    </div>
  )
}
