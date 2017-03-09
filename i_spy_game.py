
"""
Project M.A.R.T.A.

I Spy Game

This game enables Nao (https://www.ald.softbankrobotics.com/en/cool-robots/nao) to play
the famous "I Spy" game (https://en.wikipedia.org/wiki/I_spy) where the user needs to
guess which word the robot is "thinking" about. It does so by using Nao's internal speech
recognition system (from Nuance) to respond to user input and Microsoft Cognitive Services
computer vision API together with the linguistic analysis tools to choose a noun based on
what Nao's top camera (http://doc.aldebaran.com/2-1/family/robots/video_robot.html) sees.

Presentation during the hackathon:
https://youtu.be/_cYu16jrw-w

Authors:
Daniel Hernandez Garcia (https://github.com/dhgarcia):
- Nao movements and dialogues (creation and interfacing).
- Gameplay

Frederico Belmonte Klein (https://github.com/frederico-klein):
- "I Spy" game initial idea.
- Gameplay.
- Wikipedia engine and external speech recognition (not integrated... it was a Hackathon, only 48hs!)

John Doe (https://en.wikipedia.org/wiki/John_Doe):
- Random jokes.

Massimiliano Patacchiola (http://mpatacchiola.github.io/):
- Nao video streaming interface.
- M.A.R.T.A. logo.

Marta Romeo (???):
- Spiritual support.

Mina Marmpena (https://www.researchgate.net/profile/Mina_Marmpena):
- Spiritual support.

Ricardo de Azambuja (http://ricardodeazambuja.com):
- Nao speech recognition interfacing.
- MS Cognitive Services API interfacing.
- Gameplay

Riccardo Polvara (https://www.researchgate.net/profile/Riccardo_Polvara):
- Spiritual support.
- Introduced us to this: https://www.youtube.com/watch?v=JAFQFvSPhQ8

Disclaimer:
- We assume NO responsibility for shortening the amount of time until singularity (https://en.wikipedia.org/wiki/Technological_singularity).
- No Naos were harmed in the making of this game.

TODO:
- Organize the whole code (currently, it's a bunch of things put together in a hurry)
- Divide the exception handling into smaller sections (currently, we can't even avoid quitting when the translation fails)
- Write the docstrings and add extra comments before we forget why did what we did.
- Launch an external process to show the current image and what was effectivelly sent to the cloud.
- Replace mtranslate to a call to BING or Google translation API.
- PEPify the code

Launch the webserver:
python -m SimpleHTTPServer 8000
"""

import os

import numpy
import matplotlib.pyplot as plt
import time


import requests

import StringIO
from PIL import Image

from naoqi import ALProxy

import almath

import mtranslate

from speech_recognition import *

img_loaded = pythonModule = SpeachRec = myBroker = None

