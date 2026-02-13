from deep_translator import GoogleTranslator

translated = GoogleTranslator(source='en', target='ko').translate("Hello, how are you?")
print(translated) 

