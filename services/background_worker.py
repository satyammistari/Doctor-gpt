import threading
import time
from kivy.clock import Clock

class BackgroundWorker(threading.Thread):
    def __init__(self, callback, interval=1.0):
        super().__init__(daemon=True)
        self._stop_event = threading.Event()
        self.callback = callback  
        self.interval = interval

    def run(self):
        counter = 0
        while not self._stop_event.is_set():
            time.sleep(self.interval)
            counter += 1
            Clock.schedule_once(lambda dt, c=counter: self.callback(f"Tick {c}"))

    def stop(self):
        self._stop_event.set()
