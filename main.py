from tkinter import filedialog
from bitarray import bitarray
from PIL import Image
import tkinter as tk
import shutil
import struct
import wave
import math
import os
import re
#Clase para el nodo usado en el MinHeap
class HeapNode:
    def __init__(self, key, value = None, left = None, right = None):
        self.key = key
        self.value = value
        self.left = left
        self.right = right
#Clase MinHeap, se omitieron comprobaciones como si esta vacia o supera rangos, ya que en este contexto que se usa, no se dan casos especiales
class MinHeap:
    def __init__(self):
        self.heap = []
        self.size = 0
    
    def parent(self, id):
        return id//2
    def left_child(self, id):
        return id*2
    def right_child(self, id):
        return (id*2)+1
    
    def heapify(self, id):
        l = self.left_child(id)
        r = self.right_child(id)
        if l<=self.size and self.heap[l].key<self.heap[id].key:
            largest = l
        else:
            largest = id
        if r<=self.size and self.heap[r].key<self.heap[largest].key:
            largest = r
        
        if largest != id:
            aux = self.heap[id]
            self.heap[id] = self.heap[largest]
            self.heap[largest] = aux
            self.heapify(largest)
    
    def build_heap(self, elements):
        elements = self.auxiliar(elements)
        self.heap = elements
        self.size = len(elements)
        self.heap.insert(0, HeapNode(math.inf, 0))
        for nodo in range((self.size//2), 0, -1):
            self.heapify(nodo)
    
    def auxiliar(self, elements):
        arreglo = []
        for i in elements:
            arreglo.append(HeapNode(i[0], i[1]))
        return arreglo
    
    def peek(self):
        return (self.heap[1])
    
    def pop(self):
        aux = self.peek()
        self.heap[1] = self.heap[self.size]
        self.size -= 1
        self.heapify(1)
        return aux
    
    def decrease_key(self, id, key):
        self.heap[id].key = key
        while id>1 and self.heap[self.parent(id)].key > self.heap[id].key:
            papa = self.parent(id)
            aux = self.heap[papa]
            self.heap[papa] = self.heap[id]
            self.heap[id] = aux
            id = papa
    
    def insert(self, key, value, left, right):
        self.size += 1
        self.heap[self.size] = HeapNode(math.inf, value, left, right)
        self.decrease_key(self.size, key)
#Codificador Huffman, haciendo uso de una bfs para guardar el arbol en menos bits
class CHuffman:
    def __init__(self, texto):
        self.text = texto
        self.abc = []
        self.tree = None
        self.code = []
        self.encoded = bitarray()
        self.leaves = []
        self.diccionario = bitarray()
        self.letras = bitarray()
    #Tabla de frecuencia
    def frecuencia(self):
        abecedario = [0]*130
        for i in self.text:
            abecedario[ord(i)] += 1
        self.abc = abecedario
        return
    #Dfs para asignar la letra a cada nodo y sacar su representacion binaria
    def dfs(self, nodo, binario):
        if nodo.left is None and nodo.right is None:
            self.code[ord(nodo.value)] = binario
            return
        if nodo.left is not None:
            self.dfs(nodo.left, binario+"0")
        if nodo.right is not None:
            self.dfs(nodo.right, binario+"1")
        return
    #Convertir el arreglo de hojas, o de letras en orden, a un bitarray para que sea mas pequeño
    def convertir(self):
        for i in self.leaves:
            self.letras.extend(bitarray(format(ord(i), '07b')))
    #Nueva funcion bfs, para guardar el arbol de huffman en 2nbits por cada n nodos
    def bfs(self, nodo):
        queue = []
        queue.append(nodo)
        while queue:
            s = queue.pop(0)
            if s.value is not None:
                self.leaves.append(s.value)

            if s.left is not None:
                self.diccionario.extend(bitarray('1'))
                queue.append(s.left)
            else:
                self.diccionario.extend(bitarray('0'))

            if s.right is not None:
                self.diccionario.extend(bitarray('1'))
                queue.append(s.right)
            else:
                self.diccionario.extend(bitarray('0'))
        self.convertir()
    #Funcion de encoding del huffman, usando bitarrays para que sea mas comprimido, tal cual se vio en clase
    def encoding(self):
        self.code = [bitarray()] * 130
        self.frecuencia()
        arreglo = []
        for i in range(130):
            if self.abc[i] != 0:
                arreglo.append((self.abc[i], chr(i)))
        heap = MinHeap()
        heap.build_heap(arreglo)
        while heap.size > 1:
            a = heap.pop()
            b = heap.pop()
            if a.key == b.key and (b.value is None or a.value is None or (ord(b.value) <= ord(a.value))):
                heap.insert((a.key + b.key), None, b, a)
            else:
                heap.insert((a.key + b.key), None, a, b)
        self.tree = heap.peek()
        if self.tree.left is None and self.tree.right is None:
            self.dfs(heap.pop(), bitarray('1'))
        else:
            self.dfs(heap.pop(), bitarray())
        codificacion = bitarray()
        for i in self.text:
            codificacion += self.code[ord(i)]
        self.bfs(self.tree)
        self.encoded = self.diccionario + self.letras + codificacion
        return
#Decompresor huffman
class DHuffman:
    def __init__(self, compress):
        self.com = compress
        self.cabeza = None
        self.decoded = ""
    #Convertir cadena en un numero
    def to_num(self, string):
        number = 0
        pot = 64
        for i in string:
            if i=="1":
                number += pot
            pot = int(pot//2)
        return number
    #Funcion para decodificar, donde leemos el primer texto escrito en binario y reconstruimos el arbol primero
    def decoding(self):
        x = HeapNode(0)
        self.cabeza = x
        queue = []
        queue.append(self.cabeza)
        c = 0
        hojas = 0
        #Reconstruccion del arbol con una bfs
        while queue:
            s = queue.pop(0)
            if self.com[c] == 1:
                s.left = HeapNode(0)
                queue.append(s.left)
            if self.com[c+1] == 1:
                s.right = HeapNode(0)
                queue.append(s.right)
            if self.com[c] == 0 and self.com[c+1] == 0:
                hojas += 1
            c += 2
        c2 = 0
        queue.append(self.cabeza)
        #Asignacion de las hojas en la bfs, para tener el arbol huffman completo como antes
        while queue:
            s = queue.pop(0)
            if s.left is not None:
                queue.append(s.left)
            if s.right is not None:
                queue.append(s.right)

            if self.com[c2] == 0 and self.com[c2+1] == 0:
                aux = ""
                for i in range(7):
                    if self.com[c+i]==1:
                        aux += '1'
                    else:
                        aux += '0'
                c += 7
                s.value = chr(self.to_num(aux))
                hojas -= 1
            c2 += 2
        #La descompresion huffman vista, para saber que letra es el codigo que leemos
        nodo = self.cabeza
        for i in range(c, len(self.com)):
            if self.com[i] == 0 and nodo.left is not None:
                nodo = nodo.left
            elif self.com[i] == 1 and nodo.right is not None:
                nodo = nodo.right
            if nodo.left is None and nodo.right is None:
                self.decoded += nodo.value
                nodo = self.cabeza
#Otro metodo de compresion, pero al trabajar con bits y patrones no largos, decidimos no usarlo ya que el final resultaba mas largo y no era comprimirlo
class RLE:
    def __init__(self, texto):
        self.text = texto
        self.tam = len(texto)
        self.final = ""
    
    def compresor(self):
        i = 0
        while i<(self.tam-1):
            contador = 1
            while i<(self.tam-1) and self.text[i] == self.text[i+1]:
                contador += 1
                i += 1
            i += 1
            self.final += chr(self.text[i-1])
            self.final += str(contador)
#Otra clase de compresion, donde vamos guardando patrones que no hayan ocurrido antes, y los vamos guardando para usar menos bits en codificar, pero no vimos el contexto en que serviria mejor que huffman
class LZW:
    def __init__(self, texto):
        self.text = texto
        self.tam = len(texto)
        self.code = []
    
    def comprimir(self):
        i=0
        p = self.texto[i]
        while i<(self.tam-1):
            j=self.texto[i+1]
            nuevo = p+j
            if nuevo in self.code:
                p = nuevo
            else:
                self.code.append(nuevo)
#Interfaz con Tk, para mejor funcionamiento
class Interfaz:
    def __init__(self, master):
        #Titulo de la ventana
        self.master = master
        self.master.title("FILES COMPRESSOR AND DECOMPRESSORS")
        
        #Pantalla completa
        width, height = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
        self.master.geometry(f"{width}x{height}")

        #Mensaje de bienvenida
        msj_bienvenida = tk.Label(self.master, text="WELCOME TO THE FILE COMPRESSOR \"SEX.ZIP\"", font=("Times", int(height//20)))
        msj_bienvenida.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        
        #Mensaje de archivo a adjuntar
        self.msj_agregado = tk.Label(self.master, text="NO ATTACHMENT", font=("Times", int(height//50)))
        self.msj_agregado.pack(pady=10)
        self.msj_agregado.place(relx=0.5, rely=0.28, anchor=tk.CENTER)
        
        #Boton para adjuntar archivo
        self.b_agregar = tk.Button(self.master, text="SEARCH", command=self.boton_agregar, font=("Times", int(height//60)))
        self.b_agregar.pack(pady=10)
        self.b_agregar.place(relx=0.5, rely=0.33, anchor=tk.CENTER)

        #Cuadricula para los botones
        self.cuadricula = tk.Frame(self.master)
        self.cuadricula.place(relx=0.5, rely=0.62, anchor=tk.CENTER)
        #Botones para asignar a cada accion
        self.b1 = tk.Button(self.cuadricula, text=str("COMPRESS TEXT"), font=("Times", int(height//60)), width=20, height=4, command=self.comprimir_texto)
        self.b1.grid(row=0, column=0, padx=5, pady=5)
        self.b2 = tk.Button(self.cuadricula, text=str("COMPRESS IMAGE"), font=("Times", int(height//60)), width=20, height=4, command = self.comprimir_imagen)
        self.b2.grid(row=0, column=1, padx=5, pady=5)
        self.b3 = tk.Button(self.cuadricula, text=str("COMPRESS AUDIO"), font=("Times", int(height//60)), width=20, height=4, command = self.comprimir_audio)
        self.b3.grid(row=0, column=2, padx=5, pady=5)
        self.b4 = tk.Button(self.cuadricula, text=str("COMPRESS VIDEO"), font=("Times", int(height//60)), width=20, height=4, command = self.comprimir_video)
        self.b4.grid(row=0, column=3, padx=5, pady=5)
        self.b5 = tk.Button(self.cuadricula, text=str("DECOMPRESS TEXT"), font=("Times", int(height//60)), width=20, height=4, command=self.descomprimir_texto)
        self.b5.grid(row=1, column=0, padx=5, pady=5)
        self.b6 = tk.Button(self.cuadricula, text=str("DECOMPRESS IMAGE"), font=("Times", int(height//60)), width=20, height=4, command = self.descomprimir_imagen)
        self.b6.grid(row=1, column=1, padx=5, pady=5)
        self.b7 = tk.Button(self.cuadricula, text=str("DECOMPRESS AUDIO"), font=("Times", int(height//60)), width=20, height=4, command = self.descomprimir_audio)
        self.b7.grid(row=1, column=2, padx=5, pady=5)
        self.b8 = tk.Button(self.cuadricula, text=str("DECOMPRESS VIDEO"), font=("Times", int(height//60)), width=20, height=4, command = self.descomprimir_video)
        self.b8.grid(row=1, column=3, padx=5, pady=5)

        # Mensaje "ADIOS" centrado en la parte inferior derecha
        self.msj_final = tk.Label(self.master, text="GOODBYE, SEE YOU SOON!", font=("Times", int(height//35)))
        self.msj_final.place(relx=0.5, rely=0.85, anchor=tk.CENTER)
    #Funcionamiento para agregar un archivo, y guardar su nombre
    def boton_agregar(self):
        file_path = filedialog.askopenfilename(title="SELECT FILE")
        if file_path:
            self.msj_agregado.config(text=f"{file_path}")
            self.msj_agregado = file_path
    #Boton asignado para comprimir texto, recibiendo la direccion del archivo txt
    def comprimir_texto(self):
        extension = self.msj_agregado[len(self.msj_agregado)-3:]
        #Si la extension no es txt, no deja avanzar
        if extension != "txt":
            self.msj_final.config(text = "IT'S NOT POSSIBLE TO COMPRESS THAT EXTENSION")
            return
        mensaje = "FILE COMPRESSED SUCCESSFULLY, HAVE A NICE DAY!"
        #Nuevo nombre para hacerlo binario
        nombre_binario = self.msj_agregado[:-3] + "bin"
        #Lee el archivo txt
        try:
            with open(self.msj_agregado, "r") as file:
                texto = file.read()
        except FileNotFoundError:
            mensaje = "THERE'S NO SUCH FILE"
            self.msj = mensaje
            return
        #Termina si el archivo esta vacio
        if texto == "":
            self.msj_final.config(text = "FILE EMPTY, NOT POSSIBLE")
            return
        #Comprimimos usando Huffman modificado
        A = CHuffman(texto)
        A.encoding()
        comprimido = A.encoded
        #Lo escribimos en binario "hola.bin"
        with open(nombre_binario, "wb") as file:
            file.write(comprimido)
        self.msj_final.config(text = mensaje)
    #Descomprimimos un texto desde un archivo tipo bin, usando DHuffman modificado
    def descomprimir_texto(self):
        extension = self.msj_agregado[len(self.msj_agregado)-3:]
        #Si no es tipo bin, ahi termina
        if extension != "bin":
            self.msj_final.config(text = "IT'S NOT POSSIBLE TO DECOMPRESS THAT EXTENSION")
            return
        mensaje = "FILE DECOMPRESSED SUCCESSFULLY, HAVE A NICE DAY!"
        #Nuevo nombre con extension de texto
        nombre_texto = self.msj_agregado[:-3] + "txt"
        #La leemos en binario con un bitarray para no aumentar el tamaño
        try:
            with open(self.msj_agregado, "rb") as file:
                bits = bitarray()
                bits.fromfile(file)
        except FileNotFoundError:
            mensaje = "THERE'S NO SUCH FILE"
            self.msj = mensaje
            return
        if len(bits) == 0:
            self.msj_final.config(text = "FILE EMPTY, NOT POSSIBLE")
            return
        #Decodificamos con DHuffman
        A = DHuffman(bits)
        A.decoding()
        descomprimido = A.decoded
        #Lo escribimos con un w normal de texto
        with open(nombre_texto, "w") as file:
            file.write(descomprimido)
        self.msj_final.config(text = mensaje)
    #Funcion para comprimir una imagen, similar a texto pero verificando que sea de tipo bmp
    def comprimir_imagen(self):
        extension = self.msj_agregado[len(self.msj_agregado)-3:]
        if extension != "bmp":
            self.msj_final.config(text = "IT'S NOT POSSIBLE TO COMPRESS THAT EXTENSION")
            return
        mensaje = "FILE COMPRESSED SUCCESSFULLY, HAVE A NICE DAY!"
        nombre_binario = self.msj_agregado[:-3] + "bin"
        #Leemos el archivo en binario
        try:
            with open(self.msj_agregado, "rb") as file:
                textob = file.read()
        except FileNotFoundError:
            mensaje = "THERE'S NO SUCH FILE"
            self.msj = mensaje
            return
        if textob == "":
            self.msj_final.config(text = "FILE EMPTY, NOT POSSIBLE")
            return
        #Lo convertimos a texto para usar Huffman
        texto = ''.join(format(byte, '08b') for byte in textob)
        #Usamos huffman
        A = CHuffman(texto)
        A.encoding()
        comprimido = A.encoded
        #Lo escribimos en binario con extension bin
        with open(nombre_binario, "wb") as file:
            file.write(comprimido)
        self.msj_final.config(text = mensaje)
    #Funcion para descomprimir el archivo bmp de un binario
    def descomprimir_imagen(self):
        extension = self.msj_agregado[len(self.msj_agregado)-3:]
        if extension != "bin":
            self.msj_final.config(text = "IT'S NOT POSSIBLE TO DECOMPRESS THAT EXTENSION")
            return
        mensaje = "FILE DECOMPRESSED SUCCESSFULLY, HAVE A NICE DAY!"
        nombre_texto = self.msj_agregado[:-3] + "txt"
        try:
            with open(self.msj_agregado, "rb") as file:
                bits = bitarray()
                bits.fromfile(file)
        except FileNotFoundError:
            mensaje = "THERE'S NO SUCH FILE"
            self.msj = mensaje
            return
        if len(bits) == 0:
            self.msj_final.config(text = "FILE EMPTY, NOT POSSIBLE")
            return
        nombre_text = self.msj_agregado[:-3] + "bmp"  # Ajusta la extensión según el formato original
        #Descomprimimos con DHuffman
        A = DHuffman(bits)
        A.decoding()
        descomprimido = A.decoded
        #Convertimos la string de descomprimido a uno en bits
        descomprimidob = ''.join(format(ord(char), '08b') for char in descomprimido)
        #Lo escribimos convertido a bitarray, para escribirlo en binario, solamente que no deja abrirlo en archivos
        with open(nombre_text, "wb") as file:
            file.write(bitarray(descomprimidob))
            #descomprimidob.tofile(file)
        self.msj_final.config(text = mensaje)
    #Ahora vamos a comprimir un audio, con otra tecnica
    def comprimir_audio(self):
        extension = self.msj_agregado[len(self.msj_agregado)-3:]
        #Solamente con la extension wav
        if extension != "wav":
            self.msj_final.config(text = "IT'S NOT POSSIBLE TO COMPRESS THAT EXTENSION")
            return
        mensaje = "FILE COMPRESSED SUCCESSFULLY, HAVE A NICE DAY!"
        nombre_binario = self.msj_agregado[:-3] + "bin"
        #Leemos los frames del audio en binario, usando getnframes
        try:
            with wave.open(self.msj_agregado, "rb") as file:
                audio = file.readframes(file.getnframes())
        except FileNotFoundError:
            mensaje = "THERE'S NO SUCH FILE"
            self.msj = mensaje
            return
        #Formamos el texto para poder comprimirlo despues
        texto = ""
        #Por cada parte en el audio...
        for parte in audio:
            #Sacamos el valor de esa parte, convirtiendo el byte a entero
            valor = struct.unpack("<h", parte)[0]
            #Ahora convertimos el entero a caracter
            caracter = chr(valor)
            #Y finalmente sumamos el caracter al texto a comprimir
            texto += caracter
        A = CHuffman(texto)
        A.encoding()
        comprimido = A.encoded

        with open(nombre_binario, "wb") as file:
            file.write(comprimido)
        self.msj_final.config(text = mensaje)

    def descomprimir_audio(self):
        pass
    #Ahora vamos a comprimir video
    def comprimir_video(self):
        extension = self.msj_agregado[len(self.msj_agregado)-3:]
        #Limitamos a comprimir solamente la extension wmv
        if extension != "wmv":
            self.msj_final.config(text = "IT'S NOT POSSIBLE TO COMPRESS THAT EXTENSION")
            return
        mensaje = "FILE COMPRESSED SUCCESSFULLY, HAVE A NICE DAY!"
        nombre_binario = self.msj_agregado[:-3] + "bin"
        #Leemos en binario
        try:
            with open(self.msj_agregado, "rb") as file:
                textob = file.read()
        except FileNotFoundError:
            mensaje = "THERE'S NO SUCH FILE"
            self.msj = mensaje
            return
        if textob == "":
            self.msj_final.config(text = "FILE EMPTY, NOT POSSIBLE")
            return
        #Convertimos el byte en texto
        texto = ''.join(format(byte, '08b') for byte in textob)
        #Comprimimos el texto
        A = CHuffman(texto)
        A.encoding()
        comprimido = A.encoded
        #Finalmente escribimos en binario
        with open(nombre_binario, "wb") as file:
            file.write(comprimido)
        self.msj_final.config(text = mensaje)

    def descomprimir_video(self):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = Interfaz(root)
    root.mainloop()
