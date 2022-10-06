import csv
import time
import tkinter
from tkinter import filedialog
from collections import deque
import queue
import pygame, sys



RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165 ,0)
TURQUOISE = (64, 224, 208)


###CLASES NECESARIAS###
class Boton(object):
    def __init__(self, x, y, texto):
        self.nombre = texto
        self.rect = pygame.Rect(x,y,120,40)
        self.oprimido = False

    def oprimir(self):
        hacer_accion = False
        #Revisa posición del mouse
        pos = pygame.mouse.get_pos()
        #Revisa si el mouse hha hecho click en el botón
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]==1 and self.oprimido == False:
                self.oprimido = True
                hacer_accion = True
        #Reinicia el botón
        if pygame.mouse.get_pressed()[0]==0:
            self.oprimido = False

        return hacer_accion

###FUNCIONES###
##FUNCIONES DE CREACIÓN DEL LABERINTO##

#Crea la matriz del laberinto a partir del csv#
def matriz_lab(path):
    matriz_lab = []
    with open(path) as lab_csv:
        lector = csv.reader(lab_csv, delimiter=',')
        for line in lector:
            if(len(line)>0):
                matriz_lab.append(line)
    return matriz_lab

#Pide la ruta del csv del laberinto al usuario
def pedir_lab():
    tkinter.Tk().withdraw()
    path_csv = filedialog.askopenfilename()
    return matriz_lab(path_csv)

##FUNCIONES DE LA INTERFAZ DE USUSARIO##

##Dibujar botones
def dibujar_boton(ventana,boton):
    pygame.draw.rect(ventana,(230,150,70),boton.rect)
    texto_boton = fuente.render(boton.nombre,20,(0,0,0))
    screen.blit(texto_boton,(boton.rect.left+35,boton.rect.top+15))
    accion = boton.oprimir()
    return accion

def mostrar_laberinto(ventana,laberinto):
    w,h=ventana.get_size()
    filas=len(laberinto)
    cols=len(laberinto[0])
    ancho_cuadrado=int(w/cols)
    alto_cuadrado=int(h/filas)
    colores = (0,0,0)
    x_pos=0
    y_pos=0
    for lines in laberinto:
        x_pos=0
        for element in lines:
            if element == "c":
                colores = WHITE
            if element == "w":
                colores = BLACK
            if lines == laberinto[0] and element == "c":
                    colores = ORANGE 
            if lines == laberinto[len(laberinto)-1] and element == "c":
                    colores = TURQUOISE 
            if element == "e":
                    colores = GREEN                     
            pygame.draw.rect(ventana,colores,(x_pos,y_pos,ancho_cuadrado,alto_cuadrado))
            #print(element,w,h,filas,cols,ancho_cuadrado,alto_cuadrado,x_pos,y_pos, colores)
            x_pos+=ancho_cuadrado
        y_pos+=alto_cuadrado

##FUNCIONES DE NODOS##

##Enumerar nodos
def enum_nodo(laberinto, i, j):
    return(i*len(laberinto)+j)

##obtener coordenadas
def coordenadas(laberinto,nodo):
    i = nodo//len(laberinto[0])
    j = nodo%len(laberinto[0])
    return[i,j]
##Expandir nodo
def expandir_nodo(laberinto, nodo):
    i,j = coordenadas(laberinto,nodo)
    nodosHijo = []

    # Revisión de los nodos hijo en orden NESW
    if(i-1>=0 and laberinto[i-1][j]!="w"):
        nodosHijo.append(enum_nodo(laberinto,i-1,j))

    if(j+1<len(laberinto[i]) and laberinto[i][j+1]!="w"):
        nodosHijo.append(enum_nodo(laberinto,i,j+1))

    if(i+1<len(laberinto) and laberinto[i+1][j]!="w"):
        nodosHijo.append(enum_nodo(laberinto,i+1,j))

    if(j-1>=0 and laberinto[i][j-1]!="w"):
        nodosHijo.append(enum_nodo(laberinto,i,j-1))

    return nodosHijo

##Buscar nodo en al frontera
def nodo_en_frontera(frontera,nodo):
    for elem in frontera:
        if nodo == elem:
            return True
    return False

##Encontrar entrada
def encontrar_entrada(laberinto):
    entrada=laberinto[0].index("c")
    return entrada

