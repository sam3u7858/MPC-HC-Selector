from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import os
import uuid
import datetime
import glob
import threading
import time
from pathlib import Path

# Import the VideoClipper from the parent directory
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
try:
    from api import VideoClipper
except ImportError:
    # Fallback for development
    class VideoClipper:
        @staticmethod
        def go(json_file, output_dir, callback=None):
            # Mock implementation for development
            print(f"Mock clipping: {json_file} -> {output_dir}")
            if callback:
                callback(["mock_clip1.mp4", "mock_clip2.mp4"])
            return ["mock_clip1.mp4", "mock_clip2.mp4"]

app = Flask(__name__)
CORS(app)

# Configuration
MPC_HC_INFO_URL = "http://127.0.0.1:13579/info.html"
MPC_HC_VARIABLES_URL = "http://127.0.0.1:13579/variables.html"
AUTO_SAVE_DIR = "./auto-save"

# Global variables
session_data = {}

class ClipSession:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.clips = []
        self.created_at = datetime.datetime.now()
        self.last_modified = datetime.datetime.now()
        
    def add_clip(self, clip_data):
        self.clips.append(clip_data)
        self.last_modified = datetime.datetime.now()
        
    def remove_clip(self, index):
        if 0 <= index < len(self.clips):
            self.clips.pop(index)
            self.last_modified = datetime.datetime.now()
            return True
        return False
        
    def update_clip(self, index, clip_data):
        if 0 <= index < len(self.clips):
            self.clips[index] = clip_data
            self.last_modified = datetime.datetime.now()
            return True
        return False
        
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'clips': self.clips,
            'created_at': self.created_at.isoformat(),
            'last_modified': self.last_modified.isoformat()
        }

def create_auto_save_dir():
    """Create auto-save directory if it doesn't exist"""
    if not os.path.exists(AUTO_SAVE_DIR):
        os.makedirs(AUTO_SAVE_DIR)

def cleanup_old_auto_saves():
    """Remove auto-save files older than 5 days"""
    try:
        create_auto_save_dir()
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=5)
        
        for file_path in glob.glob(os.path.join(AUTO_SAVE_DIR, "*.json")):
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time < cutoff_date:
                os.remove(file_path)
                print(f"Removed old auto-save file: {file_path}")
    except Exception as e:
        print(f"Error cleaning up old auto-saves: {e}")

