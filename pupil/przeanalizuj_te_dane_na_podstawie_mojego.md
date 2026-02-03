### Co jest w pliku `summary.json`

Plik zawiera podsumowanie całego testu oraz listę rysunków (po jednym wpisie na obraz). Najważniejsze pola:
- `test_start_unix`, `test_start_perf`, `test_end_ts`, `total_duration_s` – znaczniki czasu i łączny czas badania.
- `drawings` – lista rekordów rysunków; każdy rekord opisuje jeden obraz.

Dalej opisuję każdą metrykę pojedynczego rysunku (czyli elementu z `drawings`) – co oznacza i jak ją interpretować. Nazwy odpowiadają polom tworzonym w kodzie w `DrawingRecord` i w metodzie `finish_drawing()`.

---

### Identyfikacja rysunku i pliki pomocnicze
- `index` – numer rysunku w sesji. Ułatwia powiązanie z plikami PNG generowanymi obok.
- `filename` – nazwa pliku obrazu badanego (PNG). To finalny rysunek.
- `overlay_filename` – PNG z nałożeniem rysunku badanego na wzorzec. Interpretacja: im lepsze nałożenie konturów, tym większa zgodność z wzorcem; rozjazdy pokazują błędy lokalizacji i proporcji.
- `heatmap_filename` – mapa gęstości pociągnięć. Czerwone/gorące miejsca = obszary intensywnie „szorowane” lub poprawiane. Przydatne do wykrycia wahań, niepewności, nadmiernych poprawek.
- `velocity_profile_filename` – wykres profilu prędkości (szczególnie krzywe log-normalne). Służy do oceny płynności ruchu; zbyt wiele pików lub gwałtowne fluktuacje wskazują na przerywane, niepewne rysowanie.
- `display_info` – parametry wyświetlania (rozmiary okna i obrazu, offset). Potrzebne do prawidłowej interpretacji współrzędnych i nakładek, nie jest metryką jakości.

Jak używać: porówniaj `overlay` i `heatmap` z wartościami ilościowymi poniżej (np. `max_local_density`, `overdrawing_score`) – powinny się zgadzać wizualnie.

---

### Czasy i przerwy
- `started_at`, `started_at_ts` – moment pojawienia się planszy do rysowania (perf i unix). Kontekst czasowy dla pozostałych pól.
- `first_stroke_at`, `first_stroke_at_ts` – moment pierwszego dotknięcia płótna. Długi odstęp między `started_at` a `first_stroke_at` może oznaczać planowanie lub niepewność.
- `finished_at`, `finished_at_ts` – moment zakończenia rysowania (naciśnięcie „Dalej”).
- `duration_s` – całkowity czas od pojawienia się planszy do zakończenia. Interpretacja: łączny czas poświęcony na dany rysunek (planowanie + rysowanie).
- `actual_drawing_duration_s` – rzeczywisty czas rysowania (od pierwszego śladu do końca). Niższy niż `duration_s` oznacza dłuższe planowanie przed pierwszym pociągnięciem.
- `interruptions_count` – liczba oderwań narzędzia od płótna (liczba pociągnięć/„stroke’ów” minus jeden). Wysoka wartość może oznaczać strategię detaliczną lub przerywane, niepewne rysowanie.
- `interruption_durations` – czasy poszczególnych przerw (s). Przydatne do wykrycia długich zawahań.
- `avg_interruption_duration_s` – średni czas przerwy. Większa średnia = częstsze zastanawianie się, zmiana planu lub zmęczenie.

Praktyczna interpretacja:
- Krótkie `duration_s` i niskie `interruptions_count` z małymi przerwami → płynne, pewne rysowanie.
- Długie `duration_s` i/lub wysoka `avg_interruption_duration_s` → dużo planowania lub trudność z odwzorowaniem.

---

### Cofnięcia i ponowienia
- `undo_count`, `redo_count` – liczba cofnięć i przywróceń. Wysokie wartości zwykle korelują z niepewnością, próbami poprawy lub strategią „szukania” kształtu.

---

