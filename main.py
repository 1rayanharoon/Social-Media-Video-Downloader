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
    try:
        print(f"Starting download - URL: {url}, Format: {format_id}, Task: {task_id}")
        
        # Enhanced download options for better compatibility
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIRECTORY, f'{task_id}.%(ext)s'),
            'nocheckcertificate': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': False,
        }
        
        # Handle different format types
        if format_id == 'best_mp4':
            # Download best quality MP4 with both video and audio
            ydl_opts['format'] = 'best[ext=mp4]/best[height<=1080]/best'
        elif format_id == 'audio_only':
            # Download best audio only
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['extractaudio'] = True
            ydl_opts['audioformat'] = 'mp3'
        elif format_id.startswith('merged_'):
            # Handle merged video+audio formats for better compatibility
            actual_format = format_id.replace('merged_', '')
            ydl_opts['format'] = f'{actual_format}+bestaudio/best[height<=1080]/best'
        else:
            # Use specified format but try to ensure it has audio
            ydl_opts['format'] = f'{format_id}+bestaudio/{format_id}/best'

        print(f"Using yt-dlp options: {ydl_opts}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
        print(f"Download completed: {filename}")
        return os.path.basename(filename)
        
    except Exception as e:
        print(f"Error in download_video: {str(e)}")
        raise e

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_video_info():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    ydl_opts = {
        'format': 'best',
        'quiet': False,
        'no_warnings': False,
        'extractaudio': False,
        'audioformat': 'mp3',
        'embed_subs': True,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'nocheckcertificate': True,  # Fix SSL certificate issues
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"Attempting to extract info for URL: {url}")
            info = ydl.extract_info(url, download=False)
            
            print(f"Total formats found: {len(info.get('formats', []))}")
            
            # Separate video and audio formats
            video_formats = []
            audio_formats = []
            combined_formats = []  # Formats with both video and audio
            
            for f in info['formats']:
                print(f"Processing format: {f.get('format_id')} - vcodec: {f.get('vcodec')} - acodec: {f.get('acodec')}")
                
                format_info = {
                    'format_id': f['format_id'],
                    'ext': f['ext'],
                    'resolution': f.get('resolution', 'N/A'),
                    'filesize': f.get('filesize', 'N/A'),
                    'vcodec': f.get('vcodec', 'N/A'),
                    'acodec': f.get('acodec', 'N/A'),
                    'format_note': f.get('format_note', ''),
                    'height': f.get('height', 0),
                    'fps': f.get('fps', 0),
                    'tbr': f.get('tbr', 0),
                }
                
                # Combined formats (has both video and audio) - these are most compatible
                if (f.get('vcodec') and f.get('vcodec') != 'none' and 
                    f.get('acodec') and f.get('acodec') != 'none'):
                    combined_formats.append(format_info)
                    print(f"Added to combined formats: {f['format_id']}")
                # Video-only formats
                elif f.get('vcodec') and f.get('vcodec') != 'none':
                    video_formats.append(format_info)
                    print(f"Added to video formats: {f['format_id']}")
                # Audio-only formats
                elif f.get('acodec') and f.get('acodec') != 'none':
                    audio_formats.append(format_info)
                    print(f"Added to audio formats: {f['format_id']}")
            
            # Create a curated list of download options
            final_video_formats = []
            
            # First, add the best combined formats (video+audio in one file)
            if combined_formats:
                # Sort by quality and prefer MP4
                combined_formats.sort(key=lambda x: (
                    x['ext'] == 'mp4',
                    x['height'],
                    x['tbr'] or 0
                ), reverse=True)
                
                # Add top 3 combined formats
                for fmt in combined_formats[:3]:
                    fmt['format_note'] = f"{fmt['format_note']} (Video+Audio)".strip()
                    final_video_formats.append(fmt)
            
            # Add a "Best Quality MP4" option
            final_video_formats.insert(0, {
                'format_id': 'best_mp4',
                'ext': 'mp4',
                'resolution': 'Best Available',
                'filesize': 'N/A',
                'format_note': 'Best Quality MP4 (Recommended)',
                'height': 9999,  # For sorting
                'tbr': 9999
            })
            
            # Add some merged format options for better quality
            popular_heights = [720, 1080, 480, 360]
            for height in popular_heights:
                height_formats = [f for f in video_formats if f['height'] == height and f['ext'] == 'mp4']
                if height_formats:
                    best_format = max(height_formats, key=lambda x: x['tbr'] or 0)
                    merged_format = best_format.copy()
                    merged_format['format_id'] = f"merged_{best_format['format_id']}"
                    merged_format['format_note'] = f"{height}p MP4 (Auto-merged with audio)"
                    final_video_formats.append(merged_format)
                    break  # Only add one merged option
            
            # Filter audio formats - keep only the best quality ones
            filtered_audio_formats = []
            
            # Add a simple "Audio Only" option
            if audio_formats:
                filtered_audio_formats.append({
                    'format_id': 'audio_only',
                    'ext': 'mp3',
                    'resolution': 'Audio Only',
                    'filesize': 'N/A',
                    'format_note': 'Best Quality Audio (MP3)',
                    'acodec': 'mp3',
                    'tbr': 9999
                })
            
            # Sort by bitrate descending and add top 2 original audio formats
            audio_formats.sort(key=lambda x: x['tbr'] or 0, reverse=True)
            for f in audio_formats[:2]:
                if f not in filtered_audio_formats:
                    filtered_audio_formats.append(f)
            
            # Limit final results
            final_video_formats = final_video_formats[:6]
            filtered_audio_formats = filtered_audio_formats[:3]
            
            # If no formats found, add fallback options
            if not final_video_formats and not filtered_audio_formats:
                print("No formats found with primary filtering, adding fallback options")
                # Add a basic best format option
                final_video_formats = [{
                    'format_id': 'best_mp4',
                    'ext': 'mp4',
                    'resolution': 'Best Available',
                    'filesize': 'N/A',
                    'format_note': 'Best Quality (Fallback)',
                    'height': 999,
                    'tbr': 999
                }]
            
            print(f"Final counts - Video formats: {len(final_video_formats)}, Audio formats: {len(filtered_audio_formats)}")
            
            return jsonify({
                'title': info['title'],
                'thumbnail': info.get('thumbnail'),
                'video_formats': final_video_formats,
                'audio_formats': filtered_audio_formats,
                'duration': info.get('duration', 'N/A'),
                'uploader': info.get('uploader', 'N/A'),
            })
        except Exception as e:
            error_msg = str(e)
            print(f"Error extracting info: {error_msg}")
            
            # Provide more helpful error messages
            if "Failed to extract any player response" in error_msg:
                error_msg = "This video cannot be processed. It might be private, deleted, or have restrictions. Please try a different video."
            elif "Video unavailable" in error_msg:
                error_msg = "This video is unavailable. It might be private, deleted, or restricted in your region."
            elif "Sign in to confirm your age" in error_msg:
                error_msg = "This video has age restrictions that prevent automatic downloading."
            
            return jsonify({"error": error_msg}), 500

@app.route('/api/download', methods=['POST'])
def start_download():
    try:
        data = request.json
        url = data.get('url')
        format_id = data.get('format_id')

        print(f"Download request - URL: {url}, Format: {format_id}")

        if not url or not format_id:
            return jsonify({"error": "URL and format_id are required"}), 400

        task_id = str(uuid.uuid4())
        download_status[task_id] = {'status': 'in_progress'}
        download_queue.put((url, format_id, task_id))

        print(f"Download task created: {task_id}")

        return jsonify({
            "task_id": task_id,
            "message": "Download started"
        })
    except Exception as e:
        print(f"Error in start_download: {str(e)}")
        return jsonify({"error": f"Failed to start download: {str(e)}"}), 500

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
    try:
        # Use environment port for deployment, fallback to 5000 for local
        port = int(os.environ.get('PORT', 5001))
        app.run(debug=False, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print('Shutting down...')
        download_queue.put(None)  # Signal worker to exit
        download_thread.join()