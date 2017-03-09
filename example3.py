import time, argparse

from naoqi import ALProxy


#------------------------Initialisation------------------------#
try:
    from naoqi import ALModule
    from naoqi import ALProxy
    from naoqi import ALBroker

except ImportError, err:
    print "Error when creating proxy:"
    print str(err)
    raise err
    exit(1)


class MyAudioModule(ALModule):
    def __init__( self, strName, args):
        ALModule.__init__( self, strName );

        self.saveFile=open('test.raw', 'wb')
        # Create a proxy to ALAudioDevice
        try :
            self.ALAudioRecorderProxy = ALProxy("ALAudioRecorder", args.IP, args.PORT)
        except Exception, e:
            print "Error when creating proxy on ALAudioDevice:"
            print str(e)
            exit(1)


    def startAudioTest(self):
        print 'Subscribe AudioDevice will start the processRemote'
        self.ALAudioRecorderProxy.startMicrophonesRecording("/home/parallels/test.wav", "wav", 16000, [0,0,1,0])
        time.sleep(5)
        print 'Unsubscribe AudioDevice will stop the processRemote'
        self.ALAudioRecorderProxy.stopMicrophonesRecording()
        time.sleep(1)



#------------------------Main------------------------#
if __name__ == "__main__":
    print "#----------Audio Script----------#"
    # Replace here with your robot's IP address
    ## Parse options
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip",
                      help="IP adress of the robot",
                      dest="IP",
                      default='192.168.1.100')

    parser.add_argument("--pport",
                      help="Port of communication with the robot",
                      dest="PORT",
                      default=9559)

    parser.add_argument("--rate",
                    help="Sampling rate",
                    dest="rate",
                    default=48000)

    args=parser.parse_args()

    args.rate = int(args.rate)
    args.PORT = int(args.PORT)

    pythonBroker = ALBroker("pythonBroker", "0.0.0.0", 9600, args.IP, args.PORT)
    ALSoundDiagnostic = MyAudioModule("ALSoundDiagnostic",args)
    ALSoundDiagnostic.startAudioTest()