##Devolver la matriz laberinto con el camino
def matriz_lab_final(laberinto,camino): 
    laberinto_l=[]  
    for fila in laberinto:
        for i in fila:
            laberinto_l.append(i)
    for pos in camino:
        laberinto_l[pos]="e"
    laberinto=[laberinto_l[i:i + len(laberinto)] for i in range(0, len(laberinto_l), len(laberinto))]
    return laberinto

##DFS
def buscar_dfs(laberinto):
    nodo_inicial = encontrar_entrada(laberinto)
    nodo_objetivo = enum_nodo(laberinto,len(laberinto)-1,len(laberinto[0])-2)
    nodo_actual = nodo_inicial
    camino = [nodo_inicial]

    frontera = deque()
    frontera.append(camino)
    visitado = camino
    caminos_encontrados = [camino]
    #print(nodo_inicial,nodo_objetivo, camino, frontera,visitado,caminos_encontrados)

    if(nodo_actual==nodo_objetivo):
        return camino

    while frontera:
        camino = frontera.pop()
        hijos = expandir_nodo(laberinto,camino[-1])
        #print(camino, hijos)
        if(len(hijos)>0):
            for hijo in hijos:
                nuevo_camino = camino + [hijo]
                #print(nuevo_camino)
                #print(hijo)
                if(hijo==nodo_objetivo):
                    visitado.append(hijo)
                    caminos_encontrados.append(nuevo_camino)
                    #print("found it")
                    return nuevo_camino
                #print(not nodo_en_frontera(visitado,hijo))
                if(not nodo_en_frontera(visitado,hijo)):
                    #print(visitado)
                    visitado.append(hijo)
                    caminos_encontrados.append(nuevo_camino)
                    frontera.append(nuevo_camino)
                    #print(frontera)
                #print(visitado)
    return 0

##Búsqueda iterativa
def buscar_ids(laberinto):
    nodo_inicial = encontrar_entrada(laberinto)
    nodo_objetivo = enum_nodo(laberinto,len(laberinto)-1,len(laberinto[0])-2)
    nodo_actual = nodo_inicial
    camino = [nodo_inicial]

    frontera = deque()
    frontera.append(camino)
    visitado = camino
    caminos_encontrados = [camino]

    if(camino == nodo_objetivo):
        return camino

    profundidad = 3
    valores_n = {}
    valores_n[nodo_actual] = 0
    altura = 0

    while frontera:

        camino = frontera.pop()
        nodo_actual = camino[-1]
        hijos = expandir_nodo(laberinto, camino[-1])

        if(len(hijos)>0):
            for hijo in hijos:
                nuevo_camino = camino + [hijo]
                valores_n[hijo] = valores_n[nodo_actual] + 1

                if(hijo == nodo_objetivo):
                    visitado.append(hijo)
                    caminos_encontrados.append(nuevo_camino)
                    return nuevo_camino

                if not nodo_en_frontera(visitado, hijo):
                    caminos_encontrados.append(nuevo_camino)
                    visitado.append(hijo)
                    if valores_n[hijo] <= altura:
                        frontera.append(nuevo_camino)
                    else:
                        frontera.appendleft(nuevo_camino)

                else:
                    valores_n.pop(hijo)

            valores_n.pop(nodo_actual)
        if valores_n[min(valores_n, key=valores_n.get)] == altura+1 :
            altura+= profundidad


##Busqueda uniforme
def busqueda_uniforme(laberinto):
    nodo_inicial = encontrar_entrada(laberinto)
    nodo_objetivo = enum_nodo(laberinto,len(laberinto)-1,len(laberinto[0])-2)
    nodo_actual = nodo_inicial
    camino = [nodo_inicial]

    frontera = deque()
    frontera.append(camino)
    visitado = camino
    caminos_encontrados = [camino]

    pesos_hijos = {}
    pesos_hijos[nodo_actual] = 0

    if(nodo_actual == nodo_objetivo):
        return camino

    while frontera:
        camino = frontera.pop()
        nodo_actual = camino[-1]
        hijos = expandir_nodo(laberinto, camino[-1])

        if(len(hijos)>0):
            for hijo in hijos:
                nuevo_camino = camino + [hijo]
                peso = pesos_hijos[camino[-1]]
                peso += 1
                pesos_hijos[hijo] = peso

                if(hijo == nodo_objetivo):
                    visitado.append(hijo)
                    caminos_encontrados.append(nuevo_camino)
                    return nuevo_camino

                if nodo_en_frontera(visitado, hijo):
                    del pesos_hijos[hijo]

                if not nodo_en_frontera(visitado, hijo):
                    caminos_encontrados.append(nuevo_camino)
                    visitado.append(hijo)
                    frontera.append(nuevo_camino)
            del pesos_hijos[nodo_actual]

            nodo_sig = min(pesos_hijos, key=pesos_hijos.get)
            copia=frontera.copy()

            for c in copia:
                lpath=c[-1]
                if lpath==nodo_sig:
                    frontera.remove(c)
                    frontera.append(c)


