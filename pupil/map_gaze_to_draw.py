import pandas as pd
import json
import numpy as np
from bisect import bisect_left

# Parametry
GAZE_CSV_PATH = 'pupil\\gaze_positions.csv'
SUMMARY_JSON_PATH = 'pupil\\summary.json'
OUTPUT_CSV_PATH = 'pupil\\mapped_gaze_to_draw.csv'

# Użytkownik podał: 1769353100.xxxxx (komputer) vs 2.xxxx (gaze)
# To oznacza, że offset powinien być rzędu 1769353098.
# Jeśli Mean time offset z urządzenia to -113.23 ms, to jest to tylko poprawka synchronizacji,
# ale bazowy offset (moment startu zegara urządzenia w czasie Unix) musi zostać dodany.

# Spróbujmy wyliczyć bazowy offset na podstawie pierwszego timestampu rysowania i gaze.
# Z summary.json: test_start_unix = 1769351405.1925712
# Pierwszy gaze_timestamp w csv to ok. 2.339
# Szacowany BASE_OFFSET = 1769351405.1925712 - 2.339 = 1769351402.853

BASE_OFFSET = 1769351402.853 
OFFSET_MS = -113.23  # Poprawka milisekundowa
OFFSET_S = BASE_OFFSET + (OFFSET_MS / 1000.0)

def map_gaze_to_draw():
    print(f"Wczytywanie danych z {GAZE_CSV_PATH}...")
    gaze_df = pd.read_csv(GAZE_CSV_PATH)
    
    # Przeliczenie timestampu gaze na Unixowy
    # Wzór: Unix = Device + Offset
    gaze_df['gaze_unix_ts'] = gaze_df['gaze_timestamp'] + OFFSET_S
    
    print(f"Wczytywanie danych z {SUMMARY_JSON_PATH}...")
    with open(SUMMARY_JSON_PATH, 'r', encoding='utf-8') as f:
        summary_data = json.load(f)
    
    # Przygotowanie danych strokes (spłaszczenie do jednej listy punktów)
    # Punkt w summary.json: [unix_ts, perf_ts, x_px, y_px, norm_x, norm_y]
    draw_points = []
    for drawing in summary_data.get('drawings', []):
        for stroke in drawing.get('strokes_data', []):
            for pt in stroke:
                draw_points.append({
                    'unix_ts': pt[0],
                    'draw_norm_x': pt[4],
                    'draw_norm_y': pt[5]
                })
    
    if not draw_points:
        print("Brak danych o pociągnięciach (strokes_data) w summary.json.")
        return

    # Sortowanie punktów rysowania po czasie dla szybkiego wyszukiwania
    draw_points.sort(key=lambda x: x['unix_ts'])
    draw_timestamps = [p['unix_ts'] for p in draw_points]
    
    if draw_timestamps:
        print(f"Zakres czasu strokes (Unix): {draw_timestamps[0]} do {draw_timestamps[-1]}")
    
    gaze_unix_vals = gaze_df['gaze_unix_ts'].tolist()
    if gaze_unix_vals:
        print(f"Zakres czasu gaze (Unix): {min(gaze_unix_vals)} do {max(gaze_unix_vals)}")
    
    print("Mapowanie gaze na strokes (najbliższy sąsiad)...")
    
    mapped_draw_x = []
    mapped_draw_y = []
    time_diffs = []
    is_drawing = []

    # Maksymalna dopuszczalna różnica czasu między gaze a pociągnięciem (np. 100ms)
    # Jeśli różnica jest większa, uznajemy, że w tym czasie nie było aktywnego pociągnięcia
    MAX_TIME_DIFF = 0.1 

    for gaze_ts in gaze_df['gaze_unix_ts']:
        # Znalezienie najbliższego timestampu za pomocą bisect
        pos = bisect_left(draw_timestamps, gaze_ts)
        
        best_pt = None
        min_diff = float('inf')
        
        # Sprawdzamy element znaleziony i poprzedni
        for i in [pos - 1, pos]:
            if 0 <= i < len(draw_timestamps):
                diff = abs(draw_timestamps[i] - gaze_ts)
                if diff < min_diff:
                    min_diff = diff
                    best_pt = draw_points[i]
        
        if best_pt and min_diff <= MAX_TIME_DIFF:
            mapped_draw_x.append(best_pt['draw_norm_x'])
            mapped_draw_y.append(best_pt['draw_norm_y'])
            time_diffs.append(min_diff)
            is_drawing.append(True)
        else:
            mapped_draw_x.append(np.nan)
            mapped_draw_y.append(np.nan)
            time_diffs.append(min_diff if best_pt else np.nan)
            is_drawing.append(False)

    # Dodanie zmapowanych kolumn do dataframe
    gaze_df['draw_norm_x'] = mapped_draw_x
    gaze_df['draw_norm_y'] = mapped_draw_y
    gaze_df['time_diff_s'] = time_diffs
    gaze_df['is_drawing'] = is_drawing

    # Wybranie istotnych kolumn do zapisu
    output_columns = [
        'gaze_unix_ts', 
        'norm_pos_x', 'norm_pos_y', 
        'draw_norm_x', 'draw_norm_y', 
        'is_drawing', 'time_diff_s'
    ]
    
    gaze_df[output_columns].to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"Zapisano zmapowane dane do: {OUTPUT_CSV_PATH}")
    
    # Statystyki
    drawing_samples = sum(is_drawing)
    total_samples = len(is_drawing)
    print(f"Zmapowano {drawing_samples} z {total_samples} próbek gaze jako 'w trakcie rysowania' (próg {MAX_TIME_DIFF}s).")

if __name__ == "__main__":
    map_gaze_to_draw()
