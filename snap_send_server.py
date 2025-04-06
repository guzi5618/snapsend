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

# File expiration time (seconds)
FILE_EXPIRY_TIME = 300  # 5 minutes

# Get local IP address


def get_local_ip():
    # Try multiple methods to get IP
    try:
        # Preferred method: Create UDP connection and get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()

        # Confirm if it's a local network IP
        if ip.startswith(('192.168.', '10.', '172.16.', '172.17.', '172.18.')):
            return ip
    except Exception as e:
        print(f"Primary IP detection method failed: {e}")

    # Alternative method: Try to get all network interfaces
    try:
        interfaces = socket.gethostbyname_ex(socket.gethostname())[-1]
        for ip in interfaces:
            if ip.startswith(('192.168.', '10.', '172.16.', '172.17.', '172.18.')):
                return ip
    except Exception as e:
        print(f"Alternative IP detection method failed: {e}")

    # All methods failed, return local loopback
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

            if os.path.exists('received_files'):
                for filename in os.listdir('received_files'):
                    file_path = os.path.join('received_files', filename)
                    if os.path.isfile(file_path):
                        file_stats = os.stat(file_path)
                        file_size = file_stats.st_size
                        created_time = file_stats.st_mtime

                        # Calculate remaining time (seconds)
                        time_left = max(0, int(created_time + FILE_EXPIRY_TIME - current_time))

                        # Only include unexpired files
                        if time_left > 0:
                            # Format the timestamp as a readable date
                            created_date = datetime.datetime.fromtimestamp(
                                created_time).strftime('%Y-%m-%d %H:%M:%S')

                            files.append({
                                'name': filename,
                                'size': file_size,
                                'path': f'/received_files/{filename}',
                                'created': created_date,
                                'timestamp': created_time,
                                'expiresIn': time_left  # Remaining seconds
                            })
                        else:
                            # File has expired, delete it
                            try:
                                os.remove(file_path)
                                print(f"Deleted expired file: {file_path}")
                            except Exception as e:
                                print(f"Error deleting file: {e}")

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

            if os.path.exists('shared_files'):
                for filename in os.listdir('shared_files'):
                    file_path = os.path.join('shared_files', filename)
                    if os.path.isfile(file_path):
                        file_stats = os.stat(file_path)
                        file_size = file_stats.st_size
                        created_time = file_stats.st_mtime

                        # Calculate remaining time (seconds)
                        time_left = max(0, int(created_time + FILE_EXPIRY_TIME - current_time))

                        # Only include unexpired files
                        if time_left > 0:
                            # Format the timestamp as a readable date
                            created_date = datetime.datetime.fromtimestamp(
                                created_time).strftime('%Y-%m-%d %H:%M:%S')

                            files.append({
                                'name': filename,
                                'size': file_size,
                                'path': f'/shared_files/{filename}',
                                'created': created_date,
                                'timestamp': created_time,
                                'expiresIn': time_left  # Remaining seconds
                            })
                        else:
                            # File has expired, delete it
                            try:
                                os.remove(file_path)
                                print(f"Deleted expired file: {file_path}")
                            except Exception as e:
                                print(f"Error deleting file: {e}")

            # Sort by timestamp, newest first
            files.sort(key=lambda x: x['timestamp'], reverse=True)

            # Send file list as JSON
            self.wfile.write(json.dumps(files).encode('utf-8'))
            return

        # Serve received files
        elif path.startswith('/received_files/'):
            encoded_filename = path.split('/')[-1]
            filename = unquote(encoded_filename)  # Decode URL-encoded filename
            file_path = os.path.join('received_files', filename)

            if os.path.exists(file_path) and os.path.isfile(file_path):
                # Determine content type based on file extension
                extension = os.path.splitext(filename)[1].lower()
                content_type = self.get_content_type(extension)

                # Send the file
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(os.path.getsize(file_path)))
                # Use quotes for filename and handle special characters
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
            filename = unquote(encoded_filename)  # Decode URL-encoded filename
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
                # Use quotes for filename and handle special characters
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
    """Try to find an available port"""
    port = start_port
    attempts = 0

    while attempts < max_attempts:
        try:
            # Create a temporary socket to test if port is available
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(1)
            test_socket.bind(('', port))
            test_socket.close()
            return port  # Port is available
        except OSError:
            # Port not available, try another one
            attempts += 1
            if port == start_port:
                # If default port isn't available, try a random port
                port = random.randint(8001, 9000)
            else:
                # Otherwise, continue incrementing
                port += 1

    # If all attempts fail, use a random high port
    return random.randint(49152, 65535)

# Main function


def main():
    # Create required directories if they don't exist
    for directory in ['received_files', 'shared_files']:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Get local IP address
    ip = get_local_ip()

    # Find available port
    port = find_available_port()
    print(f"Trying to use port: {port}")

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
        print("Trying to use a random port...")
        # If still fails, try a completely random port
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
            print(f"Unable to start server: {e2}")
            print("Please make sure no other programs are using too many ports, or try to manually terminate other Python processes")


if __name__ == "__main__":
    main()
