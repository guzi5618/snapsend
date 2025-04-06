#!/usr/bin/env python3
import http.server
import socketserver
import socket
import webbrowser
import os
import threading
import json
import base64
import random
import time
import datetime
from urllib.parse import urlparse, parse_qs, unquote

# Get local IP address


def get_local_ip():
    # 尝试多种方法获取IP
    try:
        # 首选方法：创建UDP连接并获取本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()

        # 确认是否为局域网IP
        if ip.startswith(('192.168.', '10.', '172.16.', '172.17.', '172.18.')):
            return ip
    except Exception as e:
        print(f"首选IP检测方法失败: {e}")

    # 备选方法：尝试获取所有网络接口
    try:
        interfaces = socket.gethostbyname_ex(socket.gethostname())[-1]
        for ip in interfaces:
            if ip.startswith(('192.168.', '10.', '172.16.', '172.17.', '172.18.')):
                return ip
    except Exception as e:
        print(f"备选IP检测方法失败: {e}")

    # 所有方法都失败，返回本地回环
    return "127.0.0.1"

# Custom HTTP request handler


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse URL path
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # Print the requested path
        print(f"GET request for: {path}")

        # API endpoint to get received files list (from mobile to desktop)
        if path == '/api/files':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            # Get list of files in received_files directory
            files = []
            current_time = time.time()
            one_day_ago = current_time - (24 * 60 * 60)  # 24 hours in seconds

            if os.path.exists('received_files'):
                for filename in os.listdir('received_files'):
                    file_path = os.path.join('received_files', filename)
                    if os.path.isfile(file_path):
                        file_stats = os.stat(file_path)
                        file_size = file_stats.st_size
                        created_time = file_stats.st_mtime

                        # Only include files created in the last 24 hours
                        if created_time >= one_day_ago:
                            # Format the timestamp as a readable date
                            created_date = datetime.datetime.fromtimestamp(
                                created_time).strftime('%Y-%m-%d %H:%M:%S')

                            files.append({
                                'name': filename,
                                'size': file_size,
                                'path': f'/received_files/{filename}',
                                'created': created_date,
                                'timestamp': created_time
                            })

            # Sort by timestamp, newest first
            files.sort(key=lambda x: x['timestamp'], reverse=True)

            # Send file list as JSON
            self.wfile.write(json.dumps(files).encode('utf-8'))
            return

        # API endpoint to get shared files list (from desktop to mobile)
        elif path == '/api/shared-files':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            # Get list of files in shared_files directory
            files = []
            current_time = time.time()
            one_day_ago = current_time - (24 * 60 * 60)  # 24 hours in seconds

            if os.path.exists('shared_files'):
                for filename in os.listdir('shared_files'):
                    file_path = os.path.join('shared_files', filename)
                    if os.path.isfile(file_path):
                        file_stats = os.stat(file_path)
                        file_size = file_stats.st_size
                        created_time = file_stats.st_mtime

                        # Only include files created in the last 24 hours
                        if created_time >= one_day_ago:
                            # Format the timestamp as a readable date
                            created_date = datetime.datetime.fromtimestamp(
                                created_time).strftime('%Y-%m-%d %H:%M:%S')

                            files.append({
                                'name': filename,
                                'size': file_size,
                                'path': f'/shared_files/{filename}',
                                'created': created_date,
                                'timestamp': created_time
                            })

            # Sort by timestamp, newest first
            files.sort(key=lambda x: x['timestamp'], reverse=True)

            # Send file list as JSON
            self.wfile.write(json.dumps(files).encode('utf-8'))
            return

        # Serve received files
        elif path.startswith('/received_files/'):
            encoded_filename = path.split('/')[-1]
            filename = unquote(encoded_filename)  # 解码URL编码的文件名
            file_path = os.path.join('received_files', filename)

            if os.path.exists(file_path) and os.path.isfile(file_path):
                # Determine content type based on file extension
                extension = os.path.splitext(filename)[1].lower()
                content_type = self.get_content_type(extension)

                # Send the file
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(os.path.getsize(file_path)))
                # 使用引号包裹文件名，并处理特殊字符
                safe_filename = filename.replace('"', '\\"')
                self.send_header('Content-Disposition', f'attachment; filename="{safe_filename}"')
                self.end_headers()

                # Read and send the file
                with open(file_path, 'rb') as file:
                    self.wfile.write(file.read())
                return
            else:
                self.send_error(404, 'File not found')
                return

        # Serve shared files
        elif path.startswith('/shared_files/'):
            encoded_filename = path.split('/')[-1]
            filename = unquote(encoded_filename)  # 解码URL编码的文件名
            file_path = os.path.join('shared_files', filename)

            print(f"Trying to access shared file: '{filename}' (from '{encoded_filename}')")
            print(f"Full path: {file_path}")

            if os.path.exists(file_path) and os.path.isfile(file_path):
                # Determine content type based on file extension
                extension = os.path.splitext(filename)[1].lower()
                content_type = self.get_content_type(extension)

                print(f"File found! Serving '{filename}' ({os.path.getsize(file_path)} bytes)")

                # Send the file
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(os.path.getsize(file_path)))
                # 使用引号包裹文件名，并处理特殊字符
                safe_filename = filename.replace('"', '\\"')
                self.send_header('Content-Disposition', f'attachment; filename="{safe_filename}"')
                self.end_headers()

                # Read and send the file
                with open(file_path, 'rb') as file:
                    self.wfile.write(file.read())
                return
            else:
                self.send_error(404, 'File not found')
                return

        # Serve index.html for the root path
        elif path == '/':
            self.path = '/desktop.html'

        # Proceed with default handler
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        """Handle POST requests for file uploads"""
        print(f"POST request for: {self.path}")

        # Handle upload from mobile to desktop
        if self.path == '/upload':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                # Try to parse JSON data
                json_data = json.loads(post_data.decode('utf-8'))

                # If it's a file upload
                if 'fileName' in json_data and 'fileData' in json_data:
                    file_name = json_data['fileName']
                    file_data = json_data['fileData']

                    # Create received_files directory if it doesn't exist
                    if not os.path.exists('received_files'):
                        os.makedirs('received_files')

                    # If fileData is a base64 string
                    if isinstance(file_data, str):
                        try:
                            file_bytes = base64.b64decode(file_data)
                        except Exception:
                            file_bytes = file_data.encode('utf-8')
                    elif isinstance(file_data, list):
                        file_bytes = bytes(file_data)
                    else:
                        file_bytes = file_data

                    # Save the file
                    file_path = os.path.join('received_files', file_name)
                    with open(file_path, 'wb') as f:
                        if isinstance(file_bytes, bytes):
                            f.write(file_bytes)
                        else:
                            f.write(file_bytes.encode('utf-8'))

                    print(f"File saved: {file_name} ({os.path.getsize(file_path)} bytes)")

                    # Send success response
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'status': 'success',
                        'message': f'File {file_name} received successfully'
                    }).encode('utf-8'))
                    return
            except Exception as e:
                print(f"Error processing upload: {e}")
                # If JSON parsing fails or any other error
                pass

        # Handle upload from desktop to mobile
        elif self.path == '/upload-to-mobile':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                # Try to parse JSON data
                json_data = json.loads(post_data.decode('utf-8'))

                # If it's a file upload
                if 'fileName' in json_data and 'fileData' in json_data:
                    file_name = json_data['fileName']
                    file_data = json_data['fileData']

                    # Create shared_files directory if it doesn't exist
                    if not os.path.exists('shared_files'):
                        os.makedirs('shared_files')

                    # If fileData is a base64 string
                    if isinstance(file_data, str):
                        try:
                            file_bytes = base64.b64decode(file_data)
                        except Exception:
                            file_bytes = file_data.encode('utf-8')
                    elif isinstance(file_data, list):
                        file_bytes = bytes(file_data)
                    else:
                        file_bytes = file_data

                    # Save the file
                    file_path = os.path.join('shared_files', file_name)
                    with open(file_path, 'wb') as f:
                        if isinstance(file_bytes, bytes):
                            f.write(file_bytes)
                        else:
                            f.write(file_bytes.encode('utf-8'))

                    print(f"File shared: {file_name} ({os.path.getsize(file_path)} bytes)")

                    # Send success response
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'status': 'success',
                        'message': f'File {file_name} shared successfully'
                    }).encode('utf-8'))
                    return
            except Exception as e:
                print(f"Error processing shared file: {e}")
                # If JSON parsing fails or any other error
                pass

        # Default response for other POST requests or errors
        self.send_response(400)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'error',
            'message': 'Invalid request'
        }).encode('utf-8'))

    def get_content_type(self, extension):
        """Determine content type based on file extension"""
        content_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.zip': 'application/zip'
        }
        return content_types.get(extension, 'application/octet-stream')


