/**
 * App.jsx — AgriPulse AI Main Application (v2)
 * New features:
 *   - Early stage detection warnings
 *   - Practical step-by-step remedies
 *   - Reference image comparison
 *   - Model selector with explanation of why EfficientNet-B0 wins
 *   - Tomato & Corn (PlantVillage, 14 classes)
 */
import { useState, useCallback, useEffect, useMemo } from 'react'
import ImageUploader from './components/ImageUploader'
import ResultCard    from './components/ResultCard'
import VideoLinks    from './components/VideoLinks'
import { UI, HI_KB } from './i18n'

const API_BASE = 'http://localhost:8000'

const STATE = {
  IDLE:            'idle',
  LOADING_PREDICT: 'loading_predict',
  LOADING_REMEDY:  'loading_remedy',
  RESULT:          'result',
  ERROR:           'error',
}

// ─── Disease Knowledge Base ───────────────────────────────────────────────────
// Early stage signs, practical remedies, reference image descriptions
export const DISEASE_KB = {
  'Corn___Cercospora_leaf_spot Gray_leaf_spot': {
    earlyStage: [
      'Small tan to gray rectangular spots on lower leaves, running parallel to the veins',
      'Spots have a thin yellow halo and are limited by the leaf veins, giving a blocky look',
      'Lesions grow and join together, so large parts of the leaf turn gray and dry',
      'Worst in warm, humid weather with heavy dew or frequent rain',
    ],
    practicalRemedies: [
      'Spray Azoxystrobin + Propiconazole or Mancozeb 75% WP (2.5g/L water) at first signs',
      'Rotate with a non-cereal crop — the fungus survives in old corn residue',
      'Bury or remove crop residue after harvest',
      'Avoid very dense planting — good air flow lets leaves dry faster',
      'Use resistant or tolerant hybrids in the next season',
      'Avoid excess nitrogen, which makes the canopy denser and more humid',
    ],
    referenceDesc: 'Narrow rectangular gray-tan lesions between leaf veins on lower leaves',
    severity: 'severe',
  },
  'Corn___Common_rust': {
    earlyStage: [
      'Small round to oval reddish-brown pustules scattered on both sides of the leaf',
      'Pustules feel powdery and leave rusty-orange dust on your fingers when rubbed',
      'Pustules later turn dark brown-black as the leaf ages',
      'Spreads fastest in cool, damp weather',
    ],
    practicalRemedies: [
      'Spray Propiconazole 25 EC (1ml/L) or Mancozeb (2.5g/L) when pustules first appear',
      'Check fields every 3–4 days in cool, humid weather — it spreads quickly',
      'Plant rust-resistant hybrids in the next season',
      'Avoid late planting, which exposes young plants to more rust spores',
      'Remove badly infected plants in small plots to slow the spread',
    ],
    referenceDesc: 'Scattered rusty reddish-brown powdery pustules on both leaf surfaces',
    severity: 'moderate',
  },
  'Corn___Northern_Leaf_Blight': {
    earlyStage: [
      'Long, cigar-shaped gray-green lesions, 2.5–15 cm, usually first on lower leaves',
      'Lesions turn tan or brown with pointed ends as they grow',
      'In damp weather, dark spore growth appears on the lesions',
      'Many lesions can join together and burn the whole leaf',
    ],
    practicalRemedies: [
      'Spray Azoxystrobin + Propiconazole or Mancozeb (2.5g/L) at first signs, before tasseling',
      'Rotate crops — avoid corn after corn in the same field',
      'Bury or remove infected residue after harvest',
      'Plant resistant hybrids in the next season',
      'Avoid overhead irrigation late in the day, which keeps leaves wet overnight',
    ],
    referenceDesc: 'Long cigar-shaped gray-green to tan lesions with pointed ends',
    severity: 'severe',
  },
  'Corn___healthy': {
    earlyStage: [],
    practicalRemedies: [
      'Scout the field every 3–4 days, especially the lower leaves',
      'Use balanced fertilizer — avoid too much nitrogen',
      'Keep the field weed-free to cut humidity and pests',
      'Rotate crops each season to reduce disease build-up in the soil',
    ],
    referenceDesc: 'Uniform deep green leaves with no spots, pustules or lesions',
    severity: 'none',
  },
  'Potato___Early_blight': {
    earlyStage: [
      'Small dark-brown spots (2–3mm) with yellow halo on lower leaves',
      'Spots have concentric rings — like a target / bullseye pattern',
      'Usually appears first on older/lower leaves, not young shoots',
      'Leaves may feel slightly leathery before spots fully form',
    ],
    practicalRemedies: [
      'Remove and burn infected leaves immediately — do not compost',
      'Apply Mancozeb 75% WP (2.5g/L water) every 7–10 days',
      'Avoid overhead watering — water at soil level in the morning',
      'Maintain spacing between plants for good air circulation',
      'Apply copper-based fungicide as preventive spray after rains',
      'Rotate crops — do not plant potatoes in the same spot next year',
    ],
    referenceDesc: 'Brown circular spots with yellow rings on lower leaves, bullseye pattern',
    severity: 'moderate',
  },
  'Potato___Late_blight': {
    earlyStage: [
      'Water-soaked pale green patches near leaf tips/edges',
      'White fuzzy mold visible on undersides of leaves in humid mornings',
      'Dark brown-black lesions spread rapidly — can kill leaf in 3–5 days',
      'Stems show dark brown streaks if you scratch the surface',
    ],
    practicalRemedies: [
      'Act immediately — Late Blight spreads in 3–5 days in wet weather',
      'Spray Metalaxyl + Mancozeb (Ridomil Gold) every 5–7 days',
      'Remove all infected plant parts and burn — do not leave on soil',
      'Avoid working in fields when plants are wet (spreads spores)',
      'Hill up soil around stems to protect tubers from infection',
      'Harvest early if infection is severe — infected tubers rot in storage',
    ],
    referenceDesc: 'Dark water-soaked lesions with white mold on leaf undersides',
    severity: 'severe',
  },
  'Potato___healthy': {
    earlyStage: [],
    practicalRemedies: [
      'Continue regular monitoring — inspect leaves every 3–4 days',
      'Maintain balanced fertilization — avoid excess nitrogen',
      'Keep field weed-free to reduce disease reservoir',
      'Apply preventive copper spray before monsoon season',
    ],
    referenceDesc: 'Deep green uniform leaves, no spots or lesions',
    severity: 'none',
  },
  'Tomato___Bacterial_spot': {
    earlyStage: [
      'Tiny water-soaked spots (1–2mm) on young leaves and stems',
      'Spots become dark brown with yellow margins over 2–3 days',
      'Fruit shows raised, rough, scab-like spots with dark centers',
      'Worse after rain or overhead irrigation — bacteria spread in water',
    ],
    practicalRemedies: [
      'Spray copper hydroxide (Kocide 3000) every 7 days',
      'Remove heavily infected leaves — sanitize tools between plants',
      'Switch to drip irrigation — avoid wetting leaves',
      'Apply fixed copper + mancozeb tank mix for better control',
      'Do not save seeds from infected plants',
      'Destroy crop debris after harvest to prevent soil carryover',
    ],
    referenceDesc: 'Small dark spots with yellow halo on leaves and scabby fruit spots',
    severity: 'moderate',
  },
  'Tomato___Early_blight': {
    earlyStage: [
      'Small dark spots on oldest (lowest) leaves first — 3–5mm diameter',
      'Classic concentric ring / target-board pattern on spots',
      'Yellow area surrounds each spot before leaf turns brown',
      'Defoliation starts from bottom of plant upward',
    ],
    practicalRemedies: [
      'Remove and dispose all affected lower leaves immediately',
      'Apply Chlorothalonil or Mancozeb fungicide every 7–10 days',
      'Mulch around plant base — stops soil splash carrying spores',
      'Water in morning at soil level — keep foliage dry',
      'Stake plants to improve airflow around leaves',
      'Avoid excessive nitrogen fertilizer — promotes lush growth disease loves',
    ],
    referenceDesc: 'Bullseye dark spots on lower leaves, yellow halo, bottom-up defoliation',
    severity: 'moderate',
  },
  'Tomato___Late_blight': {
    earlyStage: [
      'Pale green/gray water-soaked patches — usually at leaf margins',
      'White downy mold on leaf undersides in early morning',
      'Lesions turn dark brown-black quickly in cool wet weather',
      'Brown streaks on stems — especially after rain',
    ],
    practicalRemedies: [
      'URGENT — spray Metalaxyl + Mancozeb (Ridomil) immediately',
      'Remove and burn all infected tissue — disease spreads in hours',
      'Spray every 5 days if weather is cool (15–20°C) and wet',
      'Avoid overhead irrigation completely',
      'Apply preventive spray before forecast rainy periods',
      'Destroy entire plant if more than 50% infected',
    ],
    referenceDesc: 'Dark water-soaked patches, white mold underside, rapid brown-black spread',
    severity: 'severe',
  },
  'Tomato___Leaf_Mold': {
    earlyStage: [
      'Pale yellow-green spots on upper leaf surface — no clear margins',
      'Olive-green to gray-brown fuzzy growth on leaf underside',
      'Starts on older inner leaves with poor air circulation',
      'Infected leaves curl and wither from edges inward',
    ],
    practicalRemedies: [
      'Improve ventilation — prune excess leaves for airflow',
      'Reduce humidity — avoid evening watering',
      'Apply Chlorothalonil or Copper fungicide every 7 days',
      'Remove infected leaves and burn — do not compost',
      'Use resistant varieties in next season planting',
      'Space plants adequately — minimum 60cm between plants',
    ],
    referenceDesc: 'Yellow patches on top, olive fuzzy growth underneath, inner leaves affected',
    severity: 'moderate',
  },
  'Tomato___Septoria_leaf_spot': {
    earlyStage: [
      'Very small circular spots (2–3mm) with dark border and tan/gray center',
      'Tiny black dots visible inside spots (pycnidia — fungal fruiting bodies)',
      'First appears on lowest leaves after fruit set',
      'Spots very numerous — dozens per leaf before defoliation',
    ],
    practicalRemedies: [
      'Apply Chlorothalonil or Mancozeb at first sign of spots',
      'Remove and destroy infected lower leaves immediately',
      'Avoid working among wet plants — spreads by contact',
      'Mulch soil surface to prevent splash dispersal of spores',
      'Spray every 10 days throughout growing season',
      'Practice 2-year crop rotation — fungus survives in soil',
    ],
    referenceDesc: 'Many tiny spots with dark border and pale center, black dots inside spots',
    severity: 'moderate',
  },
  'Tomato___Spider_mites Two-spotted_spider_mite': {
    earlyStage: [
      'Tiny white/yellow stippling on upper leaf surface — looks like dust',
      'Fine webbing on leaf undersides and between leaves',
      'Leaves turn bronze/yellow and dry out — worse in hot dry weather',
      'Mites visible under magnification — tiny moving dots on underside',
    ],
    practicalRemedies: [
      'Spray water forcefully on leaf undersides to knock off mites',
      'Apply Abamectin or Bifenazate miticide — NOT regular insecticide',
      'Increase humidity around plants — mites thrive in dry conditions',
      'Introduce predatory mites (Phytoseiulus persimilis) if available',
      'Remove severely infested leaves and burn',
      'Avoid dusty conditions — dust suppresses natural predators',
    ],
    referenceDesc: 'Yellow stippling on leaves, fine webbing visible, bronze discoloration',
    severity: 'moderate',
  },
  'Tomato___Target_Spot': {
    earlyStage: [
      'Small brown spots with yellow halo — similar to early blight',
      'Spots have concentric rings but less distinct than early blight',
      'Affects leaves, stems, and fruit — look for sunken fruit lesions',
      'Favored by warm humid conditions — spreads rapidly',
    ],
    practicalRemedies: [
      'Apply Azoxystrobin or Chlorothalonil fungicide every 7–14 days',
      'Remove infected plant material from field',
      'Avoid dense planting — improve air circulation',
      'Water at base of plants in morning only',
      'Sanitize stakes and tools between plants',
    ],
    referenceDesc: 'Brown target-ring spots on leaves and sunken lesions on fruit',
    severity: 'moderate',
  },
  'Tomato___Tomato_Yellow_Leaf_Curl_Virus': {
    earlyStage: [
      'Young leaves curl upward and inward — like a cupped shape',
      'Leaves become yellow (chlorotic) — especially at margins',
      'Plant stunted — internodes shortened, compact bushy appearance',
      'Transmitted by whiteflies — check leaf undersides for whiteflies',
    ],
    practicalRemedies: [
      'No cure — infected plants must be removed and destroyed',
      'Control whitefly vector: spray Imidacloprid or Thiamethoxam',
      'Use yellow sticky traps to monitor and reduce whitefly population',
      'Plant virus-resistant tomato varieties (e.g. TY varieties)',
      'Use reflective mulch — repels whiteflies from landing',
      'Remove infected plants immediately to prevent spread to others',
    ],
    referenceDesc: 'Upward leaf curl, yellow margins, stunted plant, whiteflies on undersides',
    severity: 'severe',
  },
  'Tomato___Tomato_mosaic_virus': {
    earlyStage: [
      'Mottled light/dark green mosaic pattern on young leaves',
      'Leaves may appear blistered or puckered/distorted',
      'Growth is stunted — new growth looks abnormal',
      'Spreads through contact — tools, hands, infected seed',
    ],
    practicalRemedies: [
      'No chemical cure — remove and destroy infected plants',
      'Wash hands with soap before and after handling plants',
      'Disinfect tools with 10% bleach solution between plants',
      'Do not smoke near plants — TMV survives in tobacco products',
      'Use certified disease-free seed for next planting',
      'Control aphids — they can spread virus between plants',
    ],
    referenceDesc: 'Mosaic light-dark green pattern, puckered distorted leaves, stunted growth',
    severity: 'severe',
  },
  'Tomato___healthy': {
    earlyStage: [],
    practicalRemedies: [
      'Monitor plants every 3–4 days — early detection is key',
      'Maintain consistent watering — avoid drought stress',
      'Apply balanced NPK fertilizer as per growth stage',
      'Check undersides of leaves for early pest/disease signs',
    ],
    referenceDesc: 'Deep green healthy leaves, no spots, lesions or discoloration',
    severity: 'none',
  },
}

