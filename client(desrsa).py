
import threading
from time import sleep
from rsa import key
from client_socket import *

import rsa
import des

import json
import queue
####some paraments

keyofDES = b'12345678'
rsaKeyLen = 256
queueSize = 100
msgQueue = queue.Queue(queueSize)###用于存储输入input信息

###some msgs
clientHello = "Hello server, I want to connect with you"
serverHello = "OK client. This is your public key. Please send your encrypted key."
showCrypKeyFlag = "This is my encrypted key."
serverReceivedKeyFlag = "Gotcha. We can chat now."



def sendMsgToGetRSAPbk(clientSocket):###通过访问服务器，获取公钥
    clientSocket.send(clientHello)

def sendMyDesKeyToServer(clientSocket,desKey):
    helloText = "This is my encrypted key."
    sendMsgToServer(clientSocket,helloText)
    sendMsgToServer(clientSocket,desKey)


def receive_thread(clientInfo):###创建一个输入进程，不断获取输入，并将输入存储至msgQueue中
    
    while True:
        try:
            encMsg = clientInfo.socket.recv(1024)
            print("received the encMsg from server:",encMsg)
            decMsg = clientInfo.desKey.decrypt(encMsg).decode("utf-8")
            print("received the msg from server:",decMsg)

            ####发送消息
            
        except:
            print("error to receive from server")
            break
def main():
    print("input quit to exit")
    while True:
        keyofDES = input("please input an 8 bytes key :")
        if (keyofDES == "quit"):
            return
        if (len(keyofDES) != 8):
            print("your key is not suitable")
        else:
            keyofDES = keyofDES.encode("utf-8")
            break

#####初始化信息
    clientInfo = createASocket(ip,port)
    if not clientInfo:
        print("connect to server failed")
        return
    clientInfo.desKey = des.DesKey(keyofDES)
    if not clientInfo:
        print("connect to server error")
        return
    sendMsgToServer(clientInfo,clientHello)
    #####接收前几条hello消息
    
    firstMsg = clientInfo.socket.recv(1024).decode("utf-8")
    
    print("first msg received from server is :",firstMsg)
    pubKeyMsg = clientInfo.socket.recv(1024).decode("utf-8")###公钥信息
    pubKeyMsg = json.loads(pubKeyMsg)
    print("my pubKey is:",pubKeyMsg)
    clientInfo.n = pubKeyMsg["n"]
    clientInfo.e = pubKeyMsg["e"]
    pubKey,priKey = rsa.newkeys(rsaKeyLen)####我的公钥
    pubKey.n = clientInfo.n
    pubKey.e = clientInfo.e
    clientInfo.pubKey = pubKey###接收到公钥。使用公钥进行加密
    decKey = rsa.encrypt(keyofDES,pubKey)###将DES密钥加密
    sendMsgToServer(clientInfo,showCrypKeyFlag)
    #decKey = decKey.decode("gbk")###没办法加码
    sendDecKeyToServer(clientInfo,decKey)######发送我的加密DES密钥给服务端


    ###接下来接收到服务器的开始聊天后，即可不断input
    while True:
        try:
            print("received the hello goat msg from server:",clientInfo.socket.recv(1024).decode("utf-8"))
            break
        except:
            print("error to receive from server")
            break

    

    
    threading.Thread(target=receive_thread,args=(clientInfo,)).start()###开启请求收到消息线程，不断收到消息，并print
    
    
    while True:
        print("please input your msg to server:")
        msg = input()
        if (msgQueue.full()):###如果队列满了
            print("the queue is full,please waiting")
            sleep(1)
            continue
        msgQueue.put_nowait(msg)
        msgByte = clientInfo.desKey.encrypt(msg.encode("utf-8"),None,True)
        sendFlag = sendDecMsgToServer(clientInfo,msgByte)###发送加密消息
        if (msg == "quit"):###如果是退出，直接退出
            print("I quit")
            clientInfo.socket.close()
            return
        if not sendFlag:
            print("send to server error,quit")
            return

main()
