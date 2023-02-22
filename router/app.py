import pathlib

from flask import Flask, request, redirect, abort
from datetime import datetime
import string
import json

app = Flask(__name__)

srcdir = pathlib.Path(__file__).parent
top_srcdir = srcdir / ".."

# load the current version of the mapping cache
with (top_srcdir / 'iri_mappings_to_html.json').open('r') as fp:
    mappings = json.load(fp)

@app.route("/")
def root():
    '''Routes the root '/' of the host to the index of the docs'''

    # redirect when we find a match based on SSL
    if request.is_secure:
        return redirect(f'https://{request.host}/case/documentation/index.html', 301)
    else:
        return redirect(f'http://{request.host}/case/documentation/index.html', 301)

@app.route("/<ontology>/<path:target>", methods=['GET'])
def router(ontology: str, target: str):
    '''Routes data through the file system to the appropriate documentation'''

    # redirect when we find a match based on SSL
    if f"{ontology}/{target}" in mappings:
        location = mappings[f"{ontology}/{target}"]
        if request.is_secure:
            return redirect(f'https://{request.host}/{location}', 301)
        else:
            return redirect(f'http://{request.host}/{location}', 301)
    else:
        abort(401)
