// frontend/voice.js
/**
 * Kisan Mitra - Enhanced Farmer Voice Assistant & Speech Synthesis
 * Robust Multilingual TTS Engine with Windows Voice Fallbacks for Telugu & Hindi
 */

class KisanVoiceAssistant {
  constructor() {
    this.recognition = null;
    this.synthesis = window.speechSynthesis;
    this.isListening = false;
    this.isSpeaking = false;
    this.currentContext = null;
    this.availableVoices = [];

    this.initVoices();
    this.initSpeechRecognition();
    this.injectSubtitleUI();
  }

  initVoices() {
    if (!this.synthesis) return;
    const loadVoices = () => {
      this.availableVoices = this.synthesis.getVoices();
      console.log(`Loaded ${this.availableVoices.length} browser voices.`);
    };
    loadVoices();
    if (this.synthesis.onvoiceschanged !== undefined) {
      this.synthesis.onvoiceschanged = loadVoices;
    }
  }

  getLangCode() {
    const lang = window.getCurrentLanguage ? window.getCurrentLanguage() : "en";
    if (lang === "te") return "te-IN";
    if (lang === "hi") return "hi-IN";
    return "en-IN";
  }

  findBestVoice(lang) {
    const voices = this.availableVoices.length > 0 ? this.availableVoices : (this.synthesis ? this.synthesis.getVoices() : []);
    if (!voices || voices.length === 0) {
      return { voice: null, langCode: this.getLangCode() };
    }

    if (lang === "te") {
      // 1. Look for native Telugu voice
      const teVoice = voices.find(v => 
        (v.lang && v.lang.toLowerCase().startsWith("te")) ||
        (v.name && (v.name.toLowerCase().includes("telugu") || v.name.includes("తెలుగు") || v.name.toLowerCase().includes("mohan") || v.name.toLowerCase().includes("shruti")))
      );
      if (teVoice) return { voice: teVoice, langCode: teVoice.lang || "te-IN" };

      // 2. Fallback to Hindi or Indian English voice (which supports Indian phonetics on Windows)
      const hiVoice = voices.find(v => 
        (v.lang && v.lang.toLowerCase().startsWith("hi")) ||
        (v.name && (v.name.toLowerCase().includes("hindi") || v.name.includes("हिन्दी") || v.name.toLowerCase().includes("swara") || v.name.toLowerCase().includes("kalpana")))
      );
      if (hiVoice) return { voice: hiVoice, langCode: hiVoice.lang || "hi-IN" };

      const inVoice = voices.find(v => v.lang && v.lang.toLowerCase().includes("in"));
      if (inVoice) return { voice: inVoice, langCode: inVoice.lang };

      return { voice: voices[0], langCode: "te-IN" };
    }

    if (lang === "hi") {
      // Look for native Hindi voice
      const hiVoice = voices.find(v => 
        (v.lang && v.lang.toLowerCase().startsWith("hi")) ||
        (v.name && (v.name.toLowerCase().includes("hindi") || v.name.includes("हिन्दी") || v.name.toLowerCase().includes("swara") || v.name.toLowerCase().includes("kalpana")))
      );
      if (hiVoice) return { voice: hiVoice, langCode: hiVoice.lang || "hi-IN" };

      const inVoice = voices.find(v => v.lang && v.lang.toLowerCase().includes("in"));
      if (inVoice) return { voice: inVoice, langCode: inVoice.lang };

      return { voice: voices[0], langCode: "hi-IN" };
    }

    // English
    const enVoice = voices.find(v => v.lang && (v.lang.toLowerCase() === "en-in" || v.lang.toLowerCase().startsWith("en")));
    return { voice: enVoice || voices[0] || null, langCode: enVoice ? enVoice.lang : "en-IN" };
  }

  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    try {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = false;

      this.recognition.onstart = () => {
        this.isListening = true;
        this.updateVoiceStatus("listening");
      };

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        this.handleTranscript(transcript);
      };

      this.recognition.onerror = (event) => {
        this.isListening = false;
        this.updateVoiceStatus("ready");
      };

