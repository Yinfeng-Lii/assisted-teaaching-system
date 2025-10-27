import pyaudio

p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numberdevices = info.get('deviceCount')

print("Available INPUT DEVICES:")
for i in range(0, numberdevices):
    device_info = p.get_device_info_by_host_api_device_index(0, i)
    if (device_info.get('maxInputChannels')) > 0:
        print(f"  ID: {i} - {device_info.get('name')}")
        
p.terminate()