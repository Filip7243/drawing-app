import edge_tts
import asyncio
from pydub import AudioSegment
from pathlib import Path


async def generuj_glos_dla_dzieci(tekst, plik, **opcje):
    tmp_mp3 = Path(plik).with_suffix(".mp3")
    print("TMP_MP3:", tmp_mp3)

    """
    Generuje naturalny głos z pełną kontrolą nad parametrami.

    Args:
        tekst: Tekst do wypowiedzenia
        plik: Nazwa pliku wyjściowego
        **opcje: Dodatkowe parametry (rate, volume, pitch)
    """
    # Domyślne ustawienia zoptymalizowane dla dzieci
    glos = opcje.get('voice', 'pl-PL-AgnieszkaNeural')
    rate = opcje.get('rate', '+0%')
    volume = opcje.get('volume', '+0%')
    pitch = opcje.get('pitch', '+0Hz')

    # Tworzenie katalogu nadrzędnego, jeśli nie istnieje
    Path(plik).parent.mkdir(parents=True, exist_ok=True)

    # Tworzenie communicate bez jawnych jednostek w parametrach, jeśli edge-tts ich nie lubi w tej wersji
    # lub użycie domyślnych, jeśli to one powodują błąd.
    print(f"DEBUG: Tekst='{tekst}', glos='{glos}', rate='{rate}', volume='{volume}', pitch='{pitch}'")
    communicate = edge_tts.Communicate(tekst, glos, rate=rate, volume=volume, pitch=pitch)

    await communicate.save(str(tmp_mp3))
    print(f"Zapisano MP3: {tmp_mp3}")

    audio = AudioSegment.from_mp3(tmp_mp3)
    audio = audio.set_channels(1).set_frame_rate(44100).set_sample_width(2)
    audio.export(plik, format="wav")
    print(f"Zapisano WAV: {plik}")


async def main():
    import edge_tts
    # c = edge_tts.Communicate(
    #     "Cześć! Miło mi Cię poznać! Teraz pokażę Ci jak będzie przebiegał nasz test.. Jeśli jesteś gotowy wciśniej przycisk Dalej, jeśli czegoś nie zrozumiałeś kliknij Powtórz.",
    #     "pl-PL-ZofiaNeural", rate='+0%', volume='+2%', pitch='+0Hz')
    # await c.save("audio\\edge\\01_powitanie.wav")
    #
    # d = edge_tts.Communicate(
    #     "W teście będzie trzeba zapamiętać 10 rysunków, a następnie je odwzorować z pamięci. Nie martw się, nikt Cię nie będzie oceniał, możesz rysować tyle czasu ile chcesz. Na zapamiętanie każdego z rysunków będziesz miał 10 sekund. Jeśli jesteś gotowy wciśniej przycisk Dalej. jeśli czegoś nie zrozumiałeś kilknij Powtórz",
    #     "pl-PL-ZofiaNeural", rate='-1%', volume='+2%', pitch='+0Hz')
    # await d.save("audio\\edge\\02_zapamietaj_rysunek_przedmowa.wav")
    #
    # e = edge_tts.Communicate(
    #     "A teraz zapamiętaj rysunek",
    #     "pl-PL-ZofiaNeural", rate='+1%', volume='+2%', pitch='+0Hz')
    # await e.save("audio\\edge\\03_zapamietaj_rysunek.wav")
    #
    f = edge_tts.Communicate(
        "A teraz spróbuj narysować to co przed chwilą widziałeś. Jeśli skończysz kliknij przycisk Dalej znajdujący się u dołu ekranu.",
        "pl-PL-ZofiaNeural", rate='+1%', volume='+2%', pitch='+0Hz')
    await f.save("audio\\edge\\05_odwzoruj_rysunek.wav")

    # g = edge_tts.Communicate(
    #     "Jeśli będziesz gotowy, kliknij dalej, jeśli chcesz powtórzyć samouczek kliknij Powtórz!. Powodzenia!",
    #     "pl-PL-ZofiaNeural", rate='+1%', volume='+2%', pitch='+0Hz')
    # await g.save("audio\\edge\\07_koniec_samouczka.wav")

    # await generuj_glos_dla_dzieci(
    #     "W teście będzie trzeba zapamiętać 10 rysunków, a następnie je odwzorować z pamięci. Nie martw się, nikt Cię nie będzie oceniał, możesz rysować tyle czasu ile chcesz. Na zapamiętanie każdego z rysunków będziesz miał 10 sekund. Jeśli jesteś gotowy wciśniej przycisk Dalej. jeśli czegoś nie zrozumiałeś kilknij Powtórz",
    #     "audio\\edge\\02_zapamietaj_rysunek_przedmowa.wav",
    #     rate='+2%',  # Lekko szybciej
    #     volume='+6%',  # Trochę głośniej
    #     pitch='+6Hz'  # Wyższy ton - bardziej przyjazny
    # )
    #
    # await generuj_glos_dla_dzieci(
    #     "A teraz zapamiętaj rysunek",
    #     "audio\\edge\\03_zapamietaj_rysunek.wav",
    #     rate='+2%',  # Lekko szybciej
    #     volume='+6%',  # Trochę głośniej
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
    #     "A teraz spróbuj narysować to co przed chwilą widziałeś. Jeśli skończysz kliknij przycisk Dalej znajdujący się u dołu ekranu.",
    #     "audio\\edge\\05_odwzoruj_rysunek.wav",
    #     rate='+0%',  # Lekko szybciej
    #     volume='+6%',  # Trochę głośniej
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
    # await generuj_glos_dla_dzieci(
    #     "Jeśli będziesz gotowy, kliknij dalej, jeśli chcesz powtórzyć samouczek kliknij Powtórz!. Powodzenia!",
    #     "audio\\edge\\07_koniec_samouczka.wav",
    #     rate='+2%',  # Lekko szybciej
    #     volume='+6%',  # Trochę głośniej
    #     pitch='+6Hz'  # Wyższy ton - bardziej przyjazny
    # )

    # h = edge_tts.Communicate(
    #     "Cześć! Witaj w samouczku do testu. W teście odpowiesz na 60 pytań. "
    #     "Na ekranie zobaczysz kartę z brakującym elementem wzoru. Twoim zadaniem jest dopasować właściwy wzór, "
    #     "który uzupełnia tę kartę. Na dole ekranu znajdują się możliwe odpowiedzi. "
    #     "Niektóre pytania będą miały 6 odpowiedzi, a inne 8, ale zawsze tylko jedna będzie poprawna. "
    #     "Nie musisz się spieszyć — test nie jest na czas ani na ocenę. "
    #     "Jeśli wszystko jest jasne, kliknij dalej, a test się rozpocznie. "
    #     "Jeśli coś jest nie tak, kliknij powtórz, aby ponownie odsłuchać ten samouczek.",
    #     "pl-PL-ZofiaNeural", rate='+1%', volume='+2%', pitch='+0Hz'
    # )

    # await h.save("audio\\edge\\01_raven_samouczek.wav")


if __name__ == "__main__":
    asyncio.run(main())