// ─── Model Info ───────────────────────────────────────────────────────────────
// Fallback only — the live numbers come from GET /models (backend/comparison_results.json).
// Shown if the backend is unreachable. Corn+Tomato run, 14 classes.
export const MODEL_INFO = {
  efficientnet_b0: { label: 'EfficientNet-B0', valAcc: 98.23, testAcc: 98.05, params: '4.7M',  time: '2594s', why: 'Best choice: highest test accuracy with the fewest parameters.', winner: true },
  resnet18:        { label: 'ResNet18',        valAcc: 97.59, testAcc: 97.36, params: '11.4M', time: '2580s', why: '', winner: false },
  resnet50:        { label: 'ResNet50',        valAcc: 97.68, testAcc: 97.14, params: '24.6M', time: '2895s', why: '', winner: false },
  densenet121:     { label: 'DenseNet121',     valAcc: 97.23, testAcc: 96.27, params: '7.5M',  time: '2835s', why: '', winner: false },
}


// ─── Disease library (browse section) ─────────────────────────────────────────
const CROP_ICON = { Tomato: '🍅', Corn: '🌽' }
const CHIPS = ['All', 'Tomato', 'Corn', 'Healthy', 'Diseased', 'Severe']

// Returns an item's text in the chosen language (falls back to English)
function localize(item, lang) {
  if (lang !== 'hi') return item
  const hi = HI_KB[item.key]
  if (!hi) return item
  return {
    ...item,
    name: hi.name,
    referenceDesc: hi.referenceDesc || item.referenceDesc,
    earlyStage: hi.earlyStage?.length ? hi.earlyStage : item.earlyStage,
    practicalRemedies: hi.practicalRemedies?.length ? hi.practicalRemedies : item.practicalRemedies,
  }
}

