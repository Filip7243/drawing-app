from pupil_labs.realtime_api.simple import discover_one_device
import time

device = discover_one_device()
device.recording_start()

time.sleep(15)

device.recording_stop_and_save()
