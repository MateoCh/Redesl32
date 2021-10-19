from abc import abstractmethod
import socket
from threading import Lock, Thread
import hashlib
import pickle
import logging
from datetime import date, datetime
import argparse
import os
import time
import threading

SIZE = 4096
cn=1
FORMAT = "utf-8"
parser = argparse.ArgumentParser()
parser.add_argument("--threads", type=int, default=cn, help="Number of clients")
parser.add_argument("--file_id",type=int, choices=[1,2], default=1, help="1 for 100MB file, 2 for 250 MB file")

sock =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

class Client(Thread):
    def __init__(self, i, logger, lock,id):
        Thread.__init__(self)
        self.i = i
        self.logger = logger
        self.lock = lock
        self.file_id = id

    def run(self):
        msg="Hello from client"
        filename = "ArchivosRecibidos/Cliente"+str(self.i)+"-Prueba-"+str(args.threads)
        file = open(filename, "wb")
        sock.sendto(msg.encode("utf-8"),("127.0.0.1",12345+self.i))
        sock.settimeout(10)
        time_inicio = time.time()
        paquetes = 0
        bytes_enviados = 0
        siga=True
        while siga:
            try:
                data, addr=sock.recvfrom(4096)
                paquetes+=1
                file.write(data)
                bytes_enviados+=len(data)

            except socket.timeout:
                siga=False
        print("Fin")
        print("Archivo recibido por completo en el cliente", self.i)
        time_final = time.time()
        contenido_output = ""
        contenido_output += "Tamanio archivo: "+str(os.path.getsize(filename))+"\n"
        contenido_output +="Tiempo de transferencia"+str(self.i)+" es "+ str(time_final-time_inicio)+"\n"
        contenido_output += "Paquetes recibidos por el cliente "+str(self.i)+" son "+ str(paquetes)+"\n"
        contenido_output += "Bytes recibidos por el cliente "+str(self.i)+" son "+ str(bytes_enviados)+"\n"

        file1 = open(filename,"rb")
        data1 = file1.read()
        vhash = hashlib.md5(data1).hexdigest()

        if self.file_id==1:
            file_name = "../Data/100.txt"
        else:
            file_name = "../Data/250.txt"
        file2 = open(file_name, "r")
        data2 = file2.read()
        dataEn=data2.encode(FORMAT)
        dataHash = hashlib.md5(dataEn).hexdigest()

        print(str(self.i)+"vhash:"+vhash)
        print(str(self.i)+"dataHash:"+dataHash)
        if vhash==dataHash:
            #file = open(filename, "wb")
            #file.write(data)
            #file.close()
            print("hash correcto cliente "+str(self.i))
            contenido_output += "Archivo recibido correctamente por cliente "+str(self.i)+"\n"
        else:
            print("hash incorrecto cliente "+str(self.i))
            contenido_output +="Archivo NO recibido correctamente por cliente"+str(self.i)+"\n"
        contenido_output+="\n"
        self.lock.acquire()
        self.logger.write(contenido_output)
        self.lock.release()


def main(args):
    fecha = datetime.now()
    date_time = fecha.strftime("%m-%d-%Y-%H-%M-%S")
    log = open("logs/"+date_time+"-log.txt", "w")
    if args.file_id==1:
        file_name = "100.txt"
    else:
        file_name = "250.txt"
    log.write("Nombre archivo: "+ file_name+"\n")
    for i in range(args.threads):
        lock = threading.Lock()
        c=Client(i,log, lock,args.file_id)
        c.start()   

if __name__ == "__main__":
    args = parser.parse_args()
    if not os.path.isdir("./logs"):
        os.mkdir("./logs")
    if not os.path.isdir("./ArchivosRecibidos"):
        os.mkdir("./ArchivosRecibidos")

    main(args)