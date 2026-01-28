from pupil_labs.realtime_api.simple import discover_one_device
import time

print("Looking for the next best device...")
device = discover_one_device(max_search_duration_seconds=10)
if device is None:
    raise SystemExit("No device found.")

# Oszacowanie offsetu czasowego (w ms)
estimate = device.estimate_time_offset()
if estimate is None:
    device.close()
    raise SystemExit("Pupil Companion app is too old or not compatible")

offset_ms = estimate.time_offset_ms.mean
roundtrip_ms = estimate.roundtrip_duration_ms.mean

print(f"Mean time offset: {offset_ms} ms")
print(f"Mean roundtrip duration: {roundtrip_ms} ms")

# Start nagrywania
device.recording_start()
print("Nagrywanie uruchomione")

# Czekaj 15 sekund
time.sleep(5)

# Stop i zapisz
device.recording_stop_and_save()
print("Nagrywanie zatrzymane i zapisane")

device.close()

# Teraz możesz wykorzystać offset do korekcji timestampów:
external_timestamp = time.time()  # Czas lokalny w sekundach od epoki UNIX-a
print(f"External timestamp: {external_timestamp} s")
corrected_timestamp = external_timestamp - offset_ms / 1000.0
print(f"Corrected timestamp: {corrected_timestamp} s")
