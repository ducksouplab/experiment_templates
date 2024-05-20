from dotenv import load_dotenv
from pprint import pprint
import os

# use .env file if exists
load_dotenv()

class Env:
  DUCKSOUP_URL = os.getenv("OTREE_DUCKSOUP_URL", "http://localhost:8000")
  DUCKSOUP_FRONTEND_VERSION = os.getenv("OTREE_DUCKSOUP_FRONTEND_VERSION", "latest")
  DUCKSOUP_REQUEST_GPU = os.getenv("OTREE_DUCKSOUP_REQUEST_GPU", 'False').lower() in ('true', '1', 't')
  DUCKSOUP_FRAMERATE = int(os.getenv("OTREE_DUCKSOUP_FRAMERATE", "30"))
  DUCKSOUP_WIDTH = int(os.getenv("OTREE_DUCKSOUP_WIDTH", "800"))
  DUCKSOUP_HEIGHT = int(os.getenv("DUCKSOUP_HEIGHT", "600"))
  DUCKSOUP_FORMAT = os.getenv("OTREE_DUCKSOUP_FORMAT", "H264")
  DUCKSOUP_JS_URL = DUCKSOUP_URL + "/assets/" + DUCKSOUP_FRONTEND_VERSION + "/js/ducksoup.js"

pprint("OTREE_PRODUCTION          " + os.getenv("OTREE_PRODUCTION", ""))
pprint("OTREE_AUTH_LEVEL          " + os.getenv("OTREE_AUTH_LEVEL", ""))
pprint("DUCKSOUP_URL              " + Env.DUCKSOUP_URL)
pprint("DUCKSOUP_FRONTEND_VERSION " + Env.DUCKSOUP_FRONTEND_VERSION)
pprint("DUCKSOUP_JS_URL           " + Env.DUCKSOUP_JS_URL)
pprint("DUCKSOUP_REQUEST_GPU      " + str(Env.DUCKSOUP_REQUEST_GPU))
pprint("DUCKSOUP_FRAMERATE        " + str(Env.DUCKSOUP_FRAMERATE))
pprint("DUCKSOUP_WIDTH            " + str(Env.DUCKSOUP_WIDTH))
pprint("DUCKSOUP_HEIGHT           " + str(Env.DUCKSOUP_HEIGHT))
pprint("DUCKSOUP_FORMAT           " + Env.DUCKSOUP_FORMAT)