### „Szorowanie” i powroty
- `overdrawing_score` – stosunek pikseli rysowanych wielokrotnie w tym samym miejscu do wszystkich pikseli. Zakres 0–1.
  - Nisko (blisko 0): mało poprawek, bardziej zdecydowana linia.
  - Wysoko (np. > 0.15–0.20 zależnie od obrazu): częste poprawianie, cieniowanie lub „szukanie” konturu.
- `revisits_count` – liczba unikalnych powrotów do wcześniej odwiedzonych sekcji płótna (wykrywane, gdy nowy stroke silnie zachodzi na już odwiedzoną siatkę; progowe `OVERLAP_RATIO_THRESHOLD = 0.5`).
  - Pojedyncze–umiarkowane wartości: normalne w złożonych figurach.
  - Wysokie: fragmentaryzacja, wieloetapowe poprawki, trudności z planem globalnym.
- `shading_detected` – flaga prób cieniowania/mazania (heurystyka). Przydatna, gdy instrukcja wyklucza cieniowanie.

---

### Zmiany kierunku i dynamika
- `direction_changes_count` – liczba znaczących zmian kierunku w obrębie ruchu (wewnętrzna heurystyka). Większa liczba = bardziej kanciasta, poszarpana trajektoria.
- `directional_reversals_count` – liczba odwróceń kierunku (np. lewo–prawo–lewo). Wysoko → „oscylacje” ręki lub poprawki.
- `rapid_velocity_changes_count` – liczba gwałtownych zmian prędkości. Wysoko → niestabilny rytm, wahania.

Interpretacja: dużo zmian kierunku i prędkości zwykle idzie w parze z wyższym `overdrawing_score` i „gorącą” `heatmap`.

---

### Efektywność i gęstości lokalne
- `efficiency_ratio` – ratio długości rzeczywistej ścieżki do długości jej uproszczenia (RDP). W kodzie próg referencyjny `EFFICIENCY_THRESHOLD = 2.5`.
  - ≈1.0–1.5: bardzo efektywna, gładka ścieżka (mało zbędnych zawijasów).
  - >2.5: trajektoria długa względem „esencji” kształtu → zygzaki, poprawki, nieoptymalna kolejność.
- `max_local_density` – maksymalna łączna długość trajektorii w pojedynczej komórce siatki.
- `max_local_density_coords` – współrzędne tej komórki. 
  - Użycie: pokazuje „najbardziej wyszorowane” miejsce; powiąż z `heatmap` (powinno odpowiadać najgorętszemu pikowi).

---

### Prędkości rysowania
- `velocities` – lista chwilowych prędkości. Można patrzeć na rozrzut: stabilny przebieg vs. skoki.
- `avg_velocity` – średnia prędkość.
- `max_velocity` – maksymalna prędkość.
- `velocity_ratio` – `avg_velocity / max_velocity`. 
  - Zbliżone do 1: równomierna prędkość bez ostrych sprintów.
  - Niskie (np. <0.4): sporadyczne bardzo szybkie ruchy (piki) na tle ogólnie wolniejszego rysowania.
- `velocity_profile_filename` – wykres profilu prędkości (krzywa log-normalna). 
  - Pojedynczy, gładki „dzwon”: płynne pociągnięcie.
  - Wiele pików, asymetrie: zmiany tempa, poprawki i zatrzymania.

Wskazówka: skonfrontuj `velocity_ratio` i kształt wykresu z `interruptions_count` i `rapid_velocity_changes_count`.

---

### Strategia rysowania (`strategy_metrics`)
Zwracane przez `_calculate_strategy_metrics()`:
- `initial_expansion_ratio` – stosunek pola bbox pierwszych 3 kresek do pola bbox całego rysunku.
  - Wysokie (bliżej 1): start „od ogółu” – pierwsze kreski obejmują dużą część figury.
  - Niskie (bliżej 0): start „od szczegółu” – mały fragment, potem ekspansja.
- `mean_inter_stroke_distance` – średni dystans „w powietrzu” między końcem jednej kreski a początkiem następnej.
  - Niski: idzie „po kolei”, lokalna kontynuacja.
  - Wysoki: skacze po płótnie, chaotyczne przełączanie regionów.
