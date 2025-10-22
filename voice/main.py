import pyttsx3


def generuj_glos_dla_dzieci(tekst, nazwa_pliku):
    """
    Generuje plik audio z polskim głosem, offline i całkowicie darmowo.

    Args:
        tekst: Tekst do wypowiedzenia
        nazwa_pliku: Nazwa pliku wyjściowego (np. 'powitanie.mp3')
    """
    # Inicjalizacja silnika TTS
    engine = pyttsx3.init()

    # Pobranie dostępnych głosów
    voices = engine.getProperty('voices')

    # Szukanie polskiego głosu kobiecego
    polish_voice = None
    for voice in voices:
        if 'polish' in voice.name.lower() or 'pl' in voice.languages:
            # Preferuj kobiece głosy
            if 'female' in voice.name.lower() or 'paulina' in voice.name.lower():
                polish_voice = voice.id
                break
            elif polish_voice is None:  # Zapisz pierwszy polski głos jako backup
                polish_voice = voice.id

    # Ustawienie głosu
    if polish_voice:
        engine.setProperty('voice', polish_voice)

    # Dostosowanie parametrów dla dzieci
    engine.setProperty('rate', 150)  # Wolniejsze tempo (domyślnie 200)
    engine.setProperty('volume', 1.0)  # Maksymalna głośność

    # Opcjonalnie: wyższy ton (nie wszystkie silniki to obsługują)
    try:
        engine.setProperty('pitch', 1.2)
    except:
        pass  # Niektóre silniki nie mają tej opcji

    # Zapisanie do pliku
    engine.save_to_file(tekst, nazwa_pliku)
    engine.runAndWait()
    print(f"✓ Wygenerowano: {nazwa_pliku}")


def wyswietl_dostepne_glosy():
    """Pokazuje wszystkie dostępne głosy w systemie"""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    print("\n📢 Dostępne głosy w systemie:")
    print("-" * 60)
    for i, voice in enumerate(voices):
        print(f"{i}. {voice.name}")
        print(f"   ID: {voice.id}")
        print(f"   Języki: {voice.languages}")
        print()


# Przykładowe kwestie dla dzieci
kwestie = [
    ("Cześć! Miło mi Cię poznać!... Teraz pokażę Ci jak będzie przebiegał nasz test, jeśli jesteś gotowy wciśniej przycisk Dalej", "01_powitanie.wav"),
    # ("Świetnie ci idzie! Jesteś super!", "02_pochwala.wav"),
    # ("Spróbuj jeszcze raz. Wierzę w ciebie!", "03_zacheta.wav"),
    # ("Brawo! To była dobra odpowiedź!", "04_brawo.wav"),
    # ("Czas na przerwę. Pamiętaj, żeby się napić wody!", "05_przerwa.wav"),
]

if __name__ == "__main__":
    # Najpierw zobacz dostępne głosy
    print("Sprawdzam dostępne głosy...")
    wyswietl_dostepne_glosy()

    # Generowanie wszystkich plików
    print("\nGenerowanie plików audio...")
    for tekst, plik in kwestie:
        try:
            generuj_glos_dla_dzieci(tekst, plik)
        except Exception as e:
            print(f"❌ Błąd przy generowaniu {plik}: {e}")

    print("\n✅ Gotowe! Wszystkie pliki wygenerowane.")
    print("\nJeśli jakość głosu nie jest zadowalająca, możesz:")
    print("1. Zainstalować dodatkowe głosy SAPI5 (Windows)")
    print("2. Użyć gTTS (wymaga internetu, ale lepsza jakość)")
