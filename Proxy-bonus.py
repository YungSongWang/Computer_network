"""
This part is to try to complete Bonus Marks Questions
It implements the following additional functionalities:
1. Check if the expire in the cache needs to be updated.
2. Pre-fetch the file, looking for “href=” and “src=”.
3. Handle the URL of the server port

Each section of the code is documented to explain its purpose and functionality.
"""

import socket
import sys
import os
import argparse
import re
from datetime import datetime

# Buffer size 
BUFFER_SIZE = 1000000

#Get command-line arguments for hostname and port
parser = argparse.ArgumentParser()
parser.add_argument('hostname', help='the IP Address Of Proxy Server')
parser.add_argument('port', help='the port number of the proxy server')
args = parser.parse_args()
proxyHost = args.hostname
proxyPort = int(args.port)

# Create the server socket to listen for client requests
try:
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((proxyHost, proxyPort))
    serverSocket.listen(5)
    print("Proxy server is running...")
except Exception as e:
    print(f"Error setting up server: {e}")
    sys.exit()

def is_cache_fresh(cache_location):
    """
    Check if the cached file is still fresh based on the `Expires` header.
    - Read the first line of the cache
    - Compare the value of expires
    - Returns whether the value is invalid
    """
    try:
        with open(cache_location, 'r') as cache_file:
            headers = cache_file.readline()
            match = re.search(r'Expires: (.+)', headers)
            if match:
                expires = datetime.strptime(match.group(1), '%a, %d %b %Y %H:%M:%S GMT')
                return datetime.utcnow() < expires
    except Exception:
        pass
    return False

def prefetch_associated_files(html_content, hostname):
    """
    Pre-fetch associated files (e.g., `href` and `src` attributes in HTML) and cache them.
    - Extracts URLs from the HTML content using regex.
    - Fetches each resource from the origin server and caches it locally.
    - Does not send these resources back to the client.
    """
    urls = re.findall(r'(?:href|src)="([^"]+)"', html_content)
    for url in urls:
        if not url.startswith('http'):
            url = f"http://{hostname}/{url.lstrip('/')}"  # Convert relative URLs to absolute
        try:
            origin_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            origin_socket.connect((hostname, 80))
            request = f"GET {url} HTTP/1.1\r\nHost: {hostname}\r\n\r\n"
            origin_socket.sendall(request.encode())
            response = origin_socket.recv(BUFFER_SIZE)
            cache_location = './' + hostname + '/' + url.split('/')[-1]
            os.makedirs(os.path.dirname(cache_location), exist_ok=True)
            with open(cache_location, 'wb') as cache_file:
                cache_file.write(response)
            origin_socket.close()
        except Exception as e:
            print(f"Failed to prefetch {url}: {e}")

# Main loop to handle client requests
while True:
    try:
        # Accept a connection from the client
        clientSocket, clientAddress = serverSocket.accept()
        message = clientSocket.recv(BUFFER_SIZE).decode('utf-8')
        requestParts = message.split()
        method, URI, version = requestParts[0], requestParts[1], requestParts[2]

        # Parse the URI to extract hostname, port, and resource
        match = re.match(r'http://([^:/]+)(?::(\d+))?(/.*)?', URI)
        if not match:
            clientSocket.close()
            continue
        hostname, port, resource = match.groups()
        port = int(port) if port else 80  # Default to port 80 if not specified
        resource = resource if resource else '/'

        # Determine the cache location for the requested resource
        cache_location = f'./{hostname}{resource.replace("/", "_")}'
        if os.path.isfile(cache_location) and is_cache_fresh(cache_location):
            # If the resource is cached and still fresh, send it to the client
            with open(cache_location, 'rb') as cache_file:
                clientSocket.sendall(cache_file.read())
        else:
            # If the resource is not cached or is stale, fetch it from the origin server
            origin_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            origin_socket.connect((hostname, port))
            request = f"{method} {resource} {version}\r\nHost: {hostname}\r\n\r\n"
            origin_socket.sendall(request.encode())
            response = origin_socket.recv(BUFFER_SIZE)
            clientSocket.sendall(response)

            # Cache the response locally
            os.makedirs(os.path.dirname(cache_location), exist_ok=True)
            with open(cache_location, 'wb') as cache_file:
                cache_file.write(response)

            # If the response is HTML, pre-fetch associated files
            if b"text/html" in response:
                html_content = response.decode('utf-8', errors='ignore')
                prefetch_associated_files(html_content, hostname)

        # Close the client socket
        clientSocket.close()
    except Exception as e:
        print(f"Error: {e}")