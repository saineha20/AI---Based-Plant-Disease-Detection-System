# backend/voice_service.py
"""
Farmer Voice Assistant Query Interpreter
Interprets natural language voice queries in Telugu, Hindi, and English
regarding leaf disease diagnosis, treatments, fertilizers, and photo guidance.
"""
import re
from backend.treatment_service import treatment_service

class VoiceService:
    def __init__(self):
        pass

    def answer_query(self, query: str, context: dict, lang: str = "en") -> dict:
        """
        Parses user's voice inquiry with reference to the currently active leaf diagnosis context.
        query: User spoken string
        context: Current diagnosis report (if any)
        lang: 'en', 'hi', or 'te'
        """
        query_lower = (query or "").lower().strip()
        lang = lang if lang in ["en", "hi", "te"] else "en"

        has_context = context and "prediction" in context and context.get("status") == "success"
        crop = context.get("prediction", {}).get("crop", "") if has_context else ""
        disease = context.get("prediction", {}).get("disease_name", "") if has_context else ""
        is_healthy = context.get("prediction", {}).get("is_healthy", False) if has_context else False

        # Intent 1: Photo guidance
        photo_keywords = [
            "photo", "camera", "picture", "focus", "how to take",
            "ఫోటో", "కెమెరా", "తీయ్యాలి", "చిత్రం",
            "फोटो", "कैमरा", "तस्वीर", "कैसे लें"
        ]
        if any(kw in query_lower for kw in photo_keywords):
            return self._photo_guidance_answer(lang)

        # Intent 2: Fertilizer reality check
        fertilizer_keywords = [
            "fertilizer", "urea", "manure", "potash", "cure",
            "ఎరువు", "యూరియా", "ఖతాలు", "తగ్గుతుందా",
            "खाद", "उर्वरक", "यूरिया", "ठीक होगा"
        ]
        if any(kw in query_lower for kw in fertilizer_keywords):
            return self._fertilizer_answer(context, lang)

        # Intent 3: Treatment / Medicine / Chemical spray
        treatment_keywords = [
            "treatment", "medicine", "spray", "cure", "remedy", "control", "how to treat",
            "చికిత్స", "మందు", "పిచికారీ", "నివారణ", "తగ్గించాలి",
            "इलाज", "उपचार", "दवा", "छिड़काव", "रोकथाम", "कैसे ठीक करें"
        ]
        if any(kw in query_lower for kw in treatment_keywords):
            return self._treatment_answer(context, lang)

        # Intent 4: What disease / diagnosis result
        disease_keywords = [
            "disease", "what happened", "what is this", "diagnose", "result", "problem",
            "వ్యాధి", "తెగులు", "ఏమైంది", "రోగాన్ని", "ఫలితం",
            "बीमारी", "रोग", "क्या हुआ", "क्या है", "नतीजा"
        ]
        if any(kw in query_lower for kw in disease_keywords) or has_context:
            return self._diagnosis_answer(context, lang)

        # Default fallback
        return self._default_fallback(lang)

    def _photo_guidance_answer(self, lang: str) -> dict:
        answers = {
            "en": "To capture an accurate photo: place a single diseased leaf in natural daylight without shadows, hold the camera steady 15 to 20 centimeters away, and keep the focus sharp.",
            "hi": "सटीक फोटो के लिए: प्राकृतिक दिन की रोशनी में एक पत्ती को हथेली पर रखें, कैमरे को 15 से 20 सेंटीमीटर की दूरी पर स्थिर रखें और पत्ती के धब्बों पर स्पष्ट फोकस करें।",
            "te": "స్పష్టమైన ఫోటో కోసం: సహజమైన పగటి వెలుతురులో తెగులు సోకిన ఒకే ఆకును ఉంచండి. కెమెరాను 15 నుండి 20 సెంటీమీటర్ల దూరంలో కదలకుండా ఉంచి ఫోకస్ చేయండి."
        }
        return {"intent": "photo_guidance", "response_text": answers.get(lang, answers["en"])}

    def _fertilizer_answer(self, context: dict, lang: str) -> dict:
        if not context or "treatment" not in context:
            answers = {
                "en": "Fertilizers correct soil nutrient deficiencies, but they do NOT cure fungal, bacterial, or viral diseases. Please upload a leaf photo first.",
                "hi": "उर्वरक केवल पोषक तत्वों की कमी पूरी करते हैं, वे फफूंद या जीवाणु रोगों को ठीक नहीं करते। कृपया पहले पत्ती की फोटो अपलोड करें।",
                "te": "ఎరువులు పోషక లోపాలను మాత్రమే సరిచేస్తాయి, శిలీంద్ర లేదా బాక్టీరియా తెగుళ్లను తగ్గించలేవు. దయచేసి ముందుగా ఆకు ఫోటోను పరీక్షించండి."
            }
            return {"intent": "fertilizer_guidance", "response_text": answers.get(lang, answers["en"])}

        fert = context.get("treatment", {}).get("fertilizer_guidance", {})
        explanation = fert.get("explanation", "")
        if explanation:
            return {"intent": "fertilizer_guidance", "response_text": explanation}

        return self._default_fallback(lang)

    def _treatment_answer(self, context: dict, lang: str) -> dict:
        if not context or "treatment" not in context:
            answers = {
                "en": "Please first upload or capture a photo of the affected plant leaf so I can identify the disease and provide verified treatment recommendations.",
                "hi": "कृपया पहले प्रभावित पत्ती की फोटो अपलोड करें ताकि बीमारी पहचानकर सही उपचार बताया जा सके।",
                "te": "దయచేసి ముందుగా తెగులు సోకిన పంట ఆకు ఫోటోను అప్‌లోడ్ చేయండి. అప్పుడు సరైన చికిత్స వివరాలు తెలియజేస్తాను."
            }
            return {"intent": "treatment_advice", "response_text": answers.get(lang, answers["en"])}

        treat = context.get("treatment", {})
        immed = context.get("disease_info", {}).get("immediate_actions", [])
        first_step = immed[0] if immed else ""
        cultural = treat.get("cultural_controls", [])
        first_cultural = cultural[0] if cultural else ""

        if lang == "hi":
            text = f"पहला कदम: {first_step}। कृषि उपाय: {first_cultural}। विस्तृत रासायनिक मात्रा के लिए अपने नजदीकी केवीके या कृषि अधिकारी से संपर्क करें।"
        elif lang == "te":
            text = f"మొదటి చర్య: {first_step}. యాజమాన్య పద్ధతి: {first_cultural}. రసాయన మందుల వాడకానికి మీ ప్రాంతీయ కేవీకే వ్యవసాయ అధికారిని సంప్రదించండి."
        else:
            text = f"First action: {first_step}. Recommended practice: {first_cultural}. Consult your local agricultural officer for crop-specific chemical schedules."

        return {"intent": "treatment_advice", "response_text": text}

    def _diagnosis_answer(self, context: dict, lang: str) -> dict:
        if not context or "prediction" not in context:
            answers = {
                "en": "I am ready. Please upload or photograph a plant leaf to begin diagnosis.",
                "hi": "मैं तैयार हूँ। कृपया रोग की पहचान के लिए पौधे की पत्ती की फोटो अपलोड करें।",
                "te": "నేను సిద్ధంగా ఉన్నాను. వ్యాధిని గుర్తించడానికి పంట ఆకు ఫోటోను అప్‌లోడ్ చేయండి."
            }
            return {"intent": "diagnosis_status", "response_text": answers.get(lang, answers["en"])}

        pred = context["prediction"]
        crop = pred.get("crop", "")
        disease = pred.get("disease_name", "")
        conf = pred.get("confidence_percentage", 0)
        is_healthy = pred.get("is_healthy", False)

        if is_healthy:
            answers = {
                "en": f"Great news! Your {crop} leaf appears healthy with {conf}% confidence.",
                "hi": f"अच्छी खबर! आपकी {crop} की पत्ती {conf}% सटीकता के साथ स्वस्थ पाई गई है।",
                "te": f"శుభవార్త! మీ {crop} ఆకు ఎటువంటి తెగుళ్లు లేకుండా {conf}% ఖచ్చితత్వంతో ఆరోగ్యంగా ఉంది."
            }
        else:
            answers = {
                "en": f"Diagnosis: Your {crop} leaf shows signs of {disease} with {conf}% confidence.",
                "hi": f"निदान: आपकी {crop} की फसल में {conf}% विश्वास के साथ {disease} के लक्षण पाए गए हैं।",
                "te": f"వ్యాధి నిర్ధారణ: మీ {crop} ఆకుపై {conf}% ఖచ్చితత్వంతో {disease} తెగులు గుర్తించబడింది."
            }

        return {"intent": "diagnosis_status", "response_text": answers.get(lang, answers["en"])}

    def _default_fallback(self, lang: str) -> dict:
        answers = {
            "en": "You can ask me about the diagnosed disease, treatment recommendations, fertilizer guidance, or how to take a better leaf photo.",
            "hi": "आप मुझसे रोग के नाम, उपचार के तरीकों, खाद की सलाह या अच्छी फोटो लेने के तरीकों के बारे में पूछ सकते हैं।",
            "te": "మీరు నన్ను వ్యాధి పేరు, నివారణ పద్ధతులు, ఎరువుల సలహాలు లేదా మంచి ఫోటో ఎలా తీయాలనే విషయాల గురించి అడగవచ్చు."
        }
        return {"intent": "help", "response_text": answers.get(lang, answers["en"])}

voice_service = VoiceService()

