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


def word_detected():
    print("got the keyword ! time to stop the detector now")
    # first stop the detector as it's currently using the mic
    detector.terminate()
    # then start recognizing
    print("now time to start the talk ! ")
    # obtain audio from the microphone
    r = sr.Recognizer()
    # reset mic
    with sr.Microphone() as source:
        print("Say something!")
        # audio = r.listen(source)
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source, timeout=1, phrase_time_limit=2)
    # speech to text now
    try:
        print("Sphinx thinks you said " + r.recognize_google(audio))
    except sr.UnknownValueError:
        print("Sphinx could not understand audio")
    except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))


if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("Error: need to specify model name")
        print("Usage: python demo.py your.model")
        sys.exit(-1)

    model = sys.argv[1]

    # capture SIGINT signal, e.g., Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
    print('Listening... Press Ctrl+C to exit')

    # start the thread of the detector
    detector.start(detected_callback=word_detected,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)

    detector.terminate()
