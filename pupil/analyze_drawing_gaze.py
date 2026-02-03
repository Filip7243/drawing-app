import pandas as pd
import numpy as np
import json
import os
from bisect import bisect_left

# Ścieżki do plików
PUPIL_DIR = 'pupil'
GAZE_CSV = os.path.join(PUPIL_DIR, 'gaze_positions.csv')
SUMMARY_JSON = os.path.join(PUPIL_DIR, 'summary.json')
EVENT_TXT = os.path.join(PUPIL_DIR, 'event.txt')
EVENT_TIMESTAMPS_NPY = os.path.join(PUPIL_DIR, 'event_timestamps.npy')
OUTPUT_CSV = os.path.join(PUPIL_DIR, 'final_analysis.csv')

def load_events():
    """Wczytuje eventy z plików tekstowych i npy."""
    with open(EVENT_TXT, 'r') as f:
        event_names = [line.strip().split(':', 1)[1] if ':' in line else line.strip() for line in f if line.strip()]
    
    event_timestamps = np.load(EVENT_TIMESTAMPS_NPY)
    
    return list(zip(event_names, event_timestamps))

def calculate_offset(events, summary_data):
    """Oblicza średni offset między czasem Pupil a czasem Unix."""
    offsets = []
    
    # Mapowanie nazw eventów na klucze w summary.json
    # W TestMetrics.py: event_name = f"drawing_{index}_started"
    
    drawings = summary_data.get('drawings', [])
    for drawing in drawings:
        idx = drawing['index']
        start_name = f"drawing_{idx}_started"
        end_name = f"drawing_{idx}_ended"
        
        # Znajdź te eventy w nagraniu Pupil
        p_start = next((t for n, t in events if n == start_name), None)
        p_end = next((t for n, t in events if n == end_name), None)
        
        if p_start is not None:
            offsets.append(drawing['started_at_ts'] - p_start)
        if p_end is not None:
            offsets.append(drawing['finished_at_ts'] - p_end)
            
    if not offsets:
        # Próba rezerwowa: start testu
        p_begin = next((t for n, t in events if n == 'recording.begin'), None)
        if p_begin is not None:
            return summary_data['test_start_unix'] - p_begin
        
        return 0
    
    return sum(offsets) / len(offsets)

def analyze():
    print("Rozpoczynanie analizy...")
    
    if not os.path.exists(GAZE_CSV) or not os.path.exists(SUMMARY_JSON):
        print("Błąd: Brak wymaganych plików (gaze_positions.csv lub summary.json).")
        return

    # 1. Wczytaj dane
    events = load_events()
    print(events)
    with open(SUMMARY_JSON, 'r', encoding='utf-8') as f:
        summary_data = json.load(f)
    
    # 2. Oblicz offset
    offset = calculate_offset(events, summary_data)
    print(f"Wyliczony offset (Unix - Pupil): {offset}")

    # 3. Wczytaj gaze
    gaze_df = pd.read_csv(GAZE_CSV)
    gaze_df['unix_ts'] = gaze_df['gaze_timestamp'] + offset
    
    # 4. Przygotuj punkty rysowania do szybkiego mapowania
    draw_points = []
    for drawing in summary_data.get('drawings', []):
        for stroke in drawing.get('strokes_data', []):
            for pt in stroke:
                # pt: [unix_ts, perf_ts, x_px, y_px, norm_x, norm_y]
                draw_points.append({
                    'ts': pt[0],
                    'draw_x': pt[4],
                    'draw_y': pt[5],
                    'drawing_idx': drawing['index']
                })
    
    draw_points.sort(key=lambda x: x['ts'])
    draw_ts_list = [p['ts'] for p in draw_points]
    
    # 5. Mapowanie
    mapped_draw_x = []
    mapped_draw_y = []
    mapped_drawing_idx = []
    is_drawing = []
    
    MAX_DIFF = 0.05 # 50ms próg synchronizacji
    
    print("Mapowanie gaze na rysowanie...")
    for g_ts in gaze_df['unix_ts']:
        pos = bisect_left(draw_ts_list, g_ts)
        
        best_pt = None
        min_diff = float('inf')
        
        for i in [pos - 1, pos]:
            if 0 <= i < len(draw_ts_list):
                diff = abs(draw_ts_list[i] - g_ts)
                if diff < min_diff:
                    min_diff = diff
                    best_pt = draw_points[i]
        
        if best_pt and min_diff <= MAX_DIFF:
            mapped_draw_x.append(best_pt['draw_x'])
            mapped_draw_y.append(best_pt['draw_y'])
            mapped_drawing_idx.append(best_pt['drawing_idx'])
            is_drawing.append(True)
        else:
            mapped_draw_x.append(None)
            mapped_draw_y.append(None)
            mapped_drawing_idx.append(None)
            is_drawing.append(False)
            
    gaze_df['mapped_draw_x'] = mapped_draw_x
    gaze_df['mapped_draw_y'] = mapped_draw_y
    gaze_df['drawing_index'] = mapped_drawing_idx
    gaze_df['is_drawing_active'] = is_drawing
    
    # Obliczanie odległości euklidesowej między gaze a rysowaniem (współrzędne znormalizowane)
    gaze_df['gaze_draw_dist'] = np.sqrt(
        (gaze_df['norm_pos_x'] - gaze_df['mapped_draw_x'].astype(float))**2 + 
        (gaze_df['norm_pos_y'] - gaze_df['mapped_draw_y'].astype(float))**2
    )
    
    # 6. Zapisz wynik
    # Wybieramy najważniejsze kolumny
    cols_to_save = ['unix_ts', 'gaze_timestamp', 'norm_pos_x', 'norm_pos_y', 
                    'mapped_draw_x', 'mapped_draw_y', 'gaze_draw_dist', 'drawing_index', 'is_drawing_active']
    
    # Jeśli gaze_positions.csv ma inne kolumny (np. confidence), warto je zachować
    if 'confidence' in gaze_df.columns:
        cols_to_save.insert(4, 'confidence')
        
    gaze_df[cols_to_save].to_csv(OUTPUT_CSV, index=False)
    print(f"Analiza zakończona. Wynik zapisano w: {OUTPUT_CSV}")
    
    # Statystyki
    print(f"Liczba próbek gaze: {len(gaze_df)}")
    print(f"Liczba próbek podczas rysowania: {sum(is_drawing)}")

if __name__ == "__main__":
    analyze()
