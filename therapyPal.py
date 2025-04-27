import os
import google.generativeai as genai
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException
import time
from typing import Optional

# Configure the API
genai.configure(api_key="AIzaSyBysD0Y8IIxdWKPpiwnnQMjPdgYC6h6gjs")
print("API key set successfully!")

class TherapyPal:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro-latest")
        self.conversation_history = []
        self.user_language = "en"  # default to English
        self.setup_initial_prompt()
        # Add language codes for Indian languages
        self.indian_language_codes = {
            "hi": "Hindi",
            "bn": "Bengali",
            "te": "Telugu",
            "ta": "Tamil",
            "mr": "Marathi",
            "gu": "Gujarati",
            "kn": "Kannada",
            "ml": "Malayalam",
            "pa": "Punjabi",
            "or": "Odia",
            "as": "Assamese",
            "sa": "Sanskrit",
            "ur": "Urdu"
        }
        
    def setup_initial_prompt(self):
        """Set up the initial system prompt with therapeutic guidelines"""
        initial_prompt = """You are TherapyPal, a compassionate AI therapist. Your primary goal is to provide 
        emotional support, active listening, and gentle guidance to users. Follow these guidelines:
        
        1. Always respond in the same language the user is using
        2. Practice active listening by reflecting and summarizing
        3. Ask open-ended questions to encourage exploration
        4. Validate emotions before offering suggestions
        5. Maintain a warm, professional tone
        6. Avoid giving direct medical advice
        7. Focus on helping users understand their feelings
        8. Be patient and allow for silence when needed
        
        Start by welcoming the user and asking how they're feeling today."""
        
        self.conversation_history.append({
            "role": "system",
            "content": initial_prompt
        })
    
    def detect_language(self, text: str) -> str:
        """Detect the language of user input with fallback to English"""
        try:
            lang = detect(text)
            # Check if detected language is in our supported languages
            supported_languages = GoogleTranslator().get_supported_languages()
            
            # Update the user's language if detected successfully
            self.user_language = lang if lang in supported_languages else "en"
            print(f"Detected language: {self.user_language} ({self.get_language_name(self.user_language)})")
            return self.user_language
        except LangDetectException:
            print("Language detection failed, using current language")
            return self.user_language  # fallback to current language
    
    def get_language_name(self, lang_code: str) -> str:
        """Get the full language name from code"""
        language_names = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "zh-cn": "Chinese",
            "zh": "Chinese",
            "ar": "Arabic"
        }
        
        # Add Indian languages
        language_names.update(self.indian_language_codes)
        
        return language_names.get(lang_code, lang_code)
    
    def generate_response(self, user_input: str) -> Optional[str]:
        """Generate a therapeutic response to user input"""
        try:
            # First, generate a response in English
            prompt = f"""The following is a therapeutic conversation. You are a compassionate AI therapist:
            
            The user says: "{user_input}"
            
            Provide a therapeutic response as a compassionate therapist. Your response should be caring,
            thoughtful, and focused on helping the user understand their feelings.
            """
            
            english_response = self.model.generate_content(prompt)
            response_text = ""
            
            if hasattr(english_response, "text"):
                response_text = english_response.text.strip()
            else:
                response_text = "I'm listening. Could you tell me more about that?"
                
            # Always translate the response to the user's language if not English
            if self.user_language != "en":
                print(f"Translating response to {self.get_language_name(self.user_language)}")
                response_text = self.translate_to_user_language(response_text)
                
            return response_text
        except Exception as e:
            print(f"Generation error: {e}")
            return None
    
    def translate_to_user_language(self, text: str) -> str:
        """Translate English responses to user's language"""
        if self.user_language == "en":
            return text
        try:
            # Force translation to ensure we get a response in the user's language
            translated = GoogleTranslator(source="en", target=self.user_language).translate(text)
            return translated
        except Exception as e:
            print(f"Translation error: {e}")
            # Try alternative approach if first translation fails
            try:
                translated = GoogleTranslator(source="auto", target=self.user_language).translate(text)
                return translated
            except:
                return text  # proceed with original if all translation attempts fail
    
    def handle_user_input(self, user_input: str):
        """Process user input and generate appropriate response"""
        # Check for exit commands in various languages
        exit_commands = ["exit", "quit", "bye", "goodbye", "बाय", "अलविदा", "বিদায়", "నిష్క్రమించు",
                         "வெளியேறு", "बाहेर", "બાય", "ನಿರ್ಗಮಿಸಿ", "പുറത്തുകടക്കുക", "ਬਾਏ", "ବାଏ",
                         "বিদায়", "वितरामि", "خدا حافظ"]
        
        if any(command in user_input.lower() for command in exit_commands):
            # Detect language before exiting to ensure farewell is in the right language
            self.detect_language(user_input)
            
            # Add Indian language farewell phrases
            closing_phrases = {
                "en": "Take care of yourself. Remember I'm here if you need to talk again.",
                "es": "Cuídate. Recuerda que estoy aquí si necesitas hablar de nuevo.",
                "fr": "Prenez soin de vous. N'oubliez pas que je suis là si vous avez besoin de parler à nouveau.",
                "de": "Pass auf dich auf. Denk daran, ich bin da, wenn du wieder reden möchtest.",
                "it": "Abbi cura di te. Ricorda che sono qui se hai di nuovo bisogno di parlare.",
                "pt": "Cuide-se. Lembre-se de que estou aqui se você precisar conversar novamente.",
                "ru": "Береги себя. Помни, что я здесь, если тебе снова понадобится поговорить.",
                "ja": "お大事に。また話が必要な時はここにいます。",
                "zh": "照顾好自己。记住，如果你需要再次交谈，我在这里。",
                "ar": "اعتن بنفسك. تذكر أنني هنا إذا كنت بحاجة إلى التحدث مرة أخرى.",
                # Indian languages
                "hi": "अपना ख्याल रखें। याद रखें, अगर आपको फिर से बात करने की ज़रूरत हो तो मैं यहां हूं।",
                "bn": "নিজের যত্ন নিন। মনে রাখবেন, আপনার যদি আবার কথা বলার প্রয়োজন হয় তবে আমি এখানে আছি।",
                "te": "మిమ్మల్ని మీరు జాగ్రత్తగా చూసుకోండి. మీకు మళ్ళీ మాట్లాడాలంటే నేను ఇక్కడ ఉన్నానని గుర్తుంచుకోండి.",
                "ta": "உங்களை நீங்கள் கவனித்துக்கொள்ளுங்கள். மீண்டும் பேச வேண்டுமானால் நான் இங்கே இருக்கிறேன் என்பதை நினைவில் கொள்ளுங்கள்.",
                "mr": "स्वतःची काळजी घ्या. लक्षात ठेवा, तुम्हाला पुन्हा बोलण्याची गरज असल्यास मी येथे आहे.",
                "gu": "તમારી કાળજી રાખો. યાદ રાખો કે જો તમારે ફરીથી વાત કરવાની જરૂર હોય તો હું અહીં છું.",
                "kn": "ನಿಮ್ಮ ಆರೈಕೆ ತೆಗೆದುಕೊಳ್ಳಿ. ನೀವು ಮತ್ತೆ ಮಾತನಾಡಬೇಕಾದರೆ ನಾನು ಇಲ್ಲಿದ್ದೇನೆ ಎಂಬುದನ್ನು ನೆನಪಿಡಿ.",
                "ml": "നിങ്ങളെത്തന്നെ ശ്രദ്ധിക്കുക. വീണ്ടും സംസാരിക്കേണ്ടതുണ്ടെങ്കിൽ ഞാൻ ഇവിടെയുണ്ടെന്ന് ഓർക്കുക.",
                "pa": "ਆਪਣਾ ਖਿਆਲ ਰੱਖੋ। ਯਾਦ ਰੱਖੋ ਕਿ ਜੇ ਤੁਹਾਨੂੰ ਦੁਬਾਰਾ ਗੱਲ ਕਰਨ ਦੀ ਲੋੜ ਹੈ ਤਾਂ ਮੈਂ ਇੱਥੇ ਹਾਂ।",
                "or": "ନିଜର ଯତ୍ନ ନିଅନ୍ତୁ | ମନେରଖନ୍ତୁ ଯଦି ଆପଣଙ୍କୁ ପୁଣିଥରେ କଥାବାର୍ତ୍ତା କରିବାର ଆବଶ୍ୟକତା ଅଛି, ମୁଁ ଏଠାରେ ଅଛି |",
                "as": "নিজৰ যত্ন লওক। মনত ৰাখিব, আপুনি যদি আকৌ কথা পাতিব লাগে তেন্তে মই ইয়াত আছোঁ।",
                "sa": "आत्मनः रक्षणं कुर्वन्तु। स्मरन्तु, यदि भवन्तः पुनः संभाषितुम् इच्छन्ति, अहम् अत्र अस्मि।",
                "ur": "اپنا خیال رکھیں۔ یاد رکھیں، اگر آپ کو دوبارہ بات کرنے کی ضرورت ہو تو میں یہاں ہوں۔"
            }
            
            farewell = closing_phrases.get(
                self.user_language,
                closing_phrases["en"]
            )
            print(f"\nTherapyPal: {farewell}")
            return False
        
        # Detect and update language based on user input
        self.detect_language(user_input)
        
        # Generate response in user's language
        response = self.generate_response(user_input)
        
        if not response:
            # Add Indian language error phrases
            error_phrases = {
                "en": "I'm having trouble understanding. Could you rephrase that?",
                "es": "Tengo problemas para entender. ¿Podrías decirlo de otra manera?",
                "fr": "J'ai du mal à comprendre. Pourriez-vous reformuler cela?",
                "de": "Ich habe Schwierigkeiten zu verstehen. Könnten Sie das anders formulieren?",
                "it": "Ho difficoltà a capire. Potresti riformularlo?",
                "pt": "Estou com dificuldade para entender. Você poderia reformular isso?",
                # Indian languages
                "hi": "मुझे समझने में कठिनाई हो रही है। क्या आप इसे दूसरे शब्दों में कह सकते हैं?",
                "bn": "আমি বুঝতে অসুবিধা হচ্ছে। আপনি কি এটি অন্যভাবে বলতে পারেন?",
                "te": "అర్థం చేసుకోవడంలో నాకు ఇబ్బంది ఉంది. మీరు దీన్ని వేరే విధంగా చెప్పగలరా?",
                "ta": "புரிந்துகொள்வதில் எனக்கு சிரமம் உள்ளது. நீங்கள் அதை வேறு விதமாகச் சொல்ல முடியுமா?",
                "mr": "मला समजण्यात अडचण येत आहे. तुम्ही हे वेगळ्या पद्धतीने सांगू शकता का?",
                "gu": "મને સમજવામાં તકલીફ થઈ રહી છે. શું તમે તેને બીજી રીતે કહી શકો છો?",
                "kn": "ಅರ್ಥಮಾಡಿಕೊಳ್ಳುವಲ್ಲಿ ನನಗೆ ತೊಂದರೆ ಆಗುತ್ತಿದೆ. ನೀವು ಅದನ್ನು ಬೇರೆ ರೀತಿಯಲ್ಲಿ ಹೇಳಬಹುದೇ?",
                "ml": "മനസ്സിലാക്കുന്നതിൽ എനിക്ക് ബുദ്ധിമുട്ടുണ്ട്. നിങ്ങൾക്ക് അത് മറ്റൊരു രീതിയിൽ പറയാമോ?",
                "pa": "ਮੈਨੂੰ ਸਮਝਣ ਵਿੱਚ ਮੁਸ਼ਕਲ ਹੋ ਰਹੀ ਹੈ। ਕੀ ਤੁਸੀਂ ਇਸਨੂੰ ਕਿਸੇ ਹੋਰ ਤਰੀਕੇ ਨਾਲ ਕਹਿ ਸਕਦੇ ਹੋ?",
                "or": "ମୁଁ ବୁଝିବାରେ ଅସୁବିଧା ହେଉଛି | ଆପଣ ଏହାକୁ ଅନ୍ୟ ଉପାୟରେ କହିପାରିବେ କି?",
                "as": "মই বুজিবলৈ অসুবিধা পাইছোঁ। আপুনি ইয়াক বেলেগ ধৰণে ক'ব পাৰিবনে?",
                "sa": "अहं बोद्धुम् अशक्तोऽस्मि। भवान् एतद् अन्यथा वक्तुं शक्नोति किम्?",
                "ur": "مجھے سمجھنے میں دشواری ہو رہی ہے۔ کیا آپ اسے کسی اور طریقے سے بیان کر سکتے ہیں؟"
            }
            
            error_msg = error_phrases.get(
                self.user_language,
                error_phrases["en"]
            )
            print(f"\nTherapyPal: {error_msg}")
            return True
        
        # Print response with typing effect
        print("\nTherapyPal: ", end="", flush=True)
        for char in response:
            print(char, end="", flush=True)
            time.sleep(0.03)  # typing effect
        print()
        
        return True
    
    def start_session(self):
        """Start the therapy session with appropriate greeting"""
        # Add Indian language greetings
        greetings = {
            "en": "Hello, I'm TherapyPal. How are you feeling today?",
            "es": "Hola, soy TherapyPal. ¿Cómo te sientes hoy?",
            "fr": "Bonjour, je suis TherapyPal. Comment vous sentez-vous aujourd'hui?",
            "de": "Hallo, ich bin TherapyPal. Wie fühlst du dich heute?",
            "it": "Ciao, sono TherapyPal. Come ti senti oggi?",
            "pt": "Olá, eu sou o TherapyPal. Como você está se sentindo hoje?",
            "ru": "Привет, я TherapyPal. Как ты себя чувствуешь сегодня?",
            "ja": "こんにちは、私はTherapyPalです。今日の気分はどうですか？",
            "zh": "你好，我是TherapyPal。你今天感觉怎么样？",
            "ar": "مرحبًا، أنا TherapyPal. كيف تشعر اليوم؟",
            # Indian languages
            "hi": "नमस्ते, मैं थेरेपीपाल हूँ। आज आप कैसा महसूस कर रहे हैं?",
            "bn": "হ্যালো, আমি থেরাপিপাল। আজ আপনি কেমন বোধ করছেন?",
            "te": "హలో, నేను థెరపీపాల్ని. మీరు ఈరోజు ఎలా ఫీల్ అవుతున్నారు?",
            "ta": "வணக்கம், நான் தெரபிபால். இன்று நீங்கள் எப்படி உணர்கிறீர்கள்?",
            "mr": "नमस्कार, मी थेरपीपाल आहे. आज आपली प्रकृती कशी आहे?",
            "gu": "નમસ્તે, હું થેરાપીપાલ છું. આજે તમે કેવું અનુભવી રહ્યા છો?",
            "kn": "ಹಲೋ, ನಾನು ಥೆರಪಿಪಾಲ್. ನೀವು ಇಂದು ಹೇಗೆ ಭಾವಿಸುತ್ತಿದ್ದೀರಿ?",
            "ml": "ഹലോ, ഞാൻ തെറാപ്പിപാൽ ആണ്. ഇന്ന് നിങ്ങൾ എങ്ങനെ തോന്നുന്നു?",
            "pa": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਮੈਂ ਥੈਰੇਪੀਪਾਲ ਹਾਂ। ਅੱਜ ਤੁਸੀਂ ਕਿਵੇਂ ਮਹਿਸੂਸ ਕਰ ਰਹੇ ਹੋ?",
            "or": "ନମସ୍କାର, ମୁଁ ଥେରାପିପାଲ୍ | ଆଜି ଆପଣ କିପରି ଅନୁଭବ କରୁଛନ୍ତି?",
            "as": "নমস্কাৰ, মই থেৰাপিপাল। আজি আপুনি কেনেকৈ অনুভৱ কৰিছে?",
            "sa": "नमस्ते, अहं थेरपीपाल अस्मि। अद्य भवान् कथं अनुभवति?",
            "ur": "السلام علیکم، میں تھیراپی پال ہوں۔ آج آپ کیسا محسوس کر رہے ہیں؟"
        }
        
        initial_greeting = greetings.get(
            self.user_language,
            greetings["en"]
        )
        
        print("\nLanguage support loaded for multiple Indian languages:")
        print(", ".join(self.indian_language_codes.values()))
        print(f"\nTherapyPal: {initial_greeting}")
        
        while True:
            user_input = input("\nYou: ")
            if not self.handle_user_input(user_input):
                break

    def display_supported_languages(self):
        """Display all supported languages"""
        print("\nSupported languages:")
        print("Global languages: English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Chinese, Arabic")
        print("\nIndian languages:")
        for code, name in self.indian_language_codes.items():
            print(f"- {name} ({code})")

if __name__ == "__main__":
    therapist = TherapyPal()
    therapist.display_supported_languages()
    therapist.start_session()