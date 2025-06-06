# Include the libraries for socket and system calls
import socket
import sys
import os
import argparse
import re

# 1MB buffer size
BUFFER_SIZE = 1000000
# //buffer size

#Task is to implement a simple web proxy server



# Get the IP address and Port number to use for this web proxy server
parser = argparse.ArgumentParser()
parser.add_argument('hostname', help='the IP Address Of Proxy Server')
parser.add_argument('port', help='the port number of the proxy server')
args = parser.parse_args()
proxyHost = args.hostname
proxyPort = int(args.port)

# Create a server socket, bind it to a port and start listening
try:
  # Create a server socket
  # ~~~~ INSERT CODE ~~~~
  # //I want to create a socket, this socket is used to receive the client's request

  serverSocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#   //The first parameter is the address family, which is the address type
#   //The second parameter is the socket type, which is the socket type


  # ~~~~ END CODE INSERT ~~~~
  print ('Created socket')
except:
  print ('Failed to create socket')
  sys.exit()

try:
  # Bind the the server socket to a host and port
  # ~~~~ INSERT CODE ~~~~
  

  # ~~~~ END CODE INSERT ~~~~
  # //Binding port
  serverSocker.bind((proxyHost, proxyPort))
  print ('Port is bound')
except:
  print('Port is already in use')
  sys.exit()

try:
  # Listen on the server socket
  # ~~~~ INSERT CODE ~~~~
  # ~~~~ END CODE INSERT ~~~~

  serverSocker.listen(5)
  # //listening
  # //listen for incoming connections
  print ('Listening to socket')
except:
  print ('Failed to listen')
  sys.exit()

