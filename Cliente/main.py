import hashlib
from os import set_inheritable
import socket
from socket import error
import argparse
from threading import Thread
from datetime import date, datetime
import os
import threading
import time

SIZE = 32768
cn=5
FORMAT = "utf-8"
parser = argparse.ArgumentParser()
parser.add_argument("--threads", type=int, default=cn, help="Number of clients")
parser.add_argument("--file_id",type=int, choices=[1,2], default=1, help="1 for 100MB file, 2 for 250 MB file")

client_connected = 0

class Client(Thread):
    def __init__(self, i, logger, lock):
        Thread.__init__(self)
        self.i = i
        self.logger = logger
        self.lock = lock
    def run(self):
        print("Cliente "+str(self.i)+" iniciando conexión")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("localhost", 9879))
        sock.connect(("localhost",9879+self.i+1))
        print("Cliente "+str(self.i)+ " conectado")
        
        sock.sendto(b'Start transmision OK'.encode(FORMAT),("localhost",9879+self.i))
        filename = "ArchivosRecibidos/Cliente"+str(self.i)+"-Prueba-"+str(args.threads)
        sizefile = s.recv(SIZE)
        dataHash = s.recv(SIZE)
        print(str(self.i)+"hash:"+dataHash.decode(FORMAT))
        data = ""
        i=0
        time_inicio = time.time()
        paquetes = 0
        bytes_enviados = 0
        file = open(filename, "wb")

        while True:
            try:
                input_data, addr = sock.recvfrom(SIZE)
                paquetes+=1
            except error:
                print ("Error de lectura")
                break
            else:
                if input_data:
                    # Compatibilidad con Python 3.
                    if input_data.endswith(b"Termino:200"):
                        #data+=input_data.replace(b"Termino:200",b"")
                        file.write(input_data.replace(b"Termino:200",b""))
                        file.close()
                        bytes_enviados+=len(input_data.replace(b"Termino:200",b""))
                        break
                    else:
                        # Almacenar datos.
                        # data+=input_data.decode(FORMAT)
                        file.write(input_data)
                        bytes_enviados+=len(input_data)
                else:
                    break

        print("Archivo recibido por completo en el cliente", self.i)
        time_final = time.time()
        contenido_output = ""
        contenido_output += "Tamanio archivo: "+str(sizefile)+"\n"
        contenido_output +="Tiempo de transferencia"+str(self.i)+" es "+ str(time_final-time_inicio)+"\n"
        contenido_output += "Paquetes recibidos por el cliente "+str(self.i)+" son "+ str(paquetes)+"\n"
        contenido_output += "Bytes recibidos por el cliente "+str(self.i)+" son "+ str(bytes_enviados)+"\n"
        #data = s.recv(SIZE).decode(FORMAT)
        #print(str(self.i)+"Data:"+data)
        #data= data.encode(FORMAT)
        file = open(filename,"rb")
        data = file.read()
        vhash = hashlib.md5(data).hexdigest()
        print(str(self.i)+"vhash:"+vhash)
        print(str(self.i)+"dataHash:"+dataHash.decode(FORMAT))
        if vhash==dataHash.decode(FORMAT):
            #file = open(filename, "wb")
            #file.write(data)
            #file.close()
            print("hash correcto cliente "+str(self.i))
            contenido_output += "Archivo recibido correctamente por cliente "+str(self.i)+"\n"
            s.send((b"hash correcto cliente "+str(self.i).encode(FORMAT)))
        else:
            print("hash incorrecto cliente "+str(self.i))
            contenido_output +="Archivo NO recibido correctamente por cliente"+str(self.i)+"\n"
            s.send((b"hash correcto cliente "+str(self.i).encode(FORMAT)))        
        contenido_output+="\n"
        self.lock.acquire()
        self.logger.write(contenido_output)
        self.lock.release()
        s.close()
        sock.close()



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
        c=Client(i,log, lock)
        c.start()      
        

if __name__ == "__main__":
    args = parser.parse_args()
    if not os.path.isdir("./logs"):
        os.mkdir("./logs")
    if not os.path.isdir("./ArchivosRecibidos"):
        os.mkdir("./ArchivosRecibidos")

    main(args)