const LIBRARY = Object.entries(DISEASE_KB)
  .filter(([key]) => /^(Tomato|Corn)___/.test(key))
  .map(([key, kb]) => {
    const [crop, rest] = key.split('___')
    const healthy = /healthy/i.test(rest)
    return { key, crop, healthy, name: healthy ? 'Healthy' : rest.replace(/_/g, ' '), ...kb }
  })

// Real leaf photo for a disease. Looks for /diseases/<slug>.jpg in the public folder
// and falls back to the crop emoji if the photo is missing.
export const diseaseSlug = (key) =>
  key.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')

// ─── Latest-scan thumbnails ───────────────────────────────────────────────────
// After every scan, a small copy of the photo is uploaded to the backend, which saves it
// as a file (backend/saved_scans/<disease>.jpg). The library card for that disease then
// shows it, and it stays there permanently — even after refresh or restart.

// Same key format the ResultCard uses, e.g. "Tomato___Early_blight" / "Corn___healthy"
// Both sides are normalised so names with spaces/hyphens still match their library card
const normKey = (k) => k.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '')
const scanKey = (crop, disease) =>
  normKey(disease === 'Healthy' ? `${crop}___healthy` : `${crop}___${disease}`)

// Shrink the photo to ~400px wide JPEG so it stays small in storage
function makeThumbnail(file, maxW = 400) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => {
      const scale  = Math.min(1, maxW / img.width)
      const canvas = document.createElement('canvas')
      canvas.width  = Math.round(img.width * scale)
      canvas.height = Math.round(img.height * scale)
      canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height)
      URL.revokeObjectURL(url)
      resolve(canvas.toDataURL('image/jpeg', 0.75))
    }
    img.onerror = () => { URL.revokeObjectURL(url); reject(new Error('thumbnail failed')) }
    img.src = url
  })
}

