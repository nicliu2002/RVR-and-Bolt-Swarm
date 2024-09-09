class MAS:

    vicon_server_ip = 'l-hvhnpt3'
    #vicon_server_ip = '192.168.68.52'
    vicon_server_port = '801'

    def __init__(self):
        self.log = open("mas_logViconSpheroSwarm1.txt", 'w')
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

        except ViconDataStream.DataStreamException as e:
            print('Vicon Datastream Error: ', e)


    def log_data(self, data):
        self.log.write(data)

    def get_client(self):
        return self.vicon_client