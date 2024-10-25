from threading import Thread, Lock
from vicon_dssdk import ViconDataStream

class ViconLocator:

    def __init__(self, vicon_server_ip='192.168.68.54', vicon_server_port='801', log_file="vicon_log.txt"):
        self.vicon_server_ip = vicon_server_ip
        self.vicon_server_port = vicon_server_port
        # self.log = open(log_file, 'w')
        self.vicon_client = ViconDataStream.Client()

        try:
            print("Connecting to Vicon server ...")
            self.vicon_client.Connect(f"{self.vicon_server_ip}:{self.vicon_server_port}")
            self.vicon_client.SetBufferSize(3)
            self.vicon_client.EnableSegmentData()

            has_frame = False
            while not has_frame:
                self.vicon_client.GetFrame()
                has_frame = True
            
            print("frame lost from ViCon")
        except ViconDataStream.DataStreamException as e:
            print('Vicon Datastream Error: ', e)

    def log_data(self, data):
        self.log.write(data)
        self.log.flush()

    def get_position(self, id):
        """
        Returns the X and Y coordinates of the specified Vicon object.
        """
        self.vicon_client.GetFrame()
        subject_names = self.vicon_client.GetSubjectNames()
        global_position = self.vicon_client.GetSegmentGlobalTranslation(id,id)
        x_vicon = global_position[0][0] / 10
        y_vicon = global_position[0][1] / 10
        
        # print(f"{id} at x: {x_vicon} \t y: {y_vicon}")
        
        return x_vicon, y_vicon

    def get_client(self):
        return self.vicon_client