def foo(NAO_IP = "192.168.1.104", NAO_PORT = 9559):
    global SpeachRec, myBroker, pythonModule, img_loaded

    # Variables
    _url_vision_analise = 'https://westus.api.cognitive.microsoft.com/vision/v1.0/analyze'
    _url_vision_describe = 'https://westus.api.cognitive.microsoft.com/vision/v1.0/describe'
    _url_linguistic = 'https://westus.api.cognitive.microsoft.com/linguistics/v1.0/analyze'

    _maxNumRetries = 10


    _key_vision = 'db463f42f29b464ea8853fe2f9547ba1' #Here you have to paste your primary key (mine is invalid now...)
    # _key_emotion = '77d1221c40be49198fd278132ea4fdca' #Here you have to paste your primary key (mine is invalid now...)
    _key_ling = 'f4d387f3fe344e82911c57f4fcb38303'
    # https://www.microsoft.com/cognitive-services/en-us/sign-up


    def to_stream(img, format='PNG'):
        imgdata = StringIO.StringIO() # Behaves just like an openned file
        pil = Image.fromarray(numpy.copy(img))
        if format=='PNG':
            pil.save(imgdata, format='PNG', quality=0.3, optimize=True)
        elif format=='JPEG':
            pil.save(imgdata, format='JPEG', quality=50, optimize=True)
        imgdata.seek(0)
        return imgdata.getvalue()


    def processRequest( json, data, headers, params, _url):

        """
        Helper function to process the request to Project Oxford

        Parameters:
        json: Used when processing images from its URL. See API Documentation
        data: Used when processing image read from disk. See API Documentation
        headers: Used to pass the key information and the data type request
        """

        retries = 0
        result = None

        while True:

            response = requests.request( 'post', _url, json = json, data = data, headers = headers, params = params )

            if response.status_code == 429:

                print( "Message: %s" % ( response.json()['error']['message'] ) )

                if retries <= _maxNumRetries:
                    time.sleep(1)
                    retries += 1
                    continue
                else:
                    print( 'Error: failed after retrying!' )
                    break

            elif response.status_code == 200 or response.status_code == 201:

                if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                    result = None
                elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                    if 'application/json' in response.headers['content-type'].lower():
                        result = response.json() if response.content else None
                    elif 'image' in response.headers['content-type'].lower():
                        result = response.content
            else:
                print( "Error code: %d" % ( response.status_code ) )
                print( "Message: %s" % ( response.json()['error']['message'] ) )

            break

        return result

    try:
        # Subscribe to the proxies services

        # We need this broker to be able to construct
        # NAOqi modules and subscribe to other modules
        # The broker must stay alive until the program exists
        myBroker = ALBroker("myBroker",
           "0.0.0.0",   # listen to anyone
           0,           # find a free port and use it
           NAO_IP,         # parent broker IP
           NAO_PORT)       # parent broker port


        # Warning: SpeachRec must be a global variable
        # The name given to the constructor must be the name of the
        # variable
        # global SpeachRec
        SpeachRec = SpeachRecModule("SpeachRec")

        memProxy = ALProxy("ALMemory")

        #Getting the nao proxies
        video = ALProxy("ALVideoDevice")
        tts = ALProxy("ALTextToSpeech")

        # tts_service  = session.service("ALTextToSpeech")
        motion_service  = ALProxy("ALMotion")
        # animation_player_service = ALProxy("ALAnimationPlayer")

        asr_service = ALProxy("ALAnimatedSpeech")


        # create python module
        class eventModule(ALModule):
            """Catches an Event"""

            def pythondatachanged(self, strVarName, value):
                """callback when data change"""
                # print "EVENT: datachanged", strVarName, " ", value
                global img_loaded
                img_loaded = True

            # def _pythonPrivateMethod(self, param1, param2, param3):
            #     global check


        pythonModule = eventModule("pythonModule")

        memProxy.subscribeToEvent("PythonImageLoaded","pythonModule", "pythondatachanged") #  event is case sensitive !

        # set the local configuration
        configuration = {"bodyLanguageMode":"contextual"}


        if not motion_service.robotIsWakeUp():
            motion_service.wakeUp()


        # say the text with the local configuration
        asr_service.say("Hello! I'm Multi-purpose Anthropomorphic Robot for Timely Assistance, but you can call me Marta!", configuration)
        asr_service.say("I'm powered by Microsoft Cognitive Services, APIs. I can generated meaningful descriptions of scenes, and also linguistic analysis, of that description.", configuration)
        #asr_service.say("Hello! ^start(animations/Stand/Gestures/Hey_1) Nice to meet you!")

        asr_service.say("Let's play a game called ^start(animations/Stand/Gestures/IDontKnow_1), I spy with my little eye.")

        def look_around(t):
            #look around
            names  = ["HeadPitch","HeadYaw"]
            angleLists  = [[-25.0*almath.TO_RAD, 25.0*almath.TO_RAD, -25.0*almath.TO_RAD, 0.0,],
                        [45.0*almath.TO_RAD, -45.0*almath.TO_RAD, 0.0]]
            timeLists   = [[1.0, 3.0, 5.0, 6.0], [ 2.0, 4.0, 6.0]]
            isAbsolute  = True
            motion_service.post.angleInterpolation(names, angleLists, timeLists, isAbsolute)
            time.sleep(t)

        def wrong_ans(t):
            #WRONG Answer animation
            asr_service.say("Wrong! ^start(animations/Stand/Gestures/No_3) You are embarrassingly bad at this game")
            time.sleep(t)

        def right_ans(t):
            #RiGHT Answer animation
            asr_service.say("Alright! ^start(animations/Stand/Gestures/Enthusiastic_5) alright, alright. You got this one!")
            time.sleep(t)

        try:
            #"Test_Video", CameraIndex=1, Resolution=1, ColorSpace=0, Fps=5
            #CameraIndex= 0(Top), 1(Bottom)
            #Resolution= 0(160*120), 1(320*240), VGA=2(640*480), 3(1280*960)
            #ColorSpace= AL::kYuvColorSpace (index=0, channels=1), AL::kYUV422ColorSpace (index=9,channels=3),
            #AL::kRGBColorSpace RGB (index=11, channels=3), AL::kBGRColorSpace BGR (to use in OpenCV) (index=13, channels=3)
            #Fps= OV7670 VGA camera can only run at 30, 15, 10 and 5fps. The MT9M114 HD camera run from 1 to 30fps.
            #Settings for resolution 1 (320x240)
            resolution_type = 1
            fps=10
            cam_w = 320
            cam_h = 240
            #Settigns for resolution 2 (320x240)
            #resolution_type = 2
            #fps = 15
            #cam_w = 640
            #cam_h = 480
            camera_name_id_top = video.subscribeCamera("TopCam", 0, resolution_type, 13, fps)

        except e:
            print "VIDEO ERROR: "+str(err)

        plt.ion()

        while True:
            # In this state it is captured a stream of images from
            # the NAO camera and it is converted in a Numpy matrix
            #Get Images from camera
            #TopCam
            time.sleep(5.0)
            naoqi_img = video.getImageRemote(camera_name_id_top)
            if(naoqi_img != None):
                img = (
                       numpy.reshape(
                          numpy.frombuffer(naoqi_img[6], dtype='%iuint8' % naoqi_img[2]),
                          (naoqi_img[1], naoqi_img[0], naoqi_img[2])
                                  )
                       )
            else:
               img = numpy.zeros((cam_h, cam_w))
            img_top = numpy.copy(img)

            received_image = Image.fromarray(numpy.copy(img[:,:,::-1]))
            random_name = str(numpy.random.rand())+".jpg"
            received_image.save(random_name, "JPEG")

            img_loaded = False
            URL="http://192.168.1.103:8000/"+random_name
            memProxy.raiseEvent("PythonLoadImage", URL)

            

            while not img_loaded:
                time.sleep(0.1)
            
	    # os.remove(os.getcwd()+"/"+random_name)

            #Show the image
            plt.imshow(img[:,:,::-1])

            data = to_stream(img[:,:,::-1])


            headers = dict()
            headers['Ocp-Apim-Subscription-Key'] = _key_vision
            headers['Content-Type'] = 'application/octet-stream'

            json = None

            params = {'visualFeatures': 'Description', 'language': 'en'}

            result = processRequest( json, data, headers, params, _url_vision_analise)

            # https://westus.dev.cognitive.microsoft.com/docs/services/56ea598f778daf01942505ff/operations/56ea5a1cca73071fd4b102bb
            input_text = result['description']['captions'][0]['text']
            print "SCENE DESCRIPTION: "+str(input_text)

            headers = dict()
            headers['Ocp-Apim-Subscription-Key'] = _key_ling

            body = {
                "language" : "en",
                "analyzerIds" : ["4fa79af1-f22c-408d-98bb-b7d7aeef7f04"],
                "text" : input_text}

            result = processRequest( body, None, headers, None, _url_linguistic)
            ling_anal = result[0]['result'][0]
            print "SCENE DESCRIPTION ANALISYS: "+str(ling_anal)

            NN_list = list()
            for i,t in enumerate(ling_anal):
                if t[:2]=='NN':
                    if i>0:
                        if ling_anal[i-1][:2]=='JJ':
                            NN_list.append((input_text.split(' '))[i-1] + " " +(input_text.split(' '))[i])
                        else:
                            NN_list.append((input_text.split(' '))[i])
                    else:
                        NN_list.append((input_text.split(' '))[i])

            r_idx = numpy.random.randint(0,high=len(NN_list))

            look_around(0.01)

            vocabulary = ["quit", "bye", "another", str(NN_list[r_idx])]
            tts.say("I spy with my little eye, something beginning with " + str(NN_list[r_idx][0]))
            tts.say("Can you guess what it is?")
            tts.say("You have five seconds to say it.")

            SpeachRec.my_set_vocabulary(vocabulary)
            plt.pause((60/20.)/10)
            time.sleep(5-(60/20.)/10)
            SpeachRec.pause_speech_recognition(True)

            print "DEBUG:" + str(SpeachRec.word_from_nao)

            print "DEBUG:" + str(NN_list[r_idx])

            if SpeachRec.word_from_nao[0]==vocabulary[-1]:
                right_ans(0.01)
                tts.say("Well done! The word was "+vocabulary[-1])
            else:
                wrong_ans(0.01)
                languages_abr = ['de','es','fr']
                languages = ['German','Spanish','French']
                hint = numpy.random.randint(0,high=len(languages_abr))
                tts.say("I will give you a hint.")

                trans = mtranslate.translate(NN_list[r_idx],to_language=languages_abr[hint])

                tts.say("In "+languages[hint]+", they would say ")
                tts.setLanguage(languages[hint])
                tts.say(str(trans.encode('ascii','ignore')))
                tts.setLanguage("English")
                tts.say("Can you guess now?")
                tts.say("You have five more seconds to say it.")
                # SpeachRec.change_language(languages[hint])

                SpeachRec.pause_speech_recognition(False)
                time.sleep(5)
                SpeachRec.pause_speech_recognition(True)

                if SpeachRec.word_from_nao[0]==vocabulary[-1]:
                    right_ans(0.01)
                    tts.say("Well done! The word was "+vocabulary[-1])
                else:
                    wrong_ans(0.01)
                    tts.say("Sorry, it was "+str(NN_list[r_idx]))
	    # say something to get head back to position
	    asr_service.say("Let's play again ^start(animations/Stand/Gestures/IDontKnow_1), If you don't mind.")

    except Exception, e:
        print "ERROR PARENT LOOP:" +str(e)
        print NN_list[r_idx]

    finally:
        tts.setLanguage("English")
        tts.say("I spy with my little eye, something beginning with S")
        tts.say("See you later! Bye.")

        video.unsubscribe(camera_name_id_top)

        SpeachRec.asr.setAudioExpression(False)
        SpeachRec.asr.setVisualExpression(False)
        SpeachRec.asr.unsubscribe("Test_ASR")
        # motion_service.rest()
        myBroker.shutdown()
        sys.exit(0)


if __name__=="__main__":
    foo()
