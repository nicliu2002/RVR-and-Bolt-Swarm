from assets import Constants as Cons
from pylsl import resolve_stream, StreamInlet
import time
import threading
import json

class ViconLocator:
    
    def __init__(self, RVR_ID, BOLT_IDs):
        # optional logging variable for future work
        logging = True
        self.RVR_ID = RVR_ID
        self.botLocation = {RVR_ID: [0,0]}
        boltLocations = dict.fromkeys(BOLT_IDs,[0,0])
        self.botLocation.update(boltLocations)
        
        # initiate a location stream for each robot
        self.init_lsl(RVR_ID)

        # sampling rate times/sec
        self.vicon_sr = 100      
        
        self.vicon_lock = threading.Lock()
        self.file_lock = threading.Lock()
    
    # starting lsl stream from vicon bridge    
        
    def init_lsl(self,robot_ID):
        print("looking for Vicon lsl stream...")
        streams = resolve_stream('name', robot_ID)
        print(f"Stream found for {robot_ID}")
        # create a new inlet to read from the stream
        self.inlet = StreamInlet(streams[0])
        threading.Thread(target=self.ViconLocator).start()    
        
    # keeps updating "self variables" that is a dictionary with constant updates to vicon 
        
    def ViconLocator(self):
        while True:
            try:
                # get a new sample (you can also omit the timestamp part if you're not
                # interested in it)
                
                with self.vicon_lock:
                    sample, timestamp = self.inlet.pull_sample()
                    locator_handler_x = float(sample[0]) / 1000               # /1000 to covert from mm to meters
                    locator_handler_y = float(sample[1]) / 1000               # /1000 to covert from mm to meters
                    # round values to make numbers same in all OS (Windows, Linux)
                    locator_handler_x , locator_handler_y = [round(v, 5) for v in [locator_handler_x, locator_handler_y]]
                    
                    # locations are automatically input into the bot locations dictionary --> unify the vicon bridge constants with the bot location constants
                    
                    Cons.location[sample[2]][0] = [locator_handler_x,locator_handler_y]
                    print("location for " + str(sample[2]) + " location is : \t " + str(Cons.location[sample[2]][0]))
                        
                    
            except Exception as e:
                print(e)
                pass
            finally:
                time.sleep(1 / self.vicon_sr)
                
    
    