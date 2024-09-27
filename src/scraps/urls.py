from flask import request

from ..app import app
from .controllers import *


@app.route("/scrap", methods=['GET'])
def startScrapingOfCustomeUrl():
        if request.method == "GET":
                return StartScrap(request.args['url'])
        else:
                return "Invalid request method"