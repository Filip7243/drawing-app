import edge_tts
import asyncio
from pydub import AudioSegment
from pathlib import Path

async def generuj_glos_dla_dzieci(tekst, plik, **opcje):
    tmp_mp3 = Path(plik).with_suffix(".mp3")

    """
    Generuje naturalny głos z pełną kontrolą nad parametrami.

    Args:
        tekst: Tekst do wypowiedzenia
        plik: Nazwa pliku wyjściowego
        **opcje: Dodatkowe parametry (rate, volume, pitch)
    """
    # Domyślne ustawienia zoptymalizowane dla dzieci
    glos = opcje.get('voice', 'pl-PL-AgnieszkaNeural')
    rate = opcje.get('rate', '+5%')  # Tempo: -50% do +100%
    volume = opcje.get('volume', '+10%')  # Głośność: -50% do +50%
    pitch = opcje.get('pitch', '+8Hz')  # Wysokość: -50Hz do +50Hz

    # Tworzenie communicate z SSML dla lepszej kontroli
    communicate = edge_tts.Communicate(
        tekst,
        glos,
        rate=rate,
        volume=volume,
        pitch=pitch
    )

    await communicate.save(str(tmp_mp3))
    print(f"Zapisano MP3: {tmp_mp3}")

    audio = AudioSegment.from_mp3(tmp_mp3)
    audio = audio.set_channels(1).set_frame_rate(44100).set_sample_width(2)
    audio.export(plik, format="wav")
    print(f"Zapisano WAV: {plik}")


async def main():
    print("Generowanie głosów dla dzieci z Edge TTS\n")

    print("Wariant 1: Optymalne ustawienia dla dzieci")
    # await generuj_glos_dla_dzieci(
    #     "Cześć! Miło mi Cię poznać!... Teraz pokażę Ci jak będzie przebiegał nasz test, jeśli jesteś gotowy wciśniej przycisk Dalej... jeśli czegoś nie zrozumiałeś kilknij Powtórz",
    #     "audio\\edge\\01_powitanie.wav",
    #     rate='+0%',
    #     volume='+8%',  # Trochę głośniej
    #     pitch='+6Hz'  # Wyższy ton - bardziej przyjazny
    # )
    #
    # await generuj_glos_dla_dzieci(
    #     "W teście będzie trzeba zapamiętać 10 rysunków, a następnie je odwzorować z pamięci... Na zapamiętanie każdego z rysunków będziesz miał 10 sekund. Jeśli jesteś gotowy wciśniej przycisk Dalej... jeśli czegoś nie zrozumiałeś kilknij Powtórz",
    #     "audio\\edge\\02_zapamietaj_rysunek_przedmowa.wav",
    #     rate='+2%',  # Lekko szybciej
    #     volume='+8%',  # Trochę głośniej
    #     pitch='+6Hz'  # Wyższy ton - bardziej przyjazny
    # )
    #
    # await generuj_glos_dla_dzieci(
    #     "A teraz zapamiętaj rysunek",
    #     "audio\\edge\\03_zapamietaj_rysunek.wav",
    #     rate='+2%',  # Lekko szybciej
    #     volume='+8%',  # Trochę głośniej
    #     pitch='+6Hz'  # Wyższy ton - bardziej przyjazny
    # )
    #
    # await generuj_glos_dla_dzieci(
    #     "Super! Mam nadzieję, że udało Ci się zapamiętać rysunek. Teraz pora by go odwzorować... Powodzenia! Jeśli jesteś gotowy kliknij Dalej",
    #     "audio\\edge\\04_odwzoruj_rysunek_przedmowa.wav",
    #     rate='+2%',  # Lekko szybciej
    #     volume='+8%',  # Trochę głośniej
    #     pitch='+6Hz'  # Wyższy ton - bardziej przyjazny
    # )
    #
    # await generuj_glos_dla_dzieci(
    #     "A teraz spróbuj narysować to co przed chwilą widziałeś.. Jeśli skończysz kliknij przycisk Dalej znajdujący się u dołu ekranu",
    #     "audio\\edge\\05_odwzoruj_rysunek.wav",
    #     rate='+2%',  # Lekko szybciej
    #     volume='+8%',  # Trochę głośniej
    #     pitch='+6Hz'  # Wyższy ton - bardziej przyjazny
    # )
    #
    # await generuj_glos_dla_dzieci(
    #     "Super!... Przeszliśmy przez samouczek... teraz pora na właściwy test... jeśli jesteś gotowy kliknij przycisk Dalej... jeśli chcesz powtórzyć samouczek kliknij przycisk Powtórz!... Powodzenia!",
    #     "audio\\edge\\06_koniec_samouczka.wav",
    #     rate='+2%',  # Lekko szybciej
    #     volume='+8%',  # Trochę głośniej
    #     pitch='+6Hz'  # Wyższy ton - bardziej przyjazny
    # )
    await generuj_glos_dla_dzieci(
        "Jeśli będziesz gotowy, kliknij dalej, jeśli chce powtórzyć samouczek kliknij Powtórz!... Powodzenia!",
        "audio\\edge\\07_koniec_samouczka.wav",
        rate='+2%',  # Lekko szybciej
        volume='+8%',  # Trochę głośniej
        pitch='+6Hz'  # Wyższy ton - bardziej przyjazny
    )


if __name__ == "__main__":
    asyncio.run(main())
