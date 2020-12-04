import os
from datetime import datetime

EXEC_TIME = datetime.now().strftime("%Y%m%d%H%M%S")
OUTPUT_FOLDER = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "..", "output", EXEC_TIME)
LOG_FILE = os.path.join(OUTPUT_FOLDER, "log" + ".txt")


def ensureFolderExists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def log(text= "", echoToConsole=False, end='\n', filename=LOG_FILE):
    text = str(text)
    if not filename:
        raise RuntimeError("No log file set")

    ensureFolderExists(os.path.dirname(filename))
    with open(filename, "a+") as f:
        f.write(text + end)

    if echoToConsole:
        print(text, end=end)

def sbResultFolder(sb):
    return os.path.join(OUTPUT_FOLDER, sb.name)

def logHeader(text : str, level=0, echoToConsole=False, filename=LOG_FILE):
    linelength = 80
    text = " " + text + " "
    fillLength = linelength - len(text)
    ch = '-' if level == 1 else '='
    def fill(): return ch * int(fillLength/2)
    text = fill() + text + fill()
    text = text if len(text) == 80 else text + ch
    log(text, echoToConsole, filename = filename)

def logResult(sbName, resultName, text= "", echoToConsole=False, end='\n'):
    log(text=text, echoToConsole=echoToConsole, end=end,
        filename=os.path.join(OUTPUT_FOLDER, sbName, resultName + ".txt"))

def logResultHeader(sbName, resultName, text= "", level=0, echoToConsole=False):
    logHeader(text=text, level=level, echoToConsole=echoToConsole,
        filename=os.path.join(OUTPUT_FOLDER, sbName, resultName + ".txt"))