- `drawing_direction_vector {dx, dy}` – średni wektor przesunięcia środków ciężkości kolejnych kresek.
  - Kierunek dominującego postępu (np. lewo→prawo, góra→dół). Duże wartości |dx| lub |dy| wskazują spójny kierunek pracy.
- `num_strokes` – liczba kresek (zgodna z `interruptions_count + 1` przy typowym wejściu).

---

### Dane geometryczne pociągnięć
- `strokes_data` – lista list punktów: `[unix_ts, perf_ts, x_px, y_px, norm_x, norm_y]`. 
  - Użycie: dokładna rekonstrukcja trajektorii, korelacja z danymi Pupil (jeśli używasz mapowania spojrzeń).

---

### Jak krok po kroku „czytać” pojedynczy rysunek
1) Zacznij od czasu i przerw: `duration_s`, `actual_drawing_duration_s`, `interruptions_count`, `avg_interruption_duration_s`.
2) Zobacz dynamikę: `velocities`, `velocity_ratio`, `rapid_velocity_changes_count`, wykres prędkości.
3) Oceń ekonomię ruchu: `efficiency_ratio` (próg orientacyjny >2.5 = mało efektywnie).
4) Oceń poprawki/szorowanie: `overdrawing_score`, `max_local_density` oraz `heatmap`.
5) Zbadaj strategię: `initial_expansion_ratio`, `mean_inter_stroke_distance`, `drawing_direction_vector`, `num_strokes`.
6) Zweryfikuj wizualnie: `overlay_filename` (dokładność względem wzorca), `heatmap_filename` (miejsca problematyczne).

---

### Przykładowe interpretacje progowe i wzajemne zależności
- Wysokie `overdrawing_score` + gorąca `heatmap` + duże `max_local_density` → wiele poprawek w jednym rejonie; sprawdź `direction_changes_count` i `redo/undo`.
- Niskie `velocity_ratio` + wiele pików na wykresie + duże `rapid_velocity_changes_count` → rysowanie przerywane, skokowe tempo.
- Wysokie `mean_inter_stroke_distance` + wysokie `revisits_count` → skakanie po obszarach i wracanie do wcześniejszych części.
- `initial_expansion_ratio` niskie, ale dobra `overlay` i niski `overdrawing_score` → strategia „od szczegółu”, ale pewna i czysta.
- `efficiency_ratio` wysokie i równocześnie niskie `velocity_ratio` → długa, zygzakowata trajektoria z przyspieszeniami–hamowaniami.

---

### Jak zastosować to do Twoich danych
- W pliku `pupil\summary.json` każdy wpis w `drawings[]` zawiera powyższe metryki. 
- Aby przygotować opis „dla każdego obrazu”, przejdź po elementach `drawings` i dla każdego wypisz kluczowe pola z krótką interpretacją wg powyższych reguł. Prosta „mapa” opisu dla jednego rysunku:
  - Id: `index`, Plik: `filename`
  - Czas: `duration_s` (całość), `actual_drawing_duration_s` (rysowanie), przerwy: `interruptions_count`, `avg_interruption_duration_s`
  - Dynamika: `avg_velocity`, `max_velocity`, `velocity_ratio`, `rapid_velocity_changes_count`
  - Ekonomia: `efficiency_ratio`
  - Poprawki: `overdrawing_score`, `revisits_count`, `max_local_density` (@ `max_local_density_coords`)
  - Strategia: `initial_expansion_ratio`, `mean_inter_stroke_distance`, `drawing_direction_vector`, `num_strokes`
  - Weryfikacja wizualna: `overlay_filename`, `heatmap_filename`, `velocity_profile_filename`

Jeśli chcesz, mogę przejść po Twoim konkretnym `summary.json` i wygenerować tabelaryczny raport per rysunek (z krótką diagnozą przy każdej metryce). Daj znać, czy chcesz pełny raport, czy skrócone wnioski dla wybranych obrazów.