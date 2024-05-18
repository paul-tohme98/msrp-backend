import json
from flask import Flask, jsonify, request, send_file
from BackendMain import *
import os
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/")
def displayHello():
    return "Hello"


UPLOAD_FOLDER = './'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

listToProcess = []

@app.route('/api/download-sheet', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'success': 'File uploaded successfully', 'filename': filename})
    return jsonify({'error': 'Something went wrong'})


@app.route('/api/process-sheet', methods=['POST'])
def process_sheet():
    print("Processing...")
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        filename = file.filename
        listOutput = BackendMain.processSheet(filename)  # Pass the file name to the function
        
        print("LIST PROCESSED")
        print(listOutput)
        listToProcess = listOutput

        # Convert inner lists to tuples if they contain a single tuple
        for i, item in enumerate(listOutput):
            if isinstance(item, list) and len(item) == 1 and isinstance(item[0], tuple):
                listOutput[i] = item[0]

        # return jsonify({'success': 'File uploaded successfully', 'listOutput': listOutput})
        return listOutput
    return jsonify({'error': 'Something went wrong'})



def convert_to_tuples(lst):
    result = []
    
    for item in lst:
        if len(item) > 1 and isinstance(item[0], list):
            sub = []
            for inner in item:
                sub.append(tuple(inner))
            result.append(sub)
        else:
            result.append(tuple(item))
    
    return result


@app.route('/api/play-midi', methods=['POST'])
def play_midi():
    # Decode the bytes object into a string
    data_str = request.data.decode('utf-8')
    
    # Convert the string into a dictionary
    data_dict = json.loads(data_str)

    # print("Data dict")
    # print(data_dict)
    
    # Extract the 'output' field from the dictionary
    listOutput = data_dict.get('listOutput')
    
    # print("LIST PLAYED BEFORE")
    # print(listOutput)

    if not listOutput:
        return jsonify({'error': 'No output provided'})
    
    listOutput = convert_to_tuples(listOutput)
    # print("LIST PLAYED AFTER")
    # print(listOutput)

    BackendMain.playMidi(listOutput)
    # print("MIDI NAME")
    # print(midi_filename)
    # if midi_filename is None:
    #     return jsonify({'error': 'Failed to generate MIDI file'})

    return send_file("temp.mid", as_attachment=True, download_name='output.mid')




if __name__ == "__main__":
    app.run(debug=True)