function DiseaseThumb({ itemKey, fallback, className = '', scan = null }) {
  const [failed, setFailed] = useState(false)
  if (scan) {
    return <img className={`disease-photo ${className}`} src={scan} alt="" />
  }
  if (failed) return <span className="thumb-emoji">{fallback}</span>
  return (
    <img
      className={`disease-photo ${className}`}
      src={`/diseases/${diseaseSlug(itemKey)}.jpg`}
      alt=""
      loading="lazy"
      onError={() => setFailed(true)}
    />
  )
}

function DiseaseModal({ item, lang, scans = {}, onClose }) {
  const t = UI[lang]
  const it = localize(item, lang)
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Close">×</button>
        <div className="modal-head">
          <span className="modal-icon"><DiseaseThumb itemKey={it.key} fallback={CROP_ICON[it.crop]} className="modal-photo" scan={scans[normKey(it.key)]} /></span>
          <div>
            <div className="result-crop-name">{t.crops[it.crop]}</div>
            <h2 className="modal-title">{it.healthy ? t.healthyLeaf : it.name}</h2>
            <span className={`sev-pill sev-${it.severity}`}>{t.sev[it.severity]}</span>
          </div>
        </div>
        <p className="modal-desc">{it.referenceDesc}</p>

        {it.earlyStage?.length > 0 && (
          <>
            <h3 className="modal-h">{t.earlySigns}</h3>
            <ul className="modal-list">{it.earlyStage.map((x, i) => <li key={i}>{x}</li>)}</ul>
          </>
        )}
        <h3 className="modal-h">{it.healthy ? t.careTips : t.whatToDo}</h3>
        <ol className="modal-list">{it.practicalRemedies.map((x, i) => <li key={i}>{x}</li>)}</ol>

        <VideoLinks itemKey={it.key} lang={lang} />
      </div>
    </div>
  )
}

