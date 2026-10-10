/**
 * ResultCard.jsx — Full result display (v4)
 * Adds: English / Hindi (lang prop), YouTube prevention links,
 *       uploaded photo next to the diagnosis.
 */
import { useState, useEffect, useRef } from 'react'
import { DISEASE_KB } from '../App'
import { UI, HI_KB } from '../i18n'
import VideoLinks from './VideoLinks'

const CROP_ICONS = { Tomato: '🍅', Corn: '🌽', Potato: '🥔' }

function getDiseaseKey(crop, disease) {
  if (disease === 'Healthy') return `${crop}___healthy`
  return `${crop}___${disease.replace(/ /g, '_')}`
}

const SEVERITY_STYLE = {
  none:     { color: 'var(--ok-text)',     bg: 'var(--ok-bg)',     border: 'var(--ok-border)' },
  moderate: { color: 'var(--warn-text)',   bg: 'var(--warn-bg)',   border: 'var(--warn-border)' },
  severe:   { color: 'var(--danger-text)', bg: 'var(--danger-bg)', border: 'var(--danger-border)' },
}

export default function ResultCard({ prediction, remedy, isRemedyLoading, imageUrl, lang = 'en', onReset }) {
  const t = UI[lang]
  const { crop, disease, confidence, is_healthy, confidence_percent, low_confidence_warning, mock } = prediction
  const cropIcon      = CROP_ICONS[crop] || '🌿'
  const confidencePct = confidence_percent || `${(confidence * 100).toFixed(1)}%`
  const barClass      = is_healthy ? 'healthy' : 'diseased'

  // Knowledge base (English) + Hindi overlay
  const diseaseKey = getDiseaseKey(crop, disease)
  const kbEn = DISEASE_KB[diseaseKey] || null
  const kbHi = lang === 'hi' ? HI_KB[diseaseKey] : null
  const earlyStage = kbHi?.earlyStage ?? kbEn?.earlyStage ?? []
  const kbRemedies = kbHi?.practicalRemedies ?? kbEn?.practicalRemedies ?? []
  const referenceDesc = kbHi?.referenceDesc ?? kbEn?.referenceDesc

  const severity = kbEn?.severity || (is_healthy ? 'none' : 'moderate')
  const sevStyle = SEVERITY_STYLE[severity]

  const cropName    = t.crops[crop] || crop
  const diseaseName = kbHi?.name || disease

  // Backend remedy text is English only, so use it only in English mode
  const remedySteps = (() => {
    if (lang === 'en' && remedy?.remedy) return remedy.remedy.split('\n').filter((l) => l.trim())
    return kbRemedies
  })()

  const explanationText =
    (lang === 'en' && remedy?.explanation) ||
    (is_healthy ? t.explainHealthy(cropName) : t.explainDisease(diseaseName, cropName, severity === 'severe'))

  // ─── Text to speech ────────────────────────────────────────────────
  const [speaking, setSpeaking] = useState(false)
  const uttRef = useRef(null)

  const handleSpeak = () => {
    if (speaking) {
      window.speechSynthesis.cancel()
      setSpeaking(false)
      return
    }
    const text = t.speech(
      cropName, diseaseName, confidencePct,
      !is_healthy ? earlyStage[0] : '',
      remedySteps[0] ? remedySteps[0].replace(/^\d+[.)]\s*/, '') : ''
    )
    const utt = new SpeechSynthesisUtterance(text)
    utt.lang = t.speechLang
    utt.rate = 0.92
    utt.onend = () => setSpeaking(false)
    utt.onerror = () => setSpeaking(false)
    uttRef.current = utt
    window.speechSynthesis.cancel()
    window.speechSynthesis.speak(utt)
    setSpeaking(true)
  }

  // Stop speaking when unmounting or when the language is switched
  useEffect(() => {
    window.speechSynthesis?.cancel()
    setSpeaking(false)
    return () => window.speechSynthesis?.cancel()
  }, [lang])

  return (
    <div className="result-card glass-card">
      {mock && <div className="mock-banner">{t.mock}</div>}
      {low_confidence_warning && <div className="low-confidence-banner">⚠️ {low_confidence_warning}</div>}

      {/* Severity banner */}
      <div className="severity-banner" style={{ background: sevStyle.bg, border: `1px solid ${sevStyle.border}`, color: sevStyle.color }}>
        {t.sevBanner[severity]}
        {severity === 'severe' && <span className="severity-urgent">{t.urgent}</span>}
      </div>

      {/* Photo + diagnosis */}
      <div className={`result-hero ${imageUrl ? 'has-photo' : ''}`}>
        {imageUrl && (
          <div className="result-photo">
            <img src={imageUrl} alt={t.photo} />
            <span>{t.photo}</span>
          </div>
        )}
        <div className="result-hero-info">
          <div className="result-header">
            <div className="result-crop-icon">{cropIcon}</div>
            <div className="result-title">
              <div className="result-crop-name">{cropName}</div>
              <div className={`result-disease-name ${barClass}`}>{diseaseName}</div>
              <span className={`result-status-badge ${barClass}`}>
                {is_healthy ? t.badgeHealthy : t.badgeDisease}
              </span>
            </div>
          </div>

          <div className="confidence-section">
            <div className="confidence-label">
              <span>{t.confidence}</span>
              <span className="confidence-pct">{confidencePct}</span>
            </div>
            <div className="confidence-bar-track">
              <div className={`confidence-bar-fill ${barClass}`} style={{ width: confidencePct }} />
            </div>
          </div>
        </div>
      </div>

      <hr className="result-divider" />

      {/* Early stage */}
      {!is_healthy && earlyStage.length > 0 && (
        <div className="early-stage-section">
          <h3>{t.earlyTitle}</h3>
          <p className="early-stage-subtitle">{t.earlySub}</p>
          <ul className="early-stage-list">
            {earlyStage.map((sign, i) => (
              <li key={i} className="early-stage-item">
                <span className="early-stage-dot" />
                {sign}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Reference description */}
      {referenceDesc && (
        <div className="reference-section">
          <h3>{t.lookTitle}</h3>
          <div className="reference-box">
            <div className="reference-icon">{is_healthy ? '🌿' : severity === 'severe' ? '🍂' : '🍃'}</div>
            <div className="reference-content">
              <p className="reference-desc">{referenceDesc}</p>
              <p className="reference-tip">{t.lookTip}</p>
            </div>
          </div>
        </div>
      )}

      <hr className="result-divider" />

      {/* Diagnosis */}
      <div className="explanation-section">
        <h3>{t.diagTitle}</h3>
        <p className="explanation-text">{explanationText}</p>
      </div>

      {/* Remedies / care tips */}
      {!is_healthy && (
        <div className="remedy-section">
          <h3>{t.remediesTitle}</h3>
          {isRemedyLoading && remedySteps.length === 0 ? (
            <div className="remedy-loading"><div className="spinner" /><span>{t.fetching}</span></div>
          ) : remedySteps.length > 0 ? (
            <ol className="remedy-steps">
              {remedySteps.map((step, i) => (
                <li key={i} className="remedy-step">
                  <span className="step-number">{i + 1}</span>
                  <span>{step.replace(/^\d+[.)]\s*/, '')}</span>
                </li>
              ))}
            </ol>
          ) : null}
        </div>
      )}

      {is_healthy && kbRemedies.length > 0 && (
        <div className="remedy-section">
          <h3>{t.careTitle}</h3>
          <ol className="remedy-steps">
            {kbRemedies.map((tip, i) => (
              <li key={i} className="remedy-step">
                <span className="step-number">{i + 1}</span>
                <span>{tip}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* YouTube prevention videos */}
      {kbEn && <VideoLinks itemKey={diseaseKey} lang={lang} />}

      <hr className="result-divider" />

      {/* Model info */}
      <div className="model-info-section">
        <h3>{t.modelUsed}</h3>
        <div className="model-info-box">
          <div className="model-info-header">
            <span className="model-info-name">EfficientNet-B0</span>
            <span className="model-info-badge">{t.bestModel}</span>
          </div>
          <div className="model-info-stats">
            <div className="model-stat"><span className="stat-label">{t.testAcc}</span><span className="stat-value green">99.89%</span></div>
            <div className="model-stat"><span className="stat-label">{t.parameters}</span><span className="stat-value">4.7M</span></div>
            <div className="model-stat"><span className="stat-label">{t.vsResnet}</span><span className="stat-value green">+0.11%</span></div>
            <div className="model-stat"><span className="stat-label">{t.vsDense}</span><span className="stat-value">{t.tied}</span></div>
          </div>
          <p className="model-info-why">{t.modelWhy}</p>
        </div>
      </div>

      {/* Audio + reset */}
      <div className="audio-section">
        <button className={`audio-btn ${speaking ? 'speaking' : ''}`} onClick={handleSpeak}>
          {speaking ? t.speaking : t.listen}
        </button>
        {speaking && <button className="audio-stop-btn" onClick={handleSpeak}>{t.stop}</button>}
      </div>

      <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
        <button className="try-again-btn" onClick={onReset}>{t.another}</button>
      </div>
    </div>
  )
}
