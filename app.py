from flask import Flask, Blueprint, render_template_string, render_template, send_file, request, current_app, jsonify, redirect, session, url_for, send_from_directory
from utils import allowed_file, is_pdf_size_valid, cleanup_temp_pdfs
from flask_caching import Cache
from flask_cors import CORS, cross_origin
from apscheduler.schedulers.background import BackgroundScheduler
import tempfile
import os
import subprocess
import base64
import fitz
import logging
import json


app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True) 
app.logger.setLevel(logging.DEBUG)  
# ustawienia sesji

custom_temp_dir = "static/temporaries"
if not os.path.exists(custom_temp_dir):
    os.makedirs(custom_temp_dir)

pdf_blueprint = Blueprint('pdf_blueprint', __name__)

@pdf_blueprint.route('/upload-pdf', methods=['POST'])

def upload_pdf():
    """
        Funkcja obsługująca wczyttwanie pliku PDF, sprawdza rozmiar i format oraz umozliwia tymczasowy zapis.
    """
    try:
        print(request.method)
        print("Inside upload_pdf route")
        print(request.files)  # Log the content of the files received
        print(request.data)  # Print raw request data
        print(request.form)  # Print form data

        if request.method == 'POST':
            if 'file' in request.files:
                file = request.files['file']
                
                print(f"Filename1: {file.filename}")  # Log filename
                print(f"File size1: {len(file.read())}")  # Log file size

                if file.filename == '':
                    return jsonify({"error": "Nie wybrano żadnego pliku"}), 400
                
                if not allowed_file(file.filename):
                    os.remove(file.filename)
                    return jsonify({"error": "Nieprawidlowy format pliku"}), 400
                
                try:
                    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=custom_temp_dir)
                    file.seek(0)  # Reset file pointer for reading
                    temp_pdf.write(file.read())
                    # DIP>>>
                    app.logger.info(f"Uploaded PDF saved to {temp_pdf.name}")
                    # DIP<<<
                    file.seek(0)
                    print('Temp file created[/upload-pdf]:', temp_pdf.name)
                    print('File exists[/upload-pdf], Size:', os.path.getsize(temp_pdf.name))
                    print('File contents[/uplaod-pdf] (first 300 bytes):', file.read(300))
                    print('[/upload-pdf] pdf_path before setPdfPath(temp_pdf.name):', temp_pdf.name)

                    initial_bytes = temp_pdf.read(300)
                    print("PDF Path(/upload-pdf -> temp_pdf.name):", temp_pdf.name)  # Verify the temporary file path

                    temp_pdf.close()
                    pdf_path = temp_pdf.name
                    print("Full absolute path of temp file:", os.path.abspath(temp_pdf.name))
                    
                    print("pdf_path in upload_pdf route: %s", pdf_path)
                    # PID:>>>
                    pdf_url = url_for('get_pdf', filename=os.path.basename(temp_pdf.name), _external=True)
                    print(f"PDF Path (URL): {pdf_url}")
                    # PID:<<<
                except Exception as e:
                    logging.exception("Unexpected error during file handling:", e)
                    os.remove(pdf_path)
                    return jsonify({"error": f"Błąd przetwarzania pliku: {str(e)}"}), 500
            else:
                print("No file found in the request")
                os.remove(pdf_path)
                return jsonify({"error": "Brak części plikowej"}), 400

        # return jsonify({"pdf_path": pdf_path})
        return jsonify({
            'pdf_url': pdf_url,
            'pdf_path': pdf_path # Send just a filename.
        })
    except Exception as e:
        os.remove(pdf_path)
        logging.exception("Error during upload:", e)
        return jsonify({"error": "Internal server error"}), 500
        
# PID:>>>
@app.route('/static/temporaries/<filename>', methods=['GET'])
def get_pdf(filename):
    return send_from_directory(custom_temp_dir, filename)
# PID:<<<

@pdf_blueprint.route('/upload-pdf', methods=['GET'])
def redirect_from_get():
    """
        Funkcja wywolywana na bledny path podany - redirect
    """
    return redirect('/')

