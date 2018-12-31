import snowboydecoder
import sys
import signal
import speech_recognition as sr


interrupted = False

# if the stop word is detected
stop_word_detected = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


def interact_with_device(recognizer, microphone):
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print "let's talk to the device !"

        # set up the response object
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=1)
        except sr.WaitTimeoutError:
            response["error"] = "Timeout"
            return response

    # fill the enum with the results
    try:
        response["success"] = True
        response["transcription"] = recognizer.recognize_google(audio, language="fr-CH")
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
        print response["error"]
    except sr.UnknownValueError:
        # speech was unintelligible
        response["success"] = False
        response["error"] = "Unable to recognize speech"
        print response["error"]
    return response


def process_result(result):
    print "let's process the result : "
    text = str(result)  # cast into string
    text.lower()

    # means that the user wants to stop the interaction with the device
    if text.__contains__("stop"):
        global stop_word_detected
        stop_word_detected = True
        return True

    # switching mode
    elif text.__contains__("mode"):
        if text.__contains__("panneau") or text.__contains__("solaire"):
            print "[mode switch] : solar pannel mode"
            return True
        elif text.__contains__("import") or text.__contains__("importations"):
            print "[mode switch] : import mode"
            return True
        elif text.__contains__("export") or text.__contains__("exportation"):
            print "[mode switch] : export mode"
            return True
        else:
            return False

    # display time of the day
    elif text.__contains__("heure"):
        print "[mode switch] : time mode"
        return True

    # wrong command
    else:
        print "vocal command is not valid... try again ! "
        return False


def start_word_detected():
    print("got the start keyword !")
    # first terminate the start detector
    startDetector.terminate()
    # now start the stop detector

    # then start recognizing
    print("now time to start the talk ! ")
    # obtain audio from the microphone
    r = sr.Recognizer()
    m = sr.Microphone()

    while True:
        res = interact_with_device(r, m)
        # if no exception was launched
        if res["error"] is None:
            print(u"You said: {}".format(res["transcription"]))
            processed = process_result(res)
            if processed is True or stop_word_detected is True:
                break

    # if we come here : means that interaction is over
    global stop_word_detected
    stop_word_detected = False
    # start again the thread of the detector
    startDetector.start(detected_callback=start_word_detected,
                        interrupt_check=interrupt_callback,
                        sleep_time=0.03)
    print "detector started again"


if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("Error: need to specify model name")
        print("Usage: python demo.py your.model")
        sys.exit(-1)

    startModel = sys.argv[1]    # start model, the one that launches the interaction

    # capture SIGINT signal, e.g., Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    startDetector = snowboydecoder.HotwordDetector(startModel, sensitivity=0.5)
    print('Listening... Press Ctrl+C to exit')

    # start the thread of the detector
    startDetector.start(detected_callback=start_word_detected,
                        interrupt_check=interrupt_callback,
                        sleep_time=0.03)

