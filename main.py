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
            
            duration_seconds = info.get('duration') or 0

            def approx_size_bytes_from_tbr(tbr_kbps, duration_s):
                if not tbr_kbps or not duration_s:
                    return None
                try:
                    return int(duration_s * tbr_kbps * 125)  # 1000/8 = 125 bytes per kbps per second
                except Exception:
                    return None

            for f in info['formats']:
                print(f"Processing format: {f.get('format_id')} - vcodec: {f.get('vcodec')} - acodec: {f.get('acodec')}")
                
                raw_filesize = f.get('filesize') or f.get('filesize_approx')
                if not raw_filesize:
                    raw_filesize = approx_size_bytes_from_tbr(f.get('tbr'), duration_seconds)

                format_info = {
                    'format_id': f['format_id'],
                    'ext': f['ext'],
                    'resolution': f.get('resolution', 'N/A'),
                    'filesize': raw_filesize,
                    'filesize_bytes': raw_filesize,
                    'vcodec': f.get('vcodec', 'N/A'),
                    'acodec': f.get('acodec', 'N/A'),
                    'format_note': f.get('format_note', ''),
                    'height': f.get('height', 0),
                    'fps': f.get('fps', 0),
                    'tbr': f.get('tbr', 0),
                    'abr': f.get('abr', 0),
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
            
            # Create a curated list of download options according to requirements:
            # - 1 best available video option
            # - up to 2 lower resolution video options
            # - 1 audio-only option
            final_video_formats = []

            def sort_key_with_preferences(fmt):
                return (
                    fmt.get('ext') == 'mp4',
                    fmt.get('height') or 0,
                    fmt.get('tbr') or 0
                )

            combined_sorted = sorted(combined_formats, key=sort_key_with_preferences, reverse=True)
            video_sorted = sorted(video_formats, key=sort_key_with_preferences, reverse=True)

            picked_heights = []  # Track unique heights picked, highest first

            def add_combined(fmt):
                item = fmt.copy()
                note = (item.get('format_note') or '').strip()
                item['format_note'] = f"{note + ' ' if note else ''}(Video+Audio)"
                final_video_formats.append(item)

            def add_merged(fmt):
                fmt_height = fmt.get('height') or 0
                item = fmt.copy()
                item['format_id'] = f"merged_{fmt['format_id']}"
                item['format_note'] = f"{fmt_height}p MP4 (Auto-merged with audio)" if fmt_height else "Auto-merged with audio"
                # Estimate merged filesize: video + best audio
                best_audio = None
                if audio_formats:
                    best_audio = max(audio_formats, key=lambda x: x.get('tbr') or 0)
                video_size = item.get('filesize_bytes') or approx_size_bytes_from_tbr(item.get('tbr'), duration_seconds)
                audio_size = None
                if best_audio:
                    audio_size = best_audio.get('filesize_bytes') or approx_size_bytes_from_tbr(best_audio.get('tbr') or best_audio.get('abr'), duration_seconds)
                if video_size and audio_size:
                    item['filesize_bytes'] = video_size + audio_size
                    item['filesize'] = item['filesize_bytes']
                final_video_formats.append(item)

            # Step 1: pick the best (highest) combined if available, else best video-only (merged)
            if combined_sorted:
                add_combined(combined_sorted[0])
                picked_heights.append(combined_sorted[0].get('height') or 0)
            elif video_sorted:
                add_merged(video_sorted[0])
                picked_heights.append(video_sorted[0].get('height') or 0)

            # Step 2: fill up to two lower resolution unique heights, preferring combined
            def fill_lower_res(candidates, adder):
                for fmt in candidates:
                    if len(final_video_formats) >= 3:
                        break
                    height_value = fmt.get('height') or 0
                    if not picked_heights:
                        continue
                    best_height = picked_heights[0]
                    if height_value < best_height and height_value not in picked_heights:
                        adder(fmt)
                        picked_heights.append(height_value)

            fill_lower_res(combined_sorted[1:], add_combined)
            if len(final_video_formats) < 3:
                fill_lower_res(video_sorted, add_merged)

            # If nothing could be selected, provide a single generic best option as a last resort
            if not final_video_formats:
                final_video_formats = [{
                    'format_id': 'best_mp4',
                    'ext': 'mp4',
                    'resolution': 'Best Available',
                    'filesize': 'N/A',
                    'format_note': 'Best Quality (Auto)',
                    'height': 0,
                    'tbr': 0
                }]

            # Build audio-only list: provide a single best quality audio option (mp3 extraction)
            filtered_audio_formats = []
            if audio_formats or combined_formats:
                # Choose best audio candidate to estimate size
                best_audio_src = None
                if audio_formats:
                    best_audio_src = max(audio_formats, key=lambda x: x.get('tbr') or 0)
                est_size = None
                if best_audio_src:
                    est_size = best_audio_src.get('filesize_bytes') or approx_size_bytes_from_tbr(best_audio_src.get('tbr') or best_audio_src.get('abr'), duration_seconds)
                filtered_audio_formats.append({
                    'format_id': 'audio_only',
                    'ext': 'mp3',
                    'resolution': 'Audio Only',
                    'filesize': est_size,
                    'filesize_bytes': est_size,
                    'format_note': 'Best Quality Audio (MP3)',
                    'acodec': 'mp3',
                    'tbr': best_audio_src.get('tbr') if best_audio_src else 0
                })
            
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