import sys
import time

import requests as r
import threading
from bs4 import BeautifulSoup

mutex = threading.Lock()
usedUrls = []


def get(url):
    c = None
    try:
        c = r.get(url).text
    except:
        print("Unable to reach {0}".format(url))
    return c


def addUrl(url):
    global usedUrls

    usedUrls.append(url)


def inUrlsList(url):
    global usedUrls
    return url in usedUrls


def getUrl(url, nest, maxnest, verb):
    if nest >= maxnest:
        return

    c = get(url)
    if not c:
        return

    soup = BeautifulSoup(c, "html.parser")
    for e in soup.find_all("a", href=True):
        newUrl = e['href']
        try:
            if newUrl[0] == '/':
                newUrl = url + newUrl[1:]
            if newUrl[0] == '.':
                newUrl = url + newUrl
        except:
            continue

        if newUrl[0] == '#':
            continue

        if not inUrlsList(newUrl):

            global mutex
            mutex.acquire()
            addUrl(newUrl)
            mutex.release()

            if verb:
                print("Searching on: {0}, Nested: {1}".format(newUrl, nest + 1))
            getUrl(newUrl, nest + 1, maxnest, verb)

    return


def main(e, nest, maxnest, verbose):
    getUrl(e, nest, maxnest, verbose)


def threads(e, nest, maxnest, verbose):
    x = threading.Thread(target=main, args=(e, nest, maxnest, verbose), name=e)
    return x


def setOptions(arguments: list):
    fi = None
    mThreads = None
    mNest = None
    verb = False

    for i in range(1, len(arguments)):
        match arguments[i]:
            case '-f':
                fi = arguments[i + 1]
            case '-t':
                mThreads = arguments[i + 1]
            case '-n':
                mNest = arguments[i + 1]
            case '-v':
                verb = True
            case '-h':
                help()
            case '--help':
                help()
            case _:
                continue

    if not fi:
        print("A file with a list of urls is required")
        exit()
    if not mThreads:
        mThreads = 3
    if not mNest:
        mNest = 2

    print("\t\tSetting maximum threads to {0}".format(mThreads))
    print("\t\tSetting maximum nesting to {0}".format(mNest))

    return fi, int(mNest), int(mThreads), verb


def startThread(thread):
    print("Starting thread:", thread.name)
    thread.start()


def scheduleThreads(threadList: list):
    i = 0
    while i < len(threadList):
        time.sleep(5)
        numExecThrds = len(execThreads)
        if numExecThrds == maxThreads:
            for t in execThreads:
                if not t.is_alive():
                    execThreads.remove(t)
        if numExecThrds < maxThreads:
            startThread(threadList[i])
            execThreads.append(threadList[i])
            i += 1

    for t in execThreads:
        t.join()

    return


def help():
    print("\n\tUsage:\n\t\t", sys.argv[0], "-f <URL File> [OPTIONS]")
    print("\tOPTIONS:", "-f <URL FIle> Path to url file to process", "-v Activates verbose mode",
          "-t Maximum number of threads, one per main URL", "-n Maximum nesting", "-h/--help Shows this menu",
          sep="\n\t\t")
    exit()


if __name__ == '__main__':

    thrds = []
    execThreads = []
    fileName, maxNest, maxThreads, verbose = setOptions(sys.argv)

    start = time.time()
    try:
        f = open(fileName, "r")
        content = f.readlines()
        f.close()
    except:
        print("Unable to open URL File")
        exit()


    for elem in content:
        if not elem[-1] == '/':
            elem = elem + '/'
        thrds.append(threads(elem.strip('\n'), 0, maxNest, verbose))

    scheduleThreads(thrds)

    end = time.time()

    print("time taken: ", end - start)

    usedUrls.sort(reverse=True)
    print(len(usedUrls), usedUrls)
