from gtts import gTTS

kwestie = [
    ("Witaj! Jak się masz dzisiaj?", "audio\\gtts\\01_powitanie.mp3"),
    ("Świetnie ci idzie! Jesteś super!", "audio\\gtts\\02_pochwala.mp3"),
    ("Brawo! To była dobra odpowiedź!", "audio\\gtts\\04_brawo.mp3"),
]

for tekst, plik in kwestie:
    tts = gTTS(text=tekst, lang='pl', slow=False)
    tts.save(plik)
    print(f"{plik}")