def find_available_port(start_port=8000, max_attempts=10):
    """尝试找到一个可用的端口"""
    port = start_port
    attempts = 0

    while attempts < max_attempts:
        try:
            # 创建一个临时socket来测试端口是否可用
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(1)
            test_socket.bind(('', port))
            test_socket.close()
            return port  # 端口可用
        except OSError:
            # 端口不可用，尝试下一个
            attempts += 1
            if port == start_port:
                # 如果默认端口不可用，尝试一个随机端口
                port = random.randint(8001, 9000)
            else:
                # 否则，继续递增
                port += 1

    # 如果所有尝试都失败，使用一个随机高端口
    return random.randint(49152, 65535)

# Main function


def main():
    # Create required directories if they don't exist
    for directory in ['received_files', 'shared_files']:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Get local IP address
    ip = get_local_ip()

    # 找到可用端口
    port = find_available_port()
    print(f"尝试使用端口: {port}")

    # Create handler with current directory
    handler = CustomHTTPRequestHandler

    # Disable browser caching
    handler.extensions_map.update({
        '.js': 'application/javascript; charset=UTF-8',
        '.html': 'text/html; charset=UTF-8',
    })

    try:
        # Create server
        httpd = socketserver.TCPServer(("", port), handler)

        print(f"Server running at http://{ip}:{port}/")
        print(f"For mobile access, use http://{ip}:{port}/mobile.html")
        print("Press Ctrl+C to stop the server")

        # Open browser automatically
        threading.Timer(1.0, lambda: webbrowser.open(f"http://{ip}:{port}/")).start()

        # Start server
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        if 'httpd' in locals():
            httpd.server_close()
    except Exception as e:
        print(f"Error starting server: {e}")
        print("尝试使用一个随机端口...")
        # 如果仍然失败，尝试一个完全随机的端口
        port = random.randint(10000, 65000)
        try:
            httpd = socketserver.TCPServer(("", port), handler)
            print(f"Server running at http://{ip}:{port}/")
            print(f"For mobile access, use http://{ip}:{port}/mobile.html")
            print("Press Ctrl+C to stop the server")

            # Open browser automatically
            threading.Timer(1.0, lambda: webbrowser.open(f"http://{ip}:{port}/")).start()

            httpd.serve_forever()
        except Exception as e2:
            print(f"无法启动服务器: {e2}")
            print("请确保没有其他程序占用过多端口，或者尝试手动终止其他Python进程")


if __name__ == "__main__":
    main()
