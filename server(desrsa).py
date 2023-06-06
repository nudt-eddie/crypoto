from os import truncate
import queue
from socket import *
import threading
import rsa
import des
import json
from time import *
from threading import*
###定义地址端口
addr = "192.168.2.101"
port = 7777
rsaKeyLen = 256

idNum = 0####用于标记是哪个客户端
maxRecWindow = 1024


clientHello = "Hello server, I want to connect with you"
serverHello = "OK client. This is your public key. Please send your encrypted key."
showCrypKeyFlag = "This is my encrypted key."
serverReceivedKeyFlag = "Gotcha. We can chat now."


class clientInfos:
    idNum = None
    pubKey = None
    priKey = None
    socket = None
    desKey = None

def encryTheMsgByDES(keyOfDES,msg):###通过DES加密，msg是字符串,返回加密后的bytes
    ####默认使用EBC加密
    desObj = des.DesKey(keyOfDES)
    le = len(msg) 
    msgByte = msg.encode("utf-8")
    decMsg = desObj.encrypt(msgByte,None,True)
    return decMsg

def receive(clientInfo):###接收消息，回复消息的处理线程
    idNum = clientInfo.idNum
    pubKey = clientInfo.pubKey
    priKey = clientInfo.priKey
    socket = clientInfo.socket####分别为公钥类，私钥类，socket
    global maxRecWindow
    while True:###receive first msg
        try:
            msg = socket.recv(maxRecWindow).decode("utf-8")
            print("the first msg receive from client {},the clientHello is {}".format(idNum,msg))
            socket.send(serverHello.encode("utf-8"))

            print("ok,client{},your n is : {},e is : {}".format(idNum,pubKey.n,pubKey.e))
            msg = {"n":pubKey.n,"e":pubKey.e}###发送一条json消息
            msg = json.dumps(msg).encode("utf-8")
            socket.send(msg)
            print("client{} ,I have send you pubKey".format(idNum))
            break
        except:
            print("receive the first msg from client error")
            return
    while True:###receive the des key
        try:
            secondHelloMsg = socket.recv(maxRecWindow)
            print("I received the second msg:",secondHelloMsg)
            desKeyEncrypted = socket.recv(maxRecWindow)
            #print("the second msg receive from client %s,the encrypted desKey is %s",idNum,desKeyEncrypted)
            
            desKey = rsa.decrypt(desKeyEncrypted,priKey)###byte
            print("client{},your des key is:{}".format(idNum,desKey))

            desKey = des.DesKey(desKey)###创建一个des类
            clientInfo.desKey = desKey

            socket.send(serverReceivedKeyFlag.encode("utf-8"))###表示收到消息
            print(serverReceivedKeyFlag)
            break
        except:
            print("receive the second  msgfrom client error")
            return
    
    while True:###收到消息使用DES方法解密，注意clientInfo中的desKey是str
        try:
            encMsg = socket.recv(maxRecWindow)##bytes
            #print("the encMsg from client%s is %s",idNum,encMsg)
            msg = clientInfo.desKey.decrypt(encMsg).decode("utf-8")
            print("the msg from client{} is: {}".format(idNum,msg))
            if ("quit" == msg[0:4]):###如果是退出指令
                print("client quit")
                clientInfo.socket.close()
                return
            print("server,please input your msg to client:{}".format(idNum))
            msg = input().encode("utf-8")
            encMsg = clientInfo.desKey.encrypt(msg,None,True)
            socket.send(encMsg)
        except:
            print("receive msg from client error,close this connection")
            clientInfo.socket.close()
            #sleep(1)
            return


        

def main():
    serverSocket = socket(AF_INET,SOCK_STREAM)
    print("serverSocket socket has created")
    serverSocket.bind((addr,port))###绑定地址，端口,定义在最上方
    print("serverSocket bind on {},port is {}".format(addr,port))
    serverSocket.listen(5)###挂起应用程序，大部分设置为5即可
    global idNum
    clientsList = []###存储各个客户端，索引即为idNum

    while True:
        client = serverSocket.accept()
        clientSocket = client[0]
        clientAddrAndPort = client[1]
        print("A client has connected on {} : {}".format(clientAddrAndPort[0],clientAddrAndPort[1]))
        global rsaKeyLen
        (pubKey,priKey) = rsa.newkeys(rsaKeyLen)
        ####创建一个clientSocket
        clientInfo = clientInfos()
        clientInfo.pubKey = pubKey
        clientInfo.priKey = priKey
        clientInfo.idNum = idNum
        clientInfo.socket = clientSocket###
        clientsList.append(clientInfo)
        thre = threading.Thread(target=receive,args=(clientInfo,))
        thre.start()
        idNum+=1
    

main()