export default function App() {
  const [appState,     setAppState]     = useState(STATE.IDLE)
  const [selectedFile, setSelectedFile] = useState(null)
  const [prediction,   setPrediction]   = useState(null)
  const [remedy,       setRemedy]       = useState(null)
  const [errorMsg,     setErrorMsg]     = useState('')
  const [activeModel,  setActiveModel]  = useState('efficientnet_b0')
  const [showModelPanel, setShowModelPanel] = useState(false)
  const [modelInfo,   setModelInfo]   = useState(MODEL_INFO)
  const [category,    setCategory]    = useState('All')
  const [query,       setQuery]       = useState('')
  const [openItem,    setOpenItem]    = useState(null)
  const [previewUrl,  setPreviewUrl]  = useState(null)
  const [scans,       setScans]       = useState({})
  const [lang, setLang] = useState(() => {
    try { return localStorage.getItem('agripulse-lang') === 'hi' ? 'hi' : 'en' } catch { return 'en' }
  })
  const t = UI[lang]

  useEffect(() => {
    document.documentElement.lang = lang
    try { localStorage.setItem('agripulse-lang', lang) } catch {}
  }, [lang])

  // Keep a preview URL of the chosen photo so the result can show it
  useEffect(() => {
    if (!selectedFile) { setPreviewUrl(null); return }
    const url = URL.createObjectURL(selectedFile)
    setPreviewUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [selectedFile])

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase()
    return LIBRARY.filter((d) => {
      if ((category === 'Tomato' || category === 'Corn') && d.crop !== category) return false
      if (category === 'Healthy'  && !d.healthy) return false
      if (category === 'Diseased' &&  d.healthy) return false
      if (category === 'Severe'   && d.severity !== 'severe') return false
      const hi = HI_KB[d.key]
      const hay = `${d.crop} ${d.name} ${d.referenceDesc} ${UI.hi.crops[d.crop]} ${hi?.name || ''} ${hi?.referenceDesc || ''}`
      return !q || hay.toLowerCase().includes(q)
    })
  }, [category, query])

  // Load the saved latest-scan photos from the backend
  useEffect(() => {
    fetch(`${API_BASE}/scans`)
      .then(r => (r.ok ? r.json() : Promise.reject()))
      .then(list => {
        const urls = {}
        Object.entries(list).forEach(([key, v]) => { urls[key] = `${API_BASE}/scans/${key}.jpg?v=${v}` })
        setScans(urls)
      })
      .catch(() => {})   // backend without the scans route: cards keep their default photos
  }, [])

  // Load the architecture comparison from the backend (comparison_results.json)
  useEffect(() => {
    fetch(`${API_BASE}/models`)
      .then(r => (r.ok ? r.json() : Promise.reject()))
      .then(d => {
        setModelInfo(d.models)
        setActiveModel(d.best)
      })
      .catch(() => {})   // keep fallback values
  }, [])

  const handleAnalyze = useCallback(async () => {
    if (!selectedFile) return
    setAppState(STATE.LOADING_PREDICT)
    setErrorMsg('')
    setPrediction(null)
    setRemedy(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const res = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        body:   formData,
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `Prediction failed (${res.status})`)
      }

      const predData = await res.json()
      setPrediction(predData)

      // Save this scan as the latest thumbnail for the predicted disease
      makeThumbnail(selectedFile)
        .then(async (thumb) => {
          const key = scanKey(predData.crop, predData.disease)
          setScans((prev) => ({ ...prev, [key]: thumb }))        // show it immediately
          const body = new FormData()
          body.append('crop', predData.crop)
          body.append('disease', predData.disease)
          body.append('file', await (await fetch(thumb)).blob(), `${key}.jpg`)
          const up = await fetch(`${API_BASE}/scans`, { method: 'POST', body })
          if (up.ok) setScans((prev) => ({ ...prev, [key]: `${API_BASE}/scans/${key}.jpg?v=${Date.now()}` }))
        })
        .catch(() => {})
      setAppState(STATE.LOADING_REMEDY)
      fetchRemedy(predData.crop, predData.disease)

    } catch (err) {
      setErrorMsg(
        err.message.includes('fetch')
          ? '⚠️ Cannot connect to backend. Make sure FastAPI server is running on port 8000.'
          : err.message
      )
      setAppState(STATE.ERROR)
    }
  }, [selectedFile])

  const fetchRemedy = async (crop, disease) => {
    try {
      const res = await fetch(`${API_BASE}/remedy`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ crop, disease }),
      })
      setRemedy(res.ok ? await res.json() : { explanation: '', remedy: '' })
    } catch {
      setRemedy({ explanation: '', remedy: '' })
    } finally {
      setAppState(STATE.RESULT)
    }
  }

  const handleReset = () => {
    setAppState(STATE.IDLE)
    setSelectedFile(null)
    setPrediction(null)
    setRemedy(null)
    setErrorMsg('')
  }

  const showResult = (appState === STATE.RESULT || appState === STATE.LOADING_REMEDY) && prediction
  const showLibrary = appState === STATE.IDLE

  return (
    <div className="app">
      {/* ─── Top bar (logo · search · model) ─────────────────────── */}
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand" onClick={handleReset} role="button" tabIndex={0}>
            <span className="brand-icon">🌿</span>
            <span className="brand-name">{t.brand}</span>
          </div>

          <div className="search-box">
            <span className="search-icon">🔎</span>
            <input
              type="search"
              placeholder={t.searchPh}
              value={query}
              onChange={(e) => { setQuery(e.target.value); if (appState !== STATE.IDLE) handleReset() }}
            />
          </div>

          <div className="lang-switch" role="group" aria-label="Language">
            <button className={lang === 'en' ? 'active' : ''} onClick={() => setLang('en')}>EN</button>
            <button className={lang === 'hi' ? 'active' : ''} onClick={() => setLang('hi')}>हिंदी</button>
          </div>

          <button className="model-toggle-btn topbar-model" onClick={() => setShowModelPanel((p) => !p)}>
            🧠 {modelInfo[activeModel].label}
            <span className="toggle-arrow">{showModelPanel ? '▲' : '▼'}</span>
          </button>
        </div>

        {/* Category chips */}
        <div className="chips-row">
          {CHIPS.map((c) => (
            <button
              key={c}
              className={`chip ${category === c ? 'active' : ''}`}
              onClick={() => { setCategory(c); if (appState !== STATE.IDLE) handleReset() }}
            >
              {c === 'Tomato' ? '🍅 ' : c === 'Corn' ? '🌽 ' : ''}{t.chips[c]}
            </button>
          ))}
        </div>
      </header>

      {showModelPanel && (
        <div className="model-panel">
          <p className="model-panel-title">{t.modelsCompare}</p>
          <div className="model-grid">
            {Object.entries(modelInfo).map(([key, m]) => (
              <div
                key={key}
                className={`model-card ${activeModel === key ? 'active' : ''} ${m.winner ? 'winner' : ''}`}
                onClick={() => setActiveModel(key)}
              >
                {m.winner && <span className="winner-badge">{t.best}</span>}
                <div className="model-name">{m.label}</div>
                <div className="model-stats">
                  <span>{t.test}: <strong>{m.testAcc}%</strong></span>
                  <span>{t.params}: <strong>{m.params}</strong></span>
                </div>
                <p className="model-why">{m.why}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── Main ────────────────────────────────────────────────── */}
      <main className="main-area">
        {(appState === STATE.IDLE || appState === STATE.LOADING_PREDICT) && (
          <section className="scan-section">
            <div className="scan-intro">
              <h1>{t.scanTitle}</h1>
              <p>{t.scanDesc}</p>
              <ul className="scan-points">
                {t.points.map((p) => <li key={p}>{p}</li>)}
              </ul>
            </div>
            <div className="glass-card scan-card">
              <ImageUploader
                onImageSelect={setSelectedFile}
                selectedFile={selectedFile}
                onAnalyze={handleAnalyze}
                isLoading={appState === STATE.LOADING_PREDICT}
                lang={lang}
              />
            </div>
          </section>
        )}

        {showResult && (
          <ResultCard
            prediction={prediction}
            remedy={appState === STATE.RESULT ? remedy : null}
            isRemedyLoading={appState === STATE.LOADING_REMEDY}
            imageUrl={previewUrl}
            lang={lang}
            onReset={handleReset}
          />
        )}

        {appState === STATE.ERROR && (
          <div className="glass-card" style={{ textAlign: 'center', padding: '2.5rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>😔</div>
            <h2 style={{ color: 'var(--danger-text)', marginBottom: '0.75rem', fontFamily: 'var(--font-display)' }}>
              {t.errTitle}
            </h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', lineHeight: 1.6 }}>{errorMsg}</p>
            <button className="try-again-btn" onClick={handleReset}>{t.tryAgain}</button>
          </div>
        )}

        {/* ─── Browse library (Amazon-style grid) ─────────────────── */}
        {showLibrary && (
          <section className="library">
            <div className="crop-tiles">
              {['Tomato', 'Corn'].map((c) => (
                <button
                  key={c}
                  className={`crop-tile ${category === c ? 'active' : ''}`}
                  onClick={() => setCategory(category === c ? 'All' : c)}
                >
                  <span className="crop-tile-icon">{CROP_ICON[c]}</span>
                  <span>
                    <strong>{t.crops[c]}</strong>
                    <small>{LIBRARY.filter((d) => d.crop === c).length} {t.conditions}</small>
                  </span>
                </button>
              ))}
            </div>

            <div className="library-head">
              <h2>{t.browse}</h2>
              <span>{t.results(visible.length)}</span>
            </div>

            {visible.length === 0 ? (
              <p className="library-empty">{t.empty(query)}</p>
            ) : (
              <div className="lib-grid">
                {visible.map((raw) => {
                  const d = localize(raw, lang)
                  return (
                  <button key={d.key} className="lib-card" onClick={() => setOpenItem(raw)}>
                    <div className={`lib-thumb sev-bg-${d.severity}`}><DiseaseThumb itemKey={d.key} fallback={CROP_ICON[d.crop]} scan={scans[normKey(d.key)]} /></div>
                    <div className="lib-body">
                      <span className="lib-crop">{t.crops[d.crop]}</span>
                      <span className="lib-name">{d.healthy ? t.healthyLeaf : d.name}</span>
                      <span className={`sev-pill sev-${d.severity}`}>{t.sev[d.severity]}</span>
                    </div>
                  </button>
                  )
                })}
              </div>
            )}
          </section>
        )}
      </main>

      {openItem && <DiseaseModal item={openItem} lang={lang} scans={scans} onClose={() => setOpenItem(null)} />}

      {/* ─── Footer ──────────────────────────────────────────────── */}
      <footer className="app-footer">
        <p>{t.footer1}</p>
        <p style={{ marginTop: '0.3rem' }}>
          {t.footer2(modelInfo[activeModel].label)}
        </p>
      </footer>
    </div>
  )
}
