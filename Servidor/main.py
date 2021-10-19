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

FORMAT = "utf-8"
SIZE=4096
cn=1
parser = argparse.ArgumentParser()
parser.add_argument("--threads", type=int, default=cn, help= "Number of clients")
parser.add_argument("--file_id",type=int, choices=[1,2], default=1, help="1 for 100MB file, 2 for 250 MB file")

class Server(Thread):
    def __init__(self, i, lock, sizefile, filename, logger):
        Thread.__init__(self)
        self.i=i
        self.lock=lock
        self.logger=logger
        self.sizefile=sizefile
        self.filename=filename
    def run(self):
        sock =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1",12345+self.i))
        print("recibir saludo")
        data, addr=sock.recvfrom(SIZE)
        print("inicio Hash " + str(addr))
        time_inicio = time.time()
        file = open(self.filename,"rb")
        content = file.read(SIZE)
        paquetes = 0
        bytes_enviados =0
        while content:
            sock.sendto(content,addr)
            content = file.read(SIZE)
            bytes_enviados += len(content)
            paquetes+=1
        sock.close()
        time_final = time.time()
        contenido_output = ""
        contenido_output +="Tiempo de transferencia para cliente "+str(addr)+" es "+ str(time_final-time_inicio)+"\n"
        contenido_output += "Paquetes enviado al cliente "+str(addr)+" son "+ str(paquetes)+"\n"
        contenido_output += "Bytes enviados al cliente "+str(addr)+" son "+ str(bytes_enviados)+"\n"
        contenido_output+="\n"
        self.lock.acquire()
        self.logger.write(contenido_output)
        self.lock.release()
        # self.conn.send(dataEn)
        file.close()


def main(args):
    fecha = datetime.now()
    date_time = fecha.strftime("%m-%d-%Y-%H-%M-%S")
    log = open("logs/"+date_time+"-log.txt", "w")
    if args.file_id==1:
        file_name = "../Data/100.txt"
    else:
        file_name = "../Data/250.txt"
    log.write("Nombre archivo: "+ file_name+"\n")
    sizefile = os.stat(file_name).st_size
    log.write("Tamanio archivo: "+str(sizefile)+"\n")
    for i in range(args.threads):
        lock = threading.Lock()
        c = Server(i, lock, sizefile,file_name,log)
        c.start()
    
if __name__ == "__main__":
    args = parser.parse_args()
    if not os.path.isdir("./logs"):
        os.mkdir("./logs")
    main(args)