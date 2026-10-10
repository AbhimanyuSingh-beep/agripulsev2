/**
 * i18n.js — English / Hindi text for AgriPulse AI
 * - UI:      every label shown on screen
 * - HI_KB:   Hindi disease names, descriptions, early signs, remedies
 *            (same item order / count as DISEASE_KB in App.jsx)
 * - ytLinks: YouTube search links for prevention / treatment videos
 */

export const CROP_HI = { Tomato: 'टमाटर', Corn: 'मक्का' }

export const UI = {
  en: {
    brand: 'AgriPulse AI',
    searchPh: 'Search a disease or crop, e.g. late blight',
    chips: { All: 'All', Tomato: 'Tomato', Corn: 'Corn', Healthy: 'Healthy', Diseased: 'Diseased', Severe: 'Severe' },
    crops: { Tomato: 'Tomato', Corn: 'Corn' },
    hindiSwitch: 'हिंदी',
    scanTitle: 'Scan a leaf. Get a diagnosis.',
    scanDesc: 'Upload a photo of a Tomato or Corn leaf for an instant disease check, remedies and a spoken summary.',
    points: ['📸 Single leaf, plain background works best', '⚡ Result in a few seconds', '🔊 Listen to the advice aloud'],
    conditions: 'conditions',
    browse: 'Browse conditions',
    results: (n) => `${n} result${n === 1 ? '' : 's'}`,
    empty: (q) => (q ? `Nothing matches “${q}”. Try another word or pick All.` : 'Nothing to show here.'),
    sev: { none: '✅ Healthy', moderate: '⚠️ Moderate', severe: '🚨 Severe' },
    sevBanner: { none: '✅ Healthy', moderate: '⚠️ Moderate Risk', severe: '🚨 Severe — Act Now' },
    healthyLeaf: 'Healthy leaf',
    earlySigns: '🔍 Early warning signs',
    whatToDo: '💊 What to do',
    careTips: '🌱 Care tips',
    modelsCompare: 'Compare all 4 architectures',
    best: '⭐ Best',
    test: 'Test',
    params: 'Params',
    errTitle: 'Analysis Failed',
    tryAgain: '↩ Try Again',
    footer1: 'AgriPulse AI · Crop Health Intelligence Module · College Exhibition Project',
    footer2: (m) => `Model: ${m} · Dataset: PlantVillage · Supports Tomato & Corn`,

    // uploader
    uploadTitle: '🌿 Upload a Crop Leaf Photo',
    dragDrop: 'Drag & drop your leaf photo here',
    or: 'or',
    browseFiles: 'browse files',
    formats: 'JPEG · PNG · WebP · Max 10 MB',
    camera: '📷 Take Photo with Camera',
    supports: 'Supports',
    analyze: '🔬 Analyze Leaf',
    analyzing: 'Analyzing',
    removeImage: 'Remove image',

    // result
    mock: '⚠️ Demo mode — no real model loaded. Showing sample output.',
    urgent: 'Treat within 24–48 hours',
    photo: '📷 Your photo',
    badgeHealthy: '✓ Healthy',
    badgeDisease: '⚠ Disease Detected',
    confidence: 'AI Confidence',
    earlyTitle: '🔍 Early Stage Warning Signs',
    earlySub: 'Check your plant for these early indicators — catching it sooner means easier treatment:',
    lookTitle: '🖼️ What This Disease Looks Like',
    lookTip: 'Compare your leaf against this description. If unsure, take another photo in natural light against a plain background for a more accurate diagnosis.',
    diagTitle: '🧬 Diagnosis',
    remediesTitle: '💊 Practical Remedies',
    fetching: 'Fetching treatment plan…',
    careTitle: '🌱 Preventive Care Tips',
    explainHealthy: (crop) => `Your ${crop} plant looks healthy! Continue regular monitoring and preventive care.`,
    explainDisease: (disease, crop, severe) =>
      `${disease} detected on ${crop}. ${severe ? 'This requires immediate action.' : 'Early treatment recommended.'}`,
    videosTitle: '📺 Prevention videos on YouTube',
    videosNote: 'These open YouTube searches, so you always see the newest videos.',
    vidPrev: 'Prevention tips',
    vidTreat: 'Treatment & control',
    vidOther: 'Prevention in Hindi (हिंदी में)',
    modelUsed: '🧠 Model Used',
    bestModel: '⭐ Best Model',
    testAcc: 'Test Accuracy',
    parameters: 'Parameters',
    vsResnet: 'vs ResNet18',
    vsDense: 'vs DenseNet121',
    tied: 'Tied, 2x lighter',
    modelWhy: 'EfficientNet-B0 was selected because it achieves the highest test accuracy (99.89%) with the fewest parameters (4.7M) among all 4 trained architectures — making it the fastest and most efficient choice for real-time farmer use.',
    listen: '🔊 Listen to Diagnosis',
    speaking: '🔊 Speaking…',
    stop: '⏹ Stop',
    another: '↩ Analyze Another Leaf',
    speech: (crop, disease, pct, early, first) =>
      `AgriPulse diagnosis for ${crop}: ${disease}. Confidence: ${pct}.` +
      (early ? ` Early warning signs: ${early}.` : '') +
      (first ? ` First action: ${first}.` : ''),
    speechLang: 'en-IN',
  },

  hi: {
    brand: 'एग्रीपल्स AI',
    searchPh: 'रोग या फसल खोजें, जैसे पछेती झुलसा',
    chips: { All: 'सभी', Tomato: 'टमाटर', Corn: 'मक्का', Healthy: 'स्वस्थ', Diseased: 'रोगग्रस्त', Severe: 'गंभीर' },
    crops: { Tomato: 'टमाटर', Corn: 'मक्का' },
    hindiSwitch: 'हिंदी',
    scanTitle: 'पत्ती स्कैन करें, तुरंत जाँच पाएँ।',
    scanDesc: 'टमाटर या मक्का की पत्ती की फोटो अपलोड करें और रोग की जाँच, इलाज और बोलकर सुनाई गई सलाह पाएँ।',
    points: ['📸 एक पत्ती की साफ़ पृष्ठभूमि वाली फोटो सबसे अच्छी', '⚡ कुछ ही सेकंड में नतीजा', '🔊 सलाह बोलकर सुनें'],
    conditions: 'स्थितियाँ',
    browse: 'रोग देखें',
    results: (n) => `${n} नतीजे`,
    empty: (q) => (q ? `“${q}” से कुछ नहीं मिला। कोई और शब्द आज़माएँ या सभी चुनें।` : 'यहाँ दिखाने के लिए कुछ नहीं है।'),
    sev: { none: '✅ स्वस्थ', moderate: '⚠️ मध्यम', severe: '🚨 गंभीर' },
    sevBanner: { none: '✅ स्वस्थ', moderate: '⚠️ मध्यम जोखिम', severe: '🚨 गंभीर — तुरंत कार्रवाई करें' },
    healthyLeaf: 'स्वस्थ पत्ती',
    earlySigns: '🔍 शुरुआती चेतावनी के संकेत',
    whatToDo: '💊 क्या करें',
    careTips: '🌱 देखभाल के सुझाव',
    modelsCompare: 'सभी 4 मॉडल की तुलना',
    best: '⭐ सर्वश्रेष्ठ',
    test: 'टेस्ट',
    params: 'पैरामीटर',
    errTitle: 'जाँच नहीं हो सकी',
    tryAgain: '↩ फिर कोशिश करें',
    footer1: 'एग्रीपल्स AI · फसल स्वास्थ्य बुद्धिमत्ता मॉड्यूल · कॉलेज प्रदर्शनी प्रोजेक्ट',
    footer2: (m) => `मॉडल: ${m} · डेटासेट: PlantVillage · टमाटर और मक्का के लिए`,

    uploadTitle: '🌿 फसल की पत्ती की फोटो अपलोड करें',
    dragDrop: 'अपनी पत्ती की फोटो यहाँ खींचकर छोड़ें',
    or: 'या',
    browseFiles: 'फ़ाइल चुनें',
    formats: 'JPEG · PNG · WebP · अधिकतम 10 MB',
    camera: '📷 कैमरे से फोटो लें',
    supports: 'उपलब्ध फसलें',
    analyze: '🔬 पत्ती की जाँच करें',
    analyzing: 'जाँच हो रही है',
    removeImage: 'फोटो हटाएँ',

    mock: '⚠️ डेमो मोड — असली मॉडल लोड नहीं है। नमूना नतीजा दिखाया जा रहा है।',
    urgent: '24–48 घंटे में इलाज करें',
    photo: '📷 आपकी फोटो',
    badgeHealthy: '✓ स्वस्थ',
    badgeDisease: '⚠ रोग पाया गया',
    confidence: 'AI का भरोसा',
    earlyTitle: '🔍 शुरुआती अवस्था के चेतावनी संकेत',
    earlySub: 'अपने पौधे में ये शुरुआती संकेत देखें — जल्दी पकड़ने पर इलाज आसान होता है:',
    lookTitle: '🖼️ यह रोग कैसा दिखता है',
    lookTip: 'अपनी पत्ती की तुलना इस विवरण से करें। यदि संदेह हो तो प्राकृतिक रोशनी में साफ़ पृष्ठभूमि पर दोबारा फोटो लें, ताकि जाँच अधिक सटीक हो।',
    diagTitle: '🧬 जाँच का नतीजा',
    remediesTitle: '💊 व्यावहारिक उपाय',
    fetching: 'इलाज की योजना लाई जा रही है…',
    careTitle: '🌱 बचाव और देखभाल के सुझाव',
    explainHealthy: (crop) => `आपका ${crop} का पौधा स्वस्थ दिख रहा है! नियमित निगरानी और बचाव की देखभाल जारी रखें।`,
    explainDisease: (disease, crop, severe) =>
      `${crop} पर ${disease} पाया गया। ${severe ? 'इसके लिए तुरंत कार्रवाई जरूरी है।' : 'जल्दी इलाज करना बेहतर है।'}`,
    videosTitle: '📺 रोकथाम के YouTube वीडियो',
    videosNote: 'ये YouTube की खोज खोलते हैं, ताकि आपको हमेशा नए वीडियो दिखें।',
    vidPrev: 'रोकथाम के उपाय',
    vidTreat: 'इलाज और नियंत्रण',
    vidOther: 'Prevention in English (अंग्रेज़ी में)',
    modelUsed: '🧠 उपयोग किया गया मॉडल',
    bestModel: '⭐ सर्वश्रेष्ठ मॉडल',
    testAcc: 'टेस्ट सटीकता',
    parameters: 'पैरामीटर',
    vsResnet: 'ResNet18 की तुलना में',
    vsDense: 'DenseNet121 की तुलना में',
    tied: 'बराबर, 2 गुना हल्का',
    modelWhy: 'EfficientNet-B0 को इसलिए चुना गया क्योंकि सभी 4 मॉडलों में इसकी टेस्ट सटीकता सबसे ज्यादा (99.89%) और पैरामीटर सबसे कम (4.7M) हैं — इसलिए यह किसानों के लिए तुरंत उपयोग हेतु सबसे तेज़ और कुशल विकल्प है।',
    listen: '🔊 जाँच सुनें',
    speaking: '🔊 बोल रहा है…',
    stop: '⏹ रोकें',
    another: '↩ दूसरी पत्ती जाँचें',
    speech: (crop, disease, pct, early, first) =>
      `${crop} के लिए एग्रीपल्स की जाँच: ${disease}। भरोसा: ${pct}।` +
      (early ? ` शुरुआती संकेत: ${early}।` : '') +
      (first ? ` पहला कदम: ${first}।` : ''),
    speechLang: 'hi-IN',
  },
}

