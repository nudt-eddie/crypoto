from socket import socket, AF_INET, SOCK_STREAM

import queue


####some paraments


ip = "127.0.0.1"
port = 10001
msgQueue = queue.Queue(50)###设置长度为50的队列，用于寄存数据

class mySockets:
    socket = None
    idNum = None
    n = None
    e = None
    pubKey = None
    desKey = None
    

def createASocket(ip,port):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    print("trying to connect to server")
    try:
        errorFlag = clientSocket.connect((ip,port))
    except:
        print("target server is refused to accpet")
        return False
    
    if (errorFlag):### if connect to server error
        print(errorFlag)
        print("connect to server error")
        return False
    else:
        print("connect to server success")
        clientSockets = mySockets()
        clientSockets.socket = clientSocket
        return clientSockets

def sendMsgToServer(clientSocket,msg):###msg is pythong object,###if success ,return true ,else return false
    try:
        #打包信息
        data = msg
        data = data.encode('utf-8')
        clientSocket.socket.send(data)
        print("send msg to server,msg is \t:",msg)
        return True
    except Exception as e:
        print("error to send msg to server ,error return is :",e)
        return False

def sendDecKeyToServer(clientSocket,msg):###msg is byte
    try:
        #打包信息
        data = msg
        clientSocket.socket.send(data)
        print("send dec key to server,msg is \t:",msg)
        return True
    except Exception as e:
        print("error to send msg to server ,error return is :",e)
        return False

def sendDecMsgToServer(clientSocket,msg):###msg is byte
    try:
        #打包信息
        data = msg
        clientSocket.socket.send(data)
        print("send dec msg to server,msg is \t:",msg)
        return True
    except Exception as e:
        print("error to send msg to server ,error return is :",e)
        return False

def recerveMsgFromServer(clientSocket):##receiver the msg from Server,###if success ,return data ,else return false
    while True:
        try:###异步
            
            data = clientSocket.socket.recv(4096)
            print("received data from server:\t",data)
            if (str(data,encoding = "utf-8") == ""):
                print("maybe server has closesd connection,data is empty")
                break
            msgQueue.put_nowait(data)##
            print("data has pushed into queue")
        except BlockingIOError as e:
            print("error to receive from server")###return 做到错误后直接退出，可以用作关闭client方法
            return
    