      this.recognition.onend = () => {
        this.isListening = false;
        this.updateVoiceStatus("ready");
      };
    } catch (e) {
      console.warn("Speech recognition initialization notice:", e);
    }
  }

  setContext(report) {
    this.currentContext = report;
  }

  toggleListening() {
    if (this.isSpeaking) {
      this.stopSpeaking();
    }

    if (!this.recognition) {
      const modal = document.getElementById("voiceAssistantModal");
      if (modal) modal.classList.remove("hidden");
      this.updateVoiceStatus("unsupported");
      return;
    }

    if (this.isListening) {
      this.stopListening();
    } else {
      this.startListening();
    }
  }

  startListening() {
    if (!this.recognition) return;
    this.recognition.lang = this.getLangCode();
    try {
      this.recognition.start();
    } catch (e) {
      console.warn("Recognition start notice:", e);
    }
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
      this.updateVoiceStatus("ready");
    }
  }

  async handleTranscript(text) {
    this.updateVoiceStatus("processing");
    const transcriptElem = document.getElementById("voiceTranscript");
    if (transcriptElem) {
      transcriptElem.innerHTML = `<strong>You:</strong> "${text}"`;
    }

    const currentLang = window.getCurrentLanguage ? window.getCurrentLanguage() : "en";
    let reply = "";

    try {
      const response = await fetch("/api/voice/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: text,
          context: this.currentContext,
          lang: currentLang
        })
      });

      if (response.ok) {
        const data = await response.json();
        reply = data.result.response_text;
      }
    } catch (err) {}

    // Offline heuristic fallback for voice questions
    if (!reply) {
      const tLower = text.toLowerCase();
      if (tLower.includes("fertilizer") || tLower.includes("urea") || tLower.includes("खाद") || tLower.includes("ఎరువు")) {
        reply = currentLang === "te" ? "ఎరువులు వేస్తే ఈ తెగులు తగ్గదు. యూరియా ఎక్కువ వేయకండి, పొటాష్ సమతుల్యంగా వేయండి." : (currentLang === "hi" ? "खाद डालने से यह बीमारी ठीक नहीं होगी। संतुलित पोटाश दें।" : "Fertilizers do NOT cure leaf blights. Maintain balanced potash.");
      } else if (tLower.includes("treatment") || tLower.includes("spray") || tLower.includes("इलाज") || tLower.includes("చికిత్స")) {
        reply = currentLang === "te" ? "మొదటి చర్యగా తెగులు సోకిన ఆకులను తుంచివేయండి. మాంకోజెబ్ లేదా కాపర్ ఆక్సిక్లోరైడ్ పిచికారీ చేయండి." : (currentLang === "hi" ? "संक्रमित पत्तियां हटाएं और मैंकोजेब या कॉपर का छिड़काव करें।" : "Prune infected leaves and apply registered Mancozeb or Copper oxychloride.");
      } else {
        const crop = this.currentContext ? this.currentContext.prediction.crop : (currentLang === "te" ? "పంట" : (currentLang === "hi" ? "फसल" : "Crop"));
        const disease = this.currentContext ? this.currentContext.prediction.disease_name : "";
        reply = currentLang === "te" ? `${crop} ఆకుపై ${disease} తెగులు గుర్తించబడింది.` : (currentLang === "hi" ? `${crop} की पत्ती में ${disease} के लक्षण हैं।` : `Leaf condition identified: ${disease}.`);
      }
    }

    const replyElem = document.getElementById("voiceReply");
    if (replyElem) {
      replyElem.innerHTML = `<strong>Kisan Mitra:</strong> "${reply}"`;
    }

    this.speak(reply);
    this.updateVoiceStatus("ready");
  }

  speak(text) {
    if (!this.synthesis) {
      console.warn("SpeechSynthesis not available.");
      this.showSubtitle(text, 5000);
      return;
    }

    // Clear any stuck audio queue in Chrome
    this.stopSpeaking();
    try {
      if (this.synthesis.paused) {
        this.synthesis.resume();
      }
    } catch (e) {}

    const currentLang = window.getCurrentLanguage ? window.getCurrentLanguage() : "en";
    const { voice, langCode } = this.findBestVoice(currentLang);

    // Show on-screen subtitle banner immediately
    this.showSubtitle(text);

    // Break text into clean concise sentences for smooth synthesis without browser cutoff
    const cleanText = text.replace(/[*_#]/g, "").trim();
    const utterance = new SpeechSynthesisUtterance(cleanText);

    utterance.lang = langCode;
    utterance.rate = 0.90; // Natural pace for farmers
    utterance.pitch = 1.0;

    if (voice) {
      utterance.voice = voice;
    }

    utterance.onstart = () => {
      this.isSpeaking = true;
      this.updateSpeakingUI(true);
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      this.updateSpeakingUI(false);
      this.hideSubtitle();
    };

    utterance.onerror = (e) => {
      console.warn("Speech synthesis notice:", e);
      this.isSpeaking = false;
      this.updateSpeakingUI(false);
      // Even if OS audio engine fails, keep subtitle visible for 5 seconds
      setTimeout(() => this.hideSubtitle(), 5000);
    };

    // Speak
    try {
      this.synthesis.speak(utterance);
    } catch (err) {
      console.warn("Speech execute notice:", err);
      this.showSubtitle(text, 5000);
    }
  }

  stopSpeaking() {
    if (this.synthesis) {
      try {
        this.synthesis.cancel();
      } catch (e) {}
      this.isSpeaking = false;
      this.updateSpeakingUI(false);
      this.hideSubtitle();
    }
  }

  updateVoiceStatus(state) {
    const statusElem = document.getElementById("voiceStatusText");
    const micBtn = document.getElementById("voiceMicBtn");
    if (!statusElem) return;

    if (state === "listening") {
      statusElem.innerText = window.getTranslation("voice_status_listening");
      if (micBtn) micBtn.classList.add("listening-active");
    } else if (state === "processing") {
      statusElem.innerText = window.getTranslation("voice_status_processing");
      if (micBtn) micBtn.classList.remove("listening-active");
    } else {
      statusElem.innerText = window.getTranslation("voice_status_ready");
      if (micBtn) micBtn.classList.remove("listening-active");
    }
  }

  updateSpeakingUI(speaking) {
    const playBtn = document.getElementById("listenReportBtn");
    if (playBtn) {
      if (speaking) {
        playBtn.innerHTML = `<span class="icon">⏹</span> <span data-i18n="stop_voice">${window.getTranslation("stop_voice")}</span>`;
        playBtn.classList.add("btn-speaking");
      } else {
        playBtn.innerHTML = `<span class="icon">🔊</span> <span data-i18n="listen_voice">${window.getTranslation("listen_voice")}</span>`;
        playBtn.classList.remove("btn-speaking");
      }
    }
  }

  injectSubtitleUI() {
    if (document.getElementById("voiceSubtitleBar")) return;
    const bar = document.createElement("div");
    bar.id = "voiceSubtitleBar";
    bar.style.cssText = `
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(27, 94, 32, 0.95);
      color: #ffffff;
      padding: 12px 22px;
      border-radius: 30px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
      font-size: 15px;
      font-weight: 600;
      max-width: 90%;
      width: max-content;
      z-index: 99999;
      display: none;
      align-items: center;
      gap: 12px;
      border: 1px solid rgba(255, 255, 255, 0.3);
      backdrop-filter: blur(4px);
    `;
    bar.innerHTML = `
      <span style="font-size: 20px;">🔊</span>
      <span id="voiceSubtitleText"></span>
      <button onclick="window.kisanVoice.stopSpeaking()" style="background: rgba(255,255,255,0.25); border: none; color: white; border-radius: 50%; width: 26px; height: 26px; cursor: pointer; font-weight: bold; margin-left: 8px;">✕</button>
    `;
    document.body.appendChild(bar);
  }

  showSubtitle(text, autoHideMs) {
    const bar = document.getElementById("voiceSubtitleBar");
    const label = document.getElementById("voiceSubtitleText");
    if (bar && label) {
      label.innerText = text;
      bar.style.display = "flex";
      if (autoHideMs) {
        setTimeout(() => this.hideSubtitle(), autoHideMs);
      }
    }
  }

  hideSubtitle() {
    const bar = document.getElementById("voiceSubtitleBar");
    if (bar) {
      bar.style.display = "none";
    }
  }
}

// Global Voice Assistant
window.kisanVoice = new KisanVoiceAssistant();
