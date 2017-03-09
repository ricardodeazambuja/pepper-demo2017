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
            self.ALAudioDevice = ALProxy("ALAudioDevice", args.IP, args.PORT)
        except Exception, e:
            print "Error when creating proxy on ALAudioDevice:"
            print str(e)
            exit(1)

        print "setClientPreferences " + str(args.rate)
        channels = [0,0,1,0]
        isDeinterleaved = False
        isTimeStampped = True # in fact this parameter is not read. Time stamps are always calculated.
        self.ALAudioDevice.setClientPreferences(self.getName(), args.rate, channels, 0, 0)

    def startAudioTest(self):
        print 'Subscribe AudioDevice will start the processRemote'
        self.ALAudioDevice.subscribe(self.getName())
        time.sleep(5)
        print 'Unsubscribe AudioDevice will stop the processRemote'
        self.ALAudioDevice.unsubscribe(self.getName())
        time.sleep(1)

    def processRemote(self, nbOfInputChannels, nbOfInputSamples, timeStamp, inputBuff):
        # print 'Process remote is called every 85 ms'
        t = timeStamp[0]+timeStamp[1]/1e6 # time in s
        print(("%.3f receive audio buffer composed of " +  str(nbOfInputChannels) +" channels and " + str(nbOfInputSamples) + " samples")%t)
        self.saveFile.write(inputBuff)



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
