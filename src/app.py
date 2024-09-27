import os


print("in it")
# App Initialization
from . import create_app # from __init__ file
app = create_app(os.getenv("CONFIG_MODE"))


# Applications Routes
from .accounts import urls
from .productions import urls
from .scraps import urls


# Hello World!
@app.route('/index')
def index():
    return "Hello World!"

if __name__ == "__main__":
    app.run()