export const HI_KB = {
  'Corn___Cercospora_leaf_spot Gray_leaf_spot': {
    name: 'सर्कोस्पोरा पत्ती धब्बा (ग्रे लीफ स्पॉट)',
    referenceDesc: 'निचली पत्तियों पर नसों के बीच संकरे, आयताकार, धूसर-भूरे धब्बे',
    earlyStage: [
      'निचली पत्तियों पर नसों के समानांतर छोटे भूरे-धूसर आयताकार धब्बे',
      'धब्बों के चारों ओर हल्का पीला घेरा होता है और वे नसों से सीमित रहते हैं, इसलिए पत्ती पर चौकोर आकृति दिखती है',
      'धब्बे बढ़कर आपस में मिल जाते हैं, जिससे पत्ती का बड़ा हिस्सा धूसर होकर सूख जाता है',
      'गर्म, नम मौसम में, भारी ओस या बार-बार बारिश होने पर सबसे ज्यादा फैलता है',
    ],
    practicalRemedies: [
      'पहले लक्षण दिखते ही Azoxystrobin + Propiconazole या Mancozeb 75% WP (2.5 ग्राम/लीटर पानी) का छिड़काव करें',
      'अनाज के अलावा दूसरी फसल (जैसे दलहन) के साथ फसल चक्र अपनाएँ — फफूंद पुराने मक्के के अवशेषों में जीवित रहती है',
      'कटाई के बाद फसल अवशेषों को जमीन में दबा दें या हटा दें',
      'बहुत घनी बुवाई से बचें — हवा का अच्छा बहाव पत्तियों को जल्दी सुखाता है',
      'अगले मौसम में रोग-प्रतिरोधी या सहनशील संकर किस्में उगाएँ',
      'ज्यादा नाइट्रोजन न दें, इससे पौधों का घनापन और नमी बढ़ती है',
    ],
  },
  'Corn___Common_rust': {
    name: 'सामान्य रतुआ (कॉमन रस्ट)',
    referenceDesc: 'पत्ती की दोनों सतहों पर बिखरे हुए जंग जैसे लाल-भूरे पाउडरी फफोले',
    earlyStage: [
      'पत्ती के दोनों ओर बिखरे हुए छोटे गोल या अंडाकार लाल-भूरे फफोले',
      'फफोले पाउडर जैसे होते हैं और रगड़ने पर उंगलियों पर जंग जैसी नारंगी धूल लग जाती है',
      'पत्ती पुरानी होने पर ये फफोले गहरे भूरे-काले हो जाते हैं',
      'ठंडे और नम मौसम में सबसे तेज़ी से फैलता है',
    ],
    practicalRemedies: [
      'फफोले दिखते ही Propiconazole 25 EC (1 मि.ली./लीटर) या Mancozeb (2.5 ग्राम/लीटर) का छिड़काव करें',
      'ठंडे, नम मौसम में हर 3–4 दिन खेत की जाँच करें — यह तेज़ी से फैलता है',
      'अगले मौसम में रतुआ-प्रतिरोधी संकर किस्में लगाएँ',
      'देर से बुवाई न करें, इससे छोटे पौधे रतुआ के बीजाणुओं के संपर्क में ज्यादा आते हैं',
      'छोटे प्लॉट में ज्यादा संक्रमित पौधों को निकाल दें ताकि फैलाव धीमा हो',
    ],
  },
  'Corn___Northern_Leaf_Blight': {
    name: 'उत्तरी पत्ती झुलसा (नॉर्दर्न लीफ ब्लाइट)',
    referenceDesc: 'लंबे सिगार जैसे धूसर-हरे से बादामी रंग के धब्बे, नुकीले सिरों वाले',
    earlyStage: [
      'लंबे, सिगार जैसे आकार के धूसर-हरे धब्बे (2.5–15 सेमी), आमतौर पर पहले निचली पत्तियों पर',
      'बढ़ने पर धब्बे नुकीले सिरों वाले भूरे या बादामी हो जाते हैं',
      'नम मौसम में धब्बों पर काले बीजाणु दिखाई देते हैं',
      'कई धब्बे मिलकर पूरी पत्ती को झुलसा सकते हैं',
    ],
    practicalRemedies: [
      'पहले लक्षण दिखते ही, मंजरी (टैसल) निकलने से पहले, Azoxystrobin + Propiconazole या Mancozeb (2.5 ग्राम/लीटर) का छिड़काव करें',
      'फसल चक्र अपनाएँ — एक ही खेत में मक्के के बाद फिर मक्का न लगाएँ',
      'कटाई के बाद संक्रमित अवशेषों को दबा दें या हटा दें',
      'अगले मौसम में प्रतिरोधी संकर किस्में लगाएँ',
      'शाम को ऊपर से सिंचाई न करें, इससे पत्तियाँ रात भर गीली रहती हैं',
    ],
  },
  'Corn___healthy': {
    name: 'स्वस्थ',
    referenceDesc: 'एक समान गहरी हरी पत्तियाँ, कोई धब्बा, फफोला या घाव नहीं',
    earlyStage: [],
    practicalRemedies: [
      'हर 3–4 दिन खेत की जाँच करें, खासकर निचली पत्तियों की',
      'संतुलित खाद दें — बहुत ज्यादा नाइट्रोजन से बचें',
      'खेत को खरपतवार-मुक्त रखें, इससे नमी और कीट कम होते हैं',
      'हर मौसम फसल चक्र अपनाएँ ताकि मिट्टी में रोग न जमे',
    ],
  },
  'Tomato___Bacterial_spot': {
    name: 'जीवाणु धब्बा (बैक्टीरियल स्पॉट)',
    referenceDesc: 'पत्तियों पर पीले घेरे वाले छोटे गहरे धब्बे और फलों पर पपड़ीदार धब्बे',
    earlyStage: [
      'नई पत्तियों और तनों पर पानी से भीगे छोटे धब्बे (1–2 मिमी)',
      '2–3 दिन में धब्बे पीले किनारों के साथ गहरे भूरे हो जाते हैं',
      'फलों पर उभरे, खुरदरे, पपड़ी जैसे धब्बे जिनके बीच में गहरा रंग होता है',
      'बारिश या ऊपर से सिंचाई के बाद ज्यादा फैलता है — जीवाणु पानी से फैलते हैं',
    ],
    practicalRemedies: [
      'हर 7 दिन में copper hydroxide (Kocide 3000) का छिड़काव करें',
      'ज्यादा संक्रमित पत्तियाँ हटा दें और पौधों के बीच औज़ार साफ करें',
      'ड्रिप सिंचाई अपनाएँ — पत्तियों को गीला न करें',
      'बेहतर नियंत्रण के लिए fixed copper + mancozeb का टैंक मिश्रण छिड़कें',
      'संक्रमित पौधों से बीज न बचाएँ',
      'कटाई के बाद फसल अवशेष नष्ट करें ताकि मिट्टी में रोग न रहे',
    ],
  },
  'Tomato___Early_blight': {
    name: 'अगेती झुलसा (अर्ली ब्लाइट)',
    referenceDesc: 'निचली पत्तियों पर बुल्स-आई जैसे गहरे धब्बे, पीला घेरा, नीचे से ऊपर पत्तियों का झड़ना',
    earlyStage: [
      'सबसे पुरानी (निचली) पत्तियों पर पहले छोटे गहरे धब्बे — 3–5 मिमी व्यास के',
      'धब्बों पर गोल छल्लों वाला विशिष्ट निशाने (टारगेट बोर्ड) जैसा पैटर्न',
      'पत्ती भूरी होने से पहले हर धब्बे के आसपास पीला क्षेत्र बनता है',
      'पत्तियाँ झड़ना पौधे के नीचे से ऊपर की ओर शुरू होता है',
    ],
    practicalRemedies: [
      'प्रभावित निचली पत्तियों को तुरंत हटाकर नष्ट करें',
      'हर 7–10 दिन में Chlorothalonil या Mancozeb फफूंदनाशक का छिड़काव करें',
      'पौधे के आधार पर मल्च बिछाएँ — इससे मिट्टी के छींटों से बीजाणु नहीं फैलते',
      'सुबह जमीन के स्तर पर पानी दें — पत्तियों को सूखा रखें',
      'पौधों को सहारा (स्टेक) दें ताकि पत्तियों के आसपास हवा चले',
      'ज्यादा नाइट्रोजन खाद न दें — इससे घनी बढ़वार होती है जो रोग को पसंद है',
    ],
  },
  'Tomato___Late_blight': {
    name: 'पछेती झुलसा (लेट ब्लाइट)',
    referenceDesc: 'गहरे पानी से भीगे धब्बे, निचली सतह पर सफेद फफूंद, तेज़ी से फैलता भूरा-काला रंग',
    earlyStage: [
      'हल्के हरे/धूसर पानी से भीगे धब्बे — आमतौर पर पत्ती के किनारों पर',
      'सुबह-सुबह पत्तियों की निचली सतह पर सफेद रोएँदार फफूंद',
      'ठंडे, नम मौसम में घाव तेज़ी से गहरे भूरे-काले हो जाते हैं',
      'तनों पर भूरी धारियाँ — खासकर बारिश के बाद',
    ],
    practicalRemedies: [
      'तुरंत — Metalaxyl + Mancozeb (Ridomil) का छिड़काव अभी करें',
      'सभी संक्रमित हिस्से हटाकर जला दें — रोग घंटों में फैल जाता है',
      'मौसम ठंडा (15–20°C) और नम हो तो हर 5 दिन में छिड़काव करें',
      'ऊपर से सिंचाई बिल्कुल न करें',
      'बारिश के पूर्वानुमान से पहले बचाव का छिड़काव करें',
      'यदि 50% से अधिक पौधा संक्रमित हो तो पूरा पौधा नष्ट कर दें',
    ],
  },
  'Tomato___Leaf_Mold': {
    name: 'पत्ती फफूंद (लीफ मोल्ड)',
    referenceDesc: 'ऊपर पीले धब्बे, नीचे जैतूनी रोएँदार फफूंद, भीतरी पत्तियाँ प्रभावित',
    earlyStage: [
      'पत्ती की ऊपरी सतह पर हल्के पीले-हरे धब्बे — स्पष्ट किनारे नहीं',
      'पत्ती की निचली सतह पर जैतूनी-हरी से धूसर-भूरी रोएँदार फफूंद',
      'कम हवा वाली पुरानी भीतरी पत्तियों से शुरू होता है',
      'संक्रमित पत्तियाँ किनारों से भीतर की ओर मुड़कर मुरझा जाती हैं',
    ],
    practicalRemedies: [
      'हवा का बहाव बढ़ाएँ — अतिरिक्त पत्तियों की छँटाई करें',
      'नमी कम करें — शाम को पानी न दें',
      'हर 7 दिन में Chlorothalonil या Copper फफूंदनाशक का छिड़काव करें',
      'संक्रमित पत्तियाँ हटाकर जला दें — खाद में न डालें',
      'अगले मौसम में प्रतिरोधी किस्में लगाएँ',
      'पौधों के बीच पर्याप्त दूरी रखें — कम से कम 60 सेमी',
    ],
  },
  'Tomato___Septoria_leaf_spot': {
    name: 'सेप्टोरिया पत्ती धब्बा',
    referenceDesc: 'गहरे किनारे और हल्के केंद्र वाले कई छोटे धब्बे, धब्बों के अंदर काले बिंदु',
    earlyStage: [
      'बहुत छोटे गोल धब्बे (2–3 मिमी) जिनका किनारा गहरा और बीच का भाग भूरा/धूसर होता है',
      'धब्बों के अंदर छोटे काले बिंदु दिखते हैं (पिक्निडिया — फफूंद के फलन पिंड)',
      'फल लगने के बाद सबसे निचली पत्तियों पर पहले दिखता है',
      'पत्तियाँ झड़ने से पहले हर पत्ती पर दर्जनों धब्बे हो जाते हैं',
    ],
    practicalRemedies: [
      'धब्बे दिखते ही Chlorothalonil या Mancozeb का छिड़काव करें',
      'संक्रमित निचली पत्तियाँ तुरंत हटाकर नष्ट करें',
      'गीले पौधों के बीच काम न करें — यह छूने से फैलता है',
      'मिट्टी की सतह पर मल्च बिछाएँ ताकि बीजाणु छींटों से न फैलें',
      'पूरे मौसम में हर 10 दिन में छिड़काव करें',
      '2 साल का फसल चक्र अपनाएँ — फफूंद मिट्टी में जीवित रहती है',
    ],
  },
  'Tomato___Spider_mites Two-spotted_spider_mite': {
    name: 'मकड़ी कण (दो-धब्बेदार स्पाइडर माइट)',
    referenceDesc: 'पत्तियों पर पीले बिंदु, महीन जाला दिखना, काँसे जैसा रंग',
    earlyStage: [
      'ऊपरी पत्ती सतह पर सफेद/पीले महीन बिंदु — धूल जैसे दिखते हैं',
      'पत्तियों की निचली सतह और पत्तियों के बीच महीन जाला',
      'पत्तियाँ काँसे जैसी/पीली होकर सूख जाती हैं — गर्म, सूखे मौसम में ज्यादा',
      'आवर्धक काँच से मकड़ी कण दिखते हैं — निचली सतह पर छोटे चलते बिंदु',
    ],
    practicalRemedies: [
      'पत्तियों की निचली सतह पर तेज़ पानी की धार मारकर कण गिराएँ',
      'Abamectin या Bifenazate माइटनाशक का छिड़काव करें — सामान्य कीटनाशक नहीं',
      'पौधों के आसपास नमी बढ़ाएँ — कण सूखे मौसम में पनपते हैं',
      'उपलब्ध हो तो शिकारी कण (Phytoseiulus persimilis) छोड़ें',
      'बहुत ज्यादा प्रभावित पत्तियाँ हटाकर जला दें',
      'धूल भरी स्थिति से बचें — धूल प्राकृतिक शत्रु कीटों को कम करती है',
    ],
  },
  'Tomato___Target_Spot': {
    name: 'टारगेट स्पॉट (निशानेदार धब्बा)',
    referenceDesc: 'पत्तियों पर भूरे छल्लेदार धब्बे और फलों पर धँसे हुए घाव',
    earlyStage: [
      'पीले घेरे वाले छोटे भूरे धब्बे — अगेती झुलसा जैसे',
      'धब्बों में गोल छल्ले होते हैं लेकिन अगेती झुलसा जितने साफ नहीं',
      'पत्तियों, तनों और फलों पर असर — फलों पर धँसे हुए घाव देखें',
      'गर्म, नम मौसम में तेज़ी से फैलता है',
    ],
    practicalRemedies: [
      'हर 7–14 दिन में Azoxystrobin या Chlorothalonil फफूंदनाशक का छिड़काव करें',
      'खेत से संक्रमित पौध-अवशेष हटाएँ',
      'घनी बुवाई से बचें — हवा का बहाव बढ़ाएँ',
      'केवल सुबह पौधों के आधार पर पानी दें',
      'पौधों के बीच डंडे (स्टेक) और औज़ार साफ करें',
    ],
  },
  'Tomato___Tomato_Yellow_Leaf_Curl_Virus': {
    name: 'टमाटर पीला पत्ती मरोड़ विषाणु',
    referenceDesc: 'पत्तियों का ऊपर मुड़ना, पीले किनारे, बौना पौधा, निचली सतह पर सफेद मक्खी',
    earlyStage: [
      'नई पत्तियाँ ऊपर और अंदर की ओर मुड़ती हैं — कटोरीनुमा आकार',
      'पत्तियाँ पीली पड़ जाती हैं (क्लोरोसिस) — खासकर किनारों पर',
      'पौधा बौना रह जाता है — गाँठों के बीच की दूरी कम, झाड़ीनुमा',
      'सफेद मक्खी से फैलता है — पत्तियों के नीचे सफेद मक्खी देखें',
    ],
    practicalRemedies: [
      'कोई इलाज नहीं — संक्रमित पौधों को उखाड़कर नष्ट करना होगा',
      'सफेद मक्खी पर नियंत्रण: Imidacloprid या Thiamethoxam का छिड़काव करें',
      'सफेद मक्खी पर नज़र रखने और घटाने के लिए पीले चिपचिपे जाल लगाएँ',
      'विषाणु-प्रतिरोधी टमाटर किस्में लगाएँ (जैसे TY किस्में)',
      'परावर्तक मल्च बिछाएँ — यह सफेद मक्खी को बैठने से रोकता है',
      'फैलाव रोकने के लिए संक्रमित पौधे तुरंत हटाएँ',
    ],
  },
  'Tomato___Tomato_mosaic_virus': {
    name: 'टमाटर मोज़ेक विषाणु',
    referenceDesc: 'हल्का-गहरा हरा मोज़ेक पैटर्न, सिकुड़ी टेढ़ी पत्तियाँ, रुकी हुई बढ़वार',
    earlyStage: [
      'नई पत्तियों पर हल्के/गहरे हरे रंग का चितकबरा (मोज़ेक) पैटर्न',
      'पत्तियाँ फफोलेदार, सिकुड़ी या टेढ़ी-मेढ़ी हो सकती हैं',
      'बढ़वार रुक जाती है — नई बढ़वार असामान्य दिखती है',
      'संपर्क से फैलता है — औज़ार, हाथ, संक्रमित बीज',
    ],
    practicalRemedies: [
      'कोई रासायनिक इलाज नहीं — संक्रमित पौधे उखाड़कर नष्ट करें',
      'पौधों को छूने से पहले और बाद में साबुन से हाथ धोएँ',
      'पौधों के बीच औज़ारों को 10% ब्लीच घोल से साफ करें',
      'पौधों के पास धूम्रपान न करें — TMV तंबाकू उत्पादों में जीवित रहता है',
      'अगली बुवाई के लिए प्रमाणित रोग-मुक्त बीज का उपयोग करें',
      'माहू (एफिड) नियंत्रित करें — वे पौधों के बीच विषाणु फैला सकते हैं',
    ],
  },
  'Tomato___healthy': {
    name: 'स्वस्थ',
    referenceDesc: 'गहरी हरी स्वस्थ पत्तियाँ, कोई धब्बा, घाव या रंग-परिवर्तन नहीं',
    earlyStage: [],
    practicalRemedies: [
      'हर 3–4 दिन पौधों की निगरानी करें — जल्दी पहचान ही कुंजी है',
      'नियमित रूप से पानी दें — सूखे के तनाव से बचें',
      'बढ़वार की अवस्था के अनुसार संतुलित NPK खाद दें',
      'शुरुआती कीट/रोग के संकेतों के लिए पत्तियों की निचली सतह जाँचें',
    ],
  },
}

