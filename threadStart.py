#Ne change rien pour l'instant, va permettre de stopper les threads sur demande

import threading

def tStart(thread):
    thread.setDaemon(True)
    try:
        thread.start()
    except KeyboardInterrupt:
        thread.do_run = False
        raise