def busqueda_BFS(laberinto):
    nodo_inicial = encontrar_entrada(laberinto)
    nodo_objetivo = enum_nodo(laberinto,len(laberinto) - 1 ,len(laberinto[0])-2)
    nodo_actual = nodo_inicial
    camino = [nodo_inicial]

    frontera_queue = deque()
    frontera_queue.append(camino)
    visitado = camino
    caminos_encontrados = [camino]

    if(camino[-1] == nodo_objetivo):
        return camino

    while queue:
        camino = frontera_queue.popleft()
        hijos = expandir_nodo(laberinto, camino[-1])
        if(len(hijos)>0):
            for hijo in hijos:
                nuevo_camino = camino + [hijo]
                if(hijo == nodo_objetivo):
                    visitado.append(hijo)
                    caminos_encontrados.append(nuevo_camino)
                    return nuevo_camino
                if(not nodo_en_frontera(visitado, hijo)):
                    caminos_encontrados.append(nuevo_camino)
                    visitado.append(hijo)
                    frontera_queue.append(nuevo_camino)

###PROGRAMA PRINCIPAL###

laberinto,laberinto_ini=[],[]
pygame.init()

#Crear la ventana y fuente para el texto
screen_width = 800
screen_heigth = 600
lab_width = 500
lab_height = 500
screen = pygame.display.set_mode((screen_width,screen_heigth))
pygame.display.set_caption('Maze Solver')
fuente = pygame.font.Font(None,20)
laberinto_grafico = pygame.Surface((lab_width,lab_height))

#Crear botones de la interfaz
boton_DFS = Boton(20,20,"DFS")
boton_BFS = Boton(20,70,"BFS")
boton_IDS = Boton(20,120,"IDS")
boton_UCS = Boton(20,170,"UCS")
boton_GREEDY = Boton(20,220,"GREEDY")
boton_ASTAR = Boton(20,270,"A*")
boton_SELECCIONAR_LABERINTO = Boton(20,320,"SELECCIONAR LABERINTO")
boton_RESET = Boton(20,370,"REINICIAR")
boton_EXIT = Boton(20,420,"SALIR")

recto=pygame.Rect(0,0,10,10)
salir = False
while not salir:
    screen.fill((202,228,241))
    if laberinto:
        mostrar_laberinto(laberinto_grafico,laberinto)
    screen.blit(laberinto_grafico,(250,50))
    if dibujar_boton(screen,boton_DFS):
        print("DFS")
        camino=buscar_dfs(laberinto)
        laberinto = matriz_lab_final(laberinto,camino)
        continue
    if dibujar_boton(screen,boton_BFS):
        print("BFS")
        camino=busqueda_BFS(laberinto)
        laberinto = matriz_lab_final(laberinto,camino)
        continue        
    if dibujar_boton(screen,boton_IDS):
        print("IDS")
        camino=buscar_ids(laberinto)
        laberinto = matriz_lab_final(laberinto,camino)
        continue        
    if dibujar_boton(screen,boton_UCS):
        print("UCS")
        camino=busqueda_uniforme(laberinto)
        laberinto = matriz_lab_final(laberinto,camino)
        continue        
    if dibujar_boton(screen,boton_GREEDY):
        print("GREEDY")
    if dibujar_boton(screen,boton_ASTAR):
        print("A*")
    if dibujar_boton(screen,boton_SELECCIONAR_LABERINTO):
        print("SELECCIONAR LABERINTO")
        laberinto=pedir_lab()
        laberinto_ini=laberinto
    if dibujar_boton(screen,boton_RESET):
        print("RESTAURAR LABERINTO")        
        laberinto=laberinto_ini
    if dibujar_boton(screen,boton_EXIT):
        salir = True
    for event in pygame.event.get():
        #print(event)
        if event.type == pygame.QUIT:
            salir = True

        pygame.display.update()
pygame.quit()
