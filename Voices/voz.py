import pyttsx3

voz = pyttsx3.init()

voz.setProperty("rate", 160)

texto = "Hola, soy Mercedes. Ya puedo hablar."

print(texto)

voz.say(texto)
voz.runAndWait()