@pdf_blueprint.route('/validate-pdf', methods=['POST'])
@cross_origin()
def validate_pdf():
    """
        Funkcja odpowiadająca za walidację wczytanego pliku i stwierdzenie jego istnienia, oraz obsługi w aplikacji.
    """
    print(request.method)
    print("Inside validate-pdf route")
    print(request.files)  # Log the content of the files received
    print(request.data)  # Print raw request data
    print(request.form)  # Print form data

    if 'pdf_path' not in request.files:
        return jsonify({"error": "No path /w pdf provided for validation"}), 400
    
    pdf_file = request.files['pdf_path']

    temp_file = tempfile.NamedTemporaryFile(delete=False, dir=custom_temp_dir, suffix='.pdf')
    pdf_file.save(temp_file.name)
    pdf_path = temp_file.name
    print("The pdf_path is [validate-block]:", pdf_path)

    try: 
        if not is_pdf_size_valid(pdf_path):
            logging.error("File is empty or corrupt:", pdf_path)
            os.remove(pdf_path)
            return jsonify({"error": "PDF size exceeds limit[validate-block]"}), 413
    except FileNotFoundError:
        logging.error("File not found:", pdf_path)
        os.remove(pdf_path)
        return jsonify({"error": "PDF not Found[validate-block]"}), 404
    except Exception as e:
        logging.exception("Unexpected error during validation:", e)
        os.remove(pdf_path)
        return jsonify({"error": "Internal server error[validate-block]"}),
    os.remove(pdf_path)
    print("wypisz pliki w [validate-pdf]:", request.files)  # Log the content of the files received
    return jsonify({"isValid": True})


@pdf_blueprint.route('/workfile/<path:pdf_path>')
def get_pdf(pdf_path):
    """
        Obsługa pliku dostępna tylko po stronie serwera.
    """
    if cache.get(pdf_path):
        return send_file(pdf_path, as_attachment=False)
    else:
        return jsonify({"error": "Nie znaleziono pliku PDF"}), 404

       
@pdf_blueprint.route('/convert-pdf', methods=['POST'])
def convert_pdf():
    """
        Funkcja odpowiadająca za konwersję pliku na gcode z wykorzystaniem procesu fontforge.
    """
    print(request.method)
    print("Inside convert-pdf route")
    print(request.files)  # Log the content of the files received
    print(request.data)  # Print raw request data
    print(request.form)  # Print form data
    # DIP:>>>
    # file_path = request.form.get('pdf_path')
    # drill_angle = request.form.get('drill_angle')
    # drill_active_height = request.form.get('drill_active_height')
    # drill_movement_speed = request.form.get('drill_movement_speed')
     # Parse incoming JSON payload
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload received"}), 400
    
    # Extract parameters
    file_path = data.get("pdf_path")  # Relative path from /static/temporaries
    drill_angle = data.get("drill_angle")
    drill_active_height = data.get("drill_active_height")
    drill_movement_speed = data.get("drill_movement_speed")
    # DIP:<<<
    print("filepath to print", file_path)
    if not file_path:
        return jsonify({"error": "File path not received in request"}), 400
    if not os.path.exists(file_path):
        return jsonify({"error": "File does not exist at the provided path"}), 400

    original_dir = os.getcwd()
    print("original dir pa tera:", original_dir)
    try:
        print("file_path przed procesesm", file_path)
        subprocess.check_call([
            'fontforge', '-script', 'font_extractor/font_extractor.py', f'"{file_path}"', 
         drill_angle, drill_active_height, drill_movement_speed
    ])
        with open('output.gcode', 'r') as f:
            gcode_content = f.read()

        return gcode_content, 200, {
            'Content-Type': 'text/plain',  # Or another appropriate MIME type 
            'Content-Disposition': 'attachment; filename=output.gcode'
        }
    except subprocess.CalledProcessError as e:
        logging.error("Failed to convert PDF to SVG: %s", e)
        return jsonify({"error": "Failed to convert PDF to SVG"}), 500
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        cleanup_files = ['fonts.json', 'pdf_text.json', 'output.gcode']
        for file_to_delete in cleanup_files:
            if os.path.exists(file_to_delete):
                os.remove(file_to_delete) 
        
        for fontfilename in os.listdir():
            if fontfilename.endswith('.svg'):
                os.remove(fontfilename)

@pdf_blueprint.route('/fetch-pdf-url', methods=['POST'])
def fetch_pdf_url():
    """Fetch a PDF file from an external HTTP URL and save it temporarily."""
    try:
        data = request.get_json()
        url = data.get('url')
        if not url or not url.endswith('.pdf'):
            return jsonify({"error": "Invalid PDF URL"}), 400
        
        response = request.get(url, stream=True)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch PDF"}), 400
        
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=custom_temp_dir)
        for chunk in response.iter_content(chunk_size=1024):
            temp_pdf.write(chunk)
        temp_pdf.close()
        
        app.logger.info(f"PDF fetched from {url} saved to {temp_pdf.name}")
        return jsonify({"pdf_path": temp_pdf.name})
    except Exception as e:
        logging.exception("Error fetching PDF from URL")
        return jsonify({"error": str(e)}), 500


cache = Cache(app)
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 1200
app.config['CORS_HEADERS'] = 'Content-Type'
app.register_blueprint(pdf_blueprint, url_prefix='/pdf')

scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_temp_pdfs, 'interval', minutes=4)
scheduler.start()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 
