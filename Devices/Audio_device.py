import pyaudio
import wave
import time
import threading

from .Devices import Device, Devices

class Audio(Device):
    def __init__(self, speed_obs, dist_obs, tooClose_obs, interface = None):
        self._interface = interface
        self._speed = speed_obs
        self._distance = dist_obs
        self._tooClose = tooClose_obs

        self._pyaudio = pyaudio.PyAudio()

        self._speed.register_observer(self.safeDistanceCheck)
        self._distance.register_observer(self.safeDistanceCheck)

        self._playing = False

    def safeDistanceCheck(self, _):
        if self.tooClose():
            if not self._playing:
                audio_thread = threading.Thread(target=self.alert)
                audio_thread.start()
                self._tooClose.value = True               

    def tooClose(self):
        secure_dist = (self._speed.value / 10)
        secure_dist = secure_dist * secure_dist
        secure_dist = secure_dist * 2 # Assuming wet floor

        return self._speed.value > 20 and self._distance.value < secure_dist

    def alert(self):
        self._playing = True

        while self.tooClose():
            wf = wave.open('Sounds/beep.wav', 'rb')

            def callback(in_data, frame_count, time_info, status):
                data = wf.readframes(frame_count)
                return (data, pyaudio.paContinue)
                
        
            stream = self._pyaudio.open(
                format=self._pyaudio.get_format_from_width(wf.getsampwidth()), 
                channels=wf.getnchannels(), 
                rate=wf.getframerate(), 
                output=True, 
                output_device_index=self._interface,
                stream_callback=callback 
                )
            stream.start_stream()
            while stream.is_active():
                time.sleep(0.1)

            stream.stop_stream()
            stream.close()
            wf.close()
            
        self._tooClose.value = False
        self._playing = False

