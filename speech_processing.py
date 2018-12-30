import snowboydecoder
import sys
import signal
import speech_recognition as sr


interrupted = False


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
        audio = recognizer.listen(source, timeout=1, phrase_time_limit=1)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

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
    for i in range(10):
        res = interact_with_device(r, m)
        print(u"You said: {}".format(res["transcription"]))


def stop_word_detected():
    print("got the stop keyword !")
    # first terminate the stop detector
    stopDetector.terminate()
    # now start the start detector
    startDetector.start(detected_callback=start_word_detected,
                        interrupt_check=interrupt_callback,
                        sleep_time=0.03)


if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("Error: need to specify model name")
        print("Usage: python demo.py your.model")
        sys.exit(-1)

    startModel = sys.argv[1]    # start model, the one that launches the interaction
    stopModel = sys.argv[2]  # end model, stops the interaction

    # capture SIGINT signal, e.g., Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    startDetector = snowboydecoder.HotwordDetector(startModel, sensitivity=0.5)
    # stopDetector = snowboydecoder.HotwordDetector(stopModel, sensitivity=0.5)
    print('Listening... Press Ctrl+C to exit')

    # start the thread of the detector
    startDetector.start(detected_callback=start_word_detected,
                        interrupt_check=interrupt_callback,
                        sleep_time=0.03)