// ─── YouTube links ──────────────────────────────────────────────────
// Search-result links (not single video IDs), so they never go dead
// and always show the newest videos.
const yt = (q) => `https://www.youtube.com/results?search_query=${encodeURIComponent(q)}`

export function ytLinks(key, lang) {
  const [crop, rest = ''] = key.split('___')
  const healthy = /healthy/i.test(rest)
  const nameEn = rest.replace(/_/g, ' ')
  const nameHi = HI_KB[key]?.name?.replace(/\s*\(.*\)\s*/, '') || nameEn
  const cropHi = CROP_HI[crop] || crop

  const en = healthy
    ? { prev: `${crop} plant care tips to prevent disease`, treat: `${crop} farming best practices` }
    : { prev: `${crop} ${nameEn} prevention`, treat: `${crop} ${nameEn} treatment control` }
  const hi = healthy
    ? { prev: `${cropHi} पौधे की देखभाल और रोकथाम`, treat: `${cropHi} की खेती के सही तरीके` }
    : { prev: `${cropHi} ${nameHi} रोकथाम`, treat: `${cropHi} ${nameHi} इलाज`}

  const t = UI[lang]
  const main = lang === 'hi' ? hi : en
  const other = lang === 'hi' ? en : hi
  return [
    { label: t.vidPrev,  url: yt(main.prev) },
    { label: t.vidTreat, url: yt(main.treat) },
    { label: t.vidOther, url: yt(other.prev) },
  ]
}