def auto_save_session(session):
    """Auto-save session to file"""
    try:
        create_auto_save_dir()
        if session.clips:  # Only save if there are clips
            auto_save_file = os.path.join(AUTO_SAVE_DIR, f"{session.session_id}.json")
            with open(auto_save_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error during auto-save: {e}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Flask backend is running',
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/api/session/new', methods=['POST'])
def create_new_session():
    """Create a new clip session"""
    session = ClipSession()
    session_data[session.session_id] = session
    
    return jsonify({
        'success': True,
        'session_id': session.session_id,
        'message': '新會話已創建'
    })

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session data"""
    if session_id not in session_data:
        return jsonify({
            'success': False,
            'error': '會話不存在'
        }), 404
        
    session = session_data[session_id]
    return jsonify({
        'success': True,
        'data': session.to_dict()
    })

@app.route('/api/mpc/timestamp', methods=['GET'])
def get_mpc_timestamp():
    """Get current timestamp from MPC-HC"""
    try:
        response = requests.get(MPC_HC_INFO_URL, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            info_text = soup.find(id='mpchc_np').get_text()
            parts = info_text.strip('«»').split('•')
            
            if len(parts) >= 3:
                file_name = parts[1].strip()
                current_position = parts[2].split('/')[0].strip()
                
                return jsonify({
                    'success': True,
                    'data': {
                        'file_name': file_name,
                        'current_position': current_position,
                        'timestamp': datetime.datetime.now().isoformat()
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '無法解析 MPC-HC 回應'
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': f'MPC-HC 回應錯誤: HTTP {response.status_code}'
            }), 400
            
    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'無法連接到 MPC-HC: {str(e)}'
        }), 500

@app.route('/api/mpc/filepath', methods=['GET'])
def get_mpc_filepath():
    """Get current file path from MPC-HC"""
    try:
        response = requests.get(MPC_HC_VARIABLES_URL, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            file_path_element = soup.find(id='filepath')
            
            if file_path_element:
                file_path = file_path_element.text
                # Convert encoding
                decoded_str = file_path.encode('latin1').decode('utf-8')
                
                return jsonify({
                    'success': True,
                    'data': {
                        'file_path': decoded_str,
                        'timestamp': datetime.datetime.now().isoformat()
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '無法找到檔案路徑元素'
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': f'MPC-HC 回應錯誤: HTTP {response.status_code}'
            }), 400
            
    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'無法連接到 MPC-HC: {str(e)}'
        }), 500

@app.route('/api/clips/<session_id>', methods=['POST'])
def add_clip(session_id):
    """Add a new clip to session"""
    if session_id not in session_data:
        return jsonify({
            'success': False,
            'error': '會話不存在'
        }), 404
        
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': '無效的請求資料'
        }), 400
        
    required_fields = ['start_time', 'end_time', 'custom_name']
    if not all(field in data for field in required_fields):
        return jsonify({
            'success': False,
            'error': '缺少必要欄位'
        }), 400
        
    session = session_data[session_id]
    
    # Get file path from MPC-HC
    try:
        file_path_response = get_mpc_filepath()
        file_path_data = file_path_response.get_json()
        
        if file_path_data['success']:
            file_path = file_path_data['data']['file_path']
        else:
            file_path = None
    except:
        file_path = None
    
    clip_data = {
        'start_time': data['start_time'],
        'end_time': data['end_time'],
        'custom_name': data['custom_name'],
        'path': file_path,
        'created_at': datetime.datetime.now().isoformat()
    }
    
    session.add_clip(clip_data)
    auto_save_session(session)
    
    return jsonify({
        'success': True,
        'data': clip_data,
        'message': '片段已新增'
    })

@app.route('/api/clips/<session_id>/<int:clip_index>', methods=['PUT'])
def update_clip(session_id, clip_index):
    """Update a clip in session"""
    if session_id not in session_data:
        return jsonify({
            'success': False,
            'error': '會話不存在'
        }), 404
        
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': '無效的請求資料'
        }), 400
        
    session = session_data[session_id]
    
    if session.update_clip(clip_index, data):
        auto_save_session(session)
        return jsonify({
            'success': True,
            'message': '片段已更新'
        })
    else:
        return jsonify({
            'success': False,
            'error': '片段索引無效'
        }), 400

@app.route('/api/clips/<session_id>/<int:clip_index>', methods=['DELETE'])
def remove_clip(session_id, clip_index):
    """Remove a clip from session"""
    if session_id not in session_data:
        return jsonify({
            'success': False,
            'error': '會話不存在'
        }), 404
        
    session = session_data[session_id]
    
    if session.remove_clip(clip_index):
        auto_save_session(session)
        return jsonify({
            'success': True,
            'message': '片段已刪除'
        })
    else:
        return jsonify({
            'success': False,
            'error': '片段索引無效'
        }), 400

@app.route('/api/export/<session_id>', methods=['POST'])
def export_clips(session_id):
    """Export clips to JSON file"""
    if session_id not in session_data:
        return jsonify({
            'success': False,
            'error': '會話不存在'
        }), 404
        
    session = session_data[session_id]
    
    if not session.clips:
        return jsonify({
            'success': False,
            'error': '沒有片段可匯出'
        }), 400
        
    data = request.get_json() or {}
    output_path = data.get('output_path', '.')
    
    timestamp = int(time.time())
    filename = f"clips_{timestamp}.json"
    filepath = os.path.join(output_path, filename)
    
    try:
        export_data = {
            'clips': session.clips,
            'exported_at': datetime.datetime.now().isoformat(),
            'session_id': session.session_id
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=4)
            
        return jsonify({
            'success': True,
            'file_path': filepath,
            'filename': filename,
            'message': f'片段已匯出至 {filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'匯出失敗: {str(e)}'
        }), 500

@app.route('/api/clip-videos', methods=['POST'])
def clip_videos():
    """Start video clipping process"""
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': '無效的請求資料'
        }), 400
        
    json_file = data.get('json_file')
    output_directory = data.get('output_directory')
    
    if not json_file or not output_directory:
        return jsonify({
            'success': False,
            'error': '缺少必要參數'
        }), 400
        
    if not os.path.exists(json_file):
        return jsonify({
            'success': False,
            'error': 'JSON 檔案不存在'
        }), 400
        
    if not os.path.exists(output_directory):
        return jsonify({
            'success': False,
            'error': '輸出目錄不存在'
        }), 400
    
    def clipping_callback(clipped_paths):
        print(f"Clipping completed: {clipped_paths}")
    
    try:
        # Start clipping in background thread
        def run_clipping():
            VideoClipper.go(json_file, output_directory, clipping_callback)
            
        threading.Thread(target=run_clipping, daemon=True).start()
        
        return jsonify({
            'success': True,
            'message': '影片剪輯已開始'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'剪輯啟動失敗: {str(e)}'
        }), 500

@app.route('/api/auto-saves', methods=['GET'])
def list_auto_saves():
    """List available auto-save files"""
    try:
        create_auto_save_dir()
        auto_saves = []
        
        for file_path in glob.glob(os.path.join(AUTO_SAVE_DIR, "*.json")):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                file_stat = os.stat(file_path)
                auto_saves.append({
                    'file_path': file_path,
                    'filename': os.path.basename(file_path),
                    'session_id': data.get('session_id', 'unknown'),
                    'clips_count': len(data.get('clips', [])),
                    'last_modified': datetime.datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    'created_at': data.get('created_at', 'unknown')
                })
            except Exception as e:
                print(f"Error reading auto-save file {file_path}: {e}")
                
        # Sort by last modified time
        auto_saves.sort(key=lambda x: x['last_modified'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': auto_saves
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'讀取自動儲存檔案失敗: {str(e)}'
        }), 500

@app.route('/api/auto-saves/<filename>', methods=['GET'])
def load_auto_save(filename):
    """Load an auto-save file"""
    try:
        file_path = os.path.join(AUTO_SAVE_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': '自動儲存檔案不存在'
            }), 404
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Create new session from auto-save data
        session = ClipSession()
        session.session_id = data.get('session_id', session.session_id)
        session.clips = data.get('clips', [])
        
        if 'created_at' in data:
            session.created_at = datetime.datetime.fromisoformat(data['created_at'])
        if 'last_modified' in data:
            session.last_modified = datetime.datetime.fromisoformat(data['last_modified'])
            
        session_data[session.session_id] = session
        
        return jsonify({
            'success': True,
            'data': session.to_dict(),
            'message': '自動儲存檔案已載入'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'載入自動儲存檔案失敗: {str(e)}'
        }), 500

# Initialize on startup
cleanup_old_auto_saves()

if __name__ == '__main__':
    print("Starting Flask backend server...")
    print(f"Auto-save directory: {AUTO_SAVE_DIR}")
    app.run(host='127.0.0.1', port=5000, debug=True)