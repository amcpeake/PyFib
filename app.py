# encoding=utf8
from flask import Flask, request, render_template, jsonify, safe_join, make_response
import os
import base64
import magic
from datetime import datetime, timedelta

app = Flask(__name__)
ROOTPATH = os.path.join('/', 'media', 'Samba')  # CONST


def sizeof_fmt(num): # Convert number of bytes to human readable
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
        if abs(num) < 1000.0:
            return f"{num} {unit}"
        num /= 1000.0
    return f"{num} YB"


@app.route('/files', methods=['GET', 'POST'])   # BlUE File Browser
def files():

    try:    # Get request parameters
        relpath = request.json['path']
        reqtype = request.json['type']
    except TypeError:   # Or, if not found use defaults
        relpath = ''
        reqtype = 'get'

    path = safe_join(ROOTPATH, relpath)     # Append user-provided path to the rootfolder
    if reqtype == 'get':    # Returns a dict of item: {type:}
        items = {}
        if os.path.isdir(path):     # If given path is a folder
            for item in os.listdir(path):   # Get all items in folder, determine type and append to dict
                itempath = os.path.join(path, item)
                size = sum(os.path.getsize(os.path.join(dirpath,filename)) for dirpath, dirnames, filenames in os.walk(itempath) for filename in filenames )
                time = datetime.utcfromtimestamp(os.path.getmtime(itempath)) - timedelta(hours=5)
                if os.path.isdir(itempath):
                    items.update({
                        item: {
                            'type': 'folder',
                            'info': {
                                'size': sizeof_fmt(size),
                                'mod': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'path': itempath,
                            }
                        }
                    })
                if os.path.isfile(itempath):
                    items.update({
                        item: {
                            'type': 'file',
                            'info': {
                                'size': sizeof_fmt(os.path.getsize(itempath)),
                                'mod': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'path': itempath,
                                'filetype': magic.from_file(itempath, mime=True)
                            }
                        }
                    })

        if os.path.isfile(path):    # If given path is a file
            file = open(path, 'rb')
            items = {'type': magic.from_file(path, mime=True), 'name': os.path.basename(path), 'content': str(base64.b64encode(file.read()))}
        if request.method == 'GET':     # Render template and pass initial item dict
            return render_template('index.html', items=items)

        elif request.method == 'POST':  # Return requested item dict
            return jsonify(items)

    elif reqtype == 'delete':   # Moves a file to trash and returns confirmation
        return jsonify({'error': 'none'})

    elif reqtype == 'create':   # Creates a file and returns confirmation
        return jsonify({'error': 'none'})

    elif reqtype == 'search':   # Returns a dict of items matching the search
        return jsonify({'error': 'none'})

    elif reqtype == 'move':
        return jsonify({'error': 'none'})

    else:   # Uncaught error
        return jsonify({'Error': 'Malformed Request'})


if __name__ == '__main__':
    app.run()
