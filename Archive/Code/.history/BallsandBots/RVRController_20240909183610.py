from pylsl import StreamInfo, StreamOutlet
import time

class RVR_Controller:
    
    def __init__(self,RVR_ip,RVR_id):
        # Create a new stream info (name, data type, number of channels, sample rate, type)
        info = StreamInfo('SpheroRVRControl', 'RVR', 2, 10, 'float32', 'myuid34234')

        # Create an outlet to stream data
        self.outlet = StreamOutlet(info)
        
        
    def drive_control(self,speed,heading):
        self.outlet.push_sample([speed, heading])
