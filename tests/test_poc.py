from jinja2 import Environment
import urllib.request

import random

import socket

import sys
from time import sleep
import splunklib.results as results
import splunklib.client as client
from time import sleep



env = Environment(extensions=['jinja2_time.TimeExtension'])
word_url = "http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"
response = urllib.request.urlopen(word_url)
long_txt = response.read().decode()
words = long_txt.splitlines()

def sendsingle(message):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('sc4s', 514)

    sock.connect(server_address)
    sock.sendall(str.encode(message))

def splunk_single(search):
    service = client.connect(username="admin", password="Changed@11",host="splunk",port="8089")
    kwargs_normalsearch = {"exec_mode": "normal"}
    job = service.jobs.create(search, **kwargs_normalsearch)

    # A normal search returns the job's SID right away, so we need to poll for completion
    while True:
        while not job.is_ready():
            pass
        stats = {"isDone": job["isDone"],
                 "doneProgress": float(job["doneProgress"]) * 100,
                 "scanCount": int(job["scanCount"]),
                 "eventCount": int(job["eventCount"]),
                 "resultCount": int(job["resultCount"])}

        status = ("\r%(doneProgress)03.1f%%   %(scanCount)d scanned   "
                  "%(eventCount)d matched   %(resultCount)d results") % stats

        sys.stdout.write(status)
        sys.stdout.flush()
        if stats["isDone"] == "1":
            sys.stdout.write("\n\nDone!\n\n")
            break
        sleep(2)

    # Get the results and display them
    resultCount=stats["resultCount"]
    eventCount=stats["eventCount"]
    return resultCount,eventCount



def test_defaultroute():

    ##mark## ##date##T##time##.000z "##name## bluecoat[0]:SPLV5

    host = "{}-{}".format(random.choice(words),random.choice(words))


    t = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %}.000z {{ host }} sc4s_default[0]: test")
    message = t.render(mark="<111>1", host=host)

    sendsingle(message)

    sleep(15)

    search = 'search "{}" | head 10'.format(host)

    resultCount ,eventCount = splunk_single(search)
    assert resultCount == 1