# continuously accept connections
while True:
  print ('Waiting for connection...')
  ClientSocket = None

  # Accept connection from client and store in the ClientSocket
  try:
    # ~~~~ INSERT CODE ~~~~
    ClientSocket, addr = serverSocker.accept()
    # ~~~~ END CODE INSERT ~~~~
    print ('Received a connection')
  except:
    print ('Failed to accept connection')
    sys.exit()

  # Get HTTP request from client
  # and store it in the variable: message_bytes
  # ~~~~ INSERT CODE ~~~~
  message_bytes = ClientSocket.recv(BUFFER_SIZE)
  # ~~~~ END CODE INSERT ~~~~
  message = message_bytes.decode('utf-8')
  print ('Received request:')
  print ('< ' + message)

  # Extract the method, URI and version of the HTTP client request 
  requestParts = message.split()
  method = requestParts[0]
  URI = requestParts[1]
  version = requestParts[2]

  print ('Method:\t\t' + method)
  print ('URI:\t\t' + URI)
  print ('Version:\t' + version)
  print ('')

  # Get the requested resource from URI
  # Remove http protocol from the URI
  URI = re.sub('^(/?)http(s?)://', '', URI, count=1)

  # Remove parent directory changes - security
  URI = URI.replace('/..', '')

  # Split hostname from resource name
  resourceParts = URI.split('/', 1)
  hostname = resourceParts[0]
  resource = '/'

  if len(resourceParts) == 2:
    # Resource is absolute URI with hostname and resource
    resource = resource + resourceParts[1]

  print ('Requested Resource:\t' + resource)

  # Check if resource is in cache
  try:
    cacheLocation = './' + hostname + resource
    if cacheLocation.endswith('/'):
        cacheLocation = cacheLocation + 'default'

    print ('Cache location:\t\t' + cacheLocation)

    fileExists = os.path.isfile(cacheLocation)
    
    # Check wether the file is currently in the cache
    cacheFile = open(cacheLocation, "r")
    cacheData = cacheFile.readlines()
    cache_str=''.join(cacheData)
    

    # Check for expiration dates

    # Check if the cache file is expired
    # ~~~~ INSERT CODE ~~~~
    cache_control_mat=re.search(r'Cache-Control: max-age=(\d+)', cache_str,re.IGNORECASE)
    mx_age=int(cache_control_mat.group(1)) if cache_control_mat else 0
    # print(mx_age)
    modified_time_mat=os.path.getmtime(cacheLocation)
    # print(modified_time_mat)
    current_age=time.time()-modified_time_mat
    print(f"current_age={current_age}")
    # print(current_age)
    if current_age>mx_age:
        print("cache expired")
        raise Exception("Cache expired")
    # ~~~~ END CODE INSERT ~~~~
    # Check if the cache file is still valid



    print ('Cache hit! Loading from cache file: ' + cacheLocation)
    # ProxyServer finds a cache hit
    # Send back response to client 
    # ~~~~ INSERT CODE ~~~~
    ClientSocket.sendall(''.join(cacheData).encode())
    # for data in cacheData:
    #   ClientSocket.send(data.encode())


    # ~~~~ END CODE INSERT ~~~~
    cacheFile.close()
    print ('Sent to the client:')

    # Print the cache data(updated)
    print ('> ' + cache_str)    
  except:
    # cache miss.  Get resource from origin server
    originServerSocket = None
    # Create a socket to connect to origin server
    # and store in originServerSocket
    # ~~~~ INSERT CODE ~~~~
    originServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ~~~~ END CODE INSERT ~~~~

    print ('Connecting to:\t\t' + hostname + '\n')
    try:
      # Get the IP address for a hostname
      address = socket.gethostbyname(hostname)
      # Connect to the origin server
      # ~~~~ INSERT CODE ~~~~
      originServerSocket.connect((address, 80)) #http-80, https-443
      # 目标网站的端口是80
      # //连接到服务器

      # ~~~~ END CODE INSERT ~~~~
      print ('Connected to origin Server')

      originServerRequest = ''
      originServerRequestHeader = ''
      # Create origin server request line and headers to send

      # Construct the request line and store in originServerRequest

      # and store in originServerRequestHeader and originServerRequest
      # originServerRequest is the first line in the request and
      # originServerRequestHeader is the second line in the request
      # ~~~~ INSERT CODE ~~~~

      originServerRequest = f"GET {resource} HTTP/1.1"
      originServerRequestHeader = f"Host: {hostname}"

      # //请求头
      # ~~~~ END CODE INSERT ~~~~

      # Construct the request to send to the origin server
      request = originServerRequest + '\r\n' + originServerRequestHeader + '\r\n\r\n'

      # Request the web resource from origin server
      print ('Forwarding request to origin server:')
      for line in request.split('\r\n'):
        print ('> ' + line)

      try:
        originServerSocket.sendall(request.encode())
      except socket.error:
        print ('Forward request to origin failed')
        sys.exit()

      print('Request sent to origin server\n')

      # Get the response from the origin server
      # ~~~~ INSERT CODE ~~~~
      originServerResponse = originServerSocket.recv(BUFFER_SIZE)
      # ~~~~ END CODE INSERT ~~~~

      # Send the response to the client
      # ~~~~ INSERT CODE ~~~~
      ClientSocket.sendall(originServerResponse)     
      # 转发给原始客户端
      # ~~~~ END CODE INSERT ~~~~

      #Determines whether it is cached
      response_str=originServerResponse.decode('ISO-8859-1')
      status_lines=response_str.split('\r\n')[0]
      status_code=status_lines.split()[1]

      no_store=re.search(r'Cache-Control:\s*no-store',response_str,re.IGNORECASE)
      no_cache=re.search(r'Cache-Control:\s*no-cache',response_str,re.IGNORECASE)
      # print(status_code)
      # print(no_cache)
      # print(no_store)
      # print(response_str)
      # Check for cache control

      go_cache=True
      if no_store:
        go_cache=False


      # Create a new file in the cache for the requested file.
      if go_cache:
        # Create a new file in the cache for the requested file.
        cacheDir, file = os.path.split(cacheLocation)
        print ('cached directory ' + cacheDir)
        if not os.path.exists(cacheDir):
          os.makedirs(cacheDir)
        cacheFile = open(cacheLocation, 'wb')

        # Save origin server response in the cache file
        # ~~~~ INSERT CODE ~~~~
        cacheFile.write(originServerResponse)
        # save origin server response in the cache

        # ~~~~ END CODE INSERT ~~~~
        cacheFile.close()
        print ('cache file closed')

      # finished communicating with origin server - shutdown socket writes
      print ('origin response received. Closing sockets')
      originServerSocket.close()
       
      ClientSocket.shutdown(socket.SHUT_WR)
      print ('client socket shutdown for writing')
    except OSError as err:
      print ('origin server request failed. ' + err.strerror)

  try:
    ClientSocket.close()
  except:
    print ('Failed to close client socket')
