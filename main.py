from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import yt_dlp
import os
import uuid
from threading import Thread
from queue import Queue

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIRECTORY = "downloads"
if not os.path.exists(DOWNLOAD_DIRECTORY):
    os.makedirs(DOWNLOAD_DIRECTORY)

download_queue = Queue()
download_status = {}

def worker():
    while True:
        task = download_queue.get()
        if task is None:
            break
        url, format_id, task_id = task
        try:
            filename = download_video(url, format_id, task_id)
            download_status[task_id] = {'status': 'complete', 'filename': filename}
        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")
            download_status[task_id] = {'status': 'error', 'error': str(e)}
        finally:
            download_queue.task_done()

def download_video(url, format_id, task_id):
    ydl_opts = {
        'format': format_id,
        'outtmpl': os.path.join(DOWNLOAD_DIRECTORY, f'{task_id}.%(ext)s'),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return os.path.basename(filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_video_info():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    ydl_opts = {'format': 'best'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = [
                {
                    'format_id': f['format_id'],
                    'ext': f['ext'],
                    'resolution': f.get('resolution', 'N/A'),
                    'filesize': f.get('filesize', 'N/A'),
                    'vcodec': f.get('vcodec', 'N/A'),
                    'acodec': f.get('acodec', 'N/A'),
                }
                for f in info['formats'] if f.get('vcodec') != 'none' and f.get('acodec') != 'none'
            ]
            return jsonify({
                'title': info['title'],
                'thumbnail': info.get('thumbnail'),
                'formats': formats
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/download', methods=['POST'])
def start_download():
    data = request.json
    url = data.get('url')
    format_id = data.get('format_id')

    if not url or not format_id:
        return jsonify({"error": "URL and format_id are required"}), 400

    task_id = str(uuid.uuid4())
    download_status[task_id] = {'status': 'in_progress'}
    download_queue.put((url, format_id, task_id))

    return jsonify({
        "task_id": task_id,
        "message": "Download started"
    })

@app.route('/api/status/<task_id>')
def check_status(task_id):
    status = download_status.get(task_id, {'status': 'not_found'})
    if status['status'] == 'complete':
        return jsonify({
            "status": "complete",
            "download_url": f"/download/{status['filename']}"
        })
    elif status['status'] == 'error':
        return jsonify({
            "status": "error",
            "error": status['error']
        })
    else:
        return jsonify({"status": status['status']})

@app.route('/download/<filename>')
def serve_file(filename):
    file_path = os.path.join(DOWNLOAD_DIRECTORY, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    download_thread = Thread(target=worker)
    download_thread.daemon = True
    download_thread.start()
    app.run(debug=True)