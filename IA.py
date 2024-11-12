import pygame
import sys
import heapq
import random
from collections import deque
from boton import Button

# Inicializar Pygame
pygame.init()

# Definir los colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)

FONT = 'font/minecraft_font.ttf'

# Dimensiones de la ventana
ANCHO_VENTANA = 600
ALTO_VENTANA = 600
TAMANO_CELDA = 100  # Cada celda será de 100x100 píxeles
FILAS = 6
COLUMNAS = 6

# Crear la ventana
ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Pacman Univalle - LUCHITO Y VARGAS")

# Reloj para controlar la velocidad de fotogramas
reloj = pygame.time.Clock()

# Cargar imágenes de personajes
imagen_rene = pygame.image.load("imagenes/rana.jpeg")
imagen_piggy = pygame.image.load("imagenes/piggy.jpeg")
imagen_elmo = pygame.image.load("imagenes/elmo.jpeg")
imagen_galleta = pygame.image.load("imagenes/galleta.jpeg")
imagen_rana_elmo = pygame.image.load("imagenes/ranayelmo.jpeg")
imagen_rana_galleta = pygame.image.load("imagenes/rene_come_galleta.jpeg")

# Escalar las imágenes al tamaño adecuado
imagen_rene = pygame.transform.scale(imagen_rene, (TAMANO_CELDA, TAMANO_CELDA))
imagen_piggy = pygame.transform.scale(imagen_piggy, (TAMANO_CELDA, TAMANO_CELDA))
imagen_elmo = pygame.transform.scale(imagen_elmo, (TAMANO_CELDA, TAMANO_CELDA))
imagen_galleta = pygame.transform.scale(imagen_galleta, (TAMANO_CELDA, TAMANO_CELDA))
imagen_rana_elmo = pygame.transform.scale(imagen_rana_elmo, (TAMANO_CELDA, TAMANO_CELDA))  
imagen_rana_galleta = pygame.transform.scale(imagen_rana_galleta, (TAMANO_CELDA, TAMANO_CELDA))

# MAPAS
mapa1 = [
    [' ', ' ', ' ', '#', ' ', 'E'],
    ['#', '#', ' ', '#', ' ', '#'],
    [' ', 'G', ' ', ' ', ' ', ' '],
    [' ', '#', '#', ' ', '#', ' '],
    [' ', ' ', ' ', ' ', ' ', ' '],
    ['R', ' ', '#', ' ', 'P', ' ']
]

mapa2 = [
    ['#', ' ', ' ', ' ', ' ', 'E'],
    ['#', '#', '#', '#', ' ', '#'],
    [' ', ' ', 'G', '#', ' ', ' '],
    [' ', '#', ' ', ' ', ' ', ' '],
    ['#', ' ', '#', '#', '#', ' '],
    ['R', ' ', ' ', ' ', 'P', ' ']
]

mapa3 = [
    [' ', '#', ' ', '#', ' ', 'E'],
    [' ', ' ', ' ', '#', ' ', '#'],
    ['#', ' ', ' ', 'G', ' ', ' '],
    [' ', '#', '#', ' ', '#', ' '],
    [' ', ' ', ' ', ' ', ' ', ' '],
    ['R', ' ', '#', ' ', 'P', ' ']
]

# Lista de mapas
mapas = [mapa1, mapa2, mapa3]
laberinto = mapas[0]  # Inicializa el laberinto con el primer mapa
en_seleccion_mapa = False  # Agrega esta línea para inicializar la variable
mapa_actual = 0  # Inicializa el mapa actual

def obtener_posicion(laberinto):
    posiciones = {
        'rene': None,
        'elmo': None,
        'piggy': None,
        'galleta': None
    }
    for fila in range(len(laberinto)):
        for columna in range(len(laberinto[fila])):
            if laberinto[fila][columna] == 'R':
                posiciones['rene'] = (fila, columna)
            elif laberinto[fila][columna] == 'E':
                posiciones['elmo'] = (fila, columna)
            elif laberinto[fila][columna] == 'P':
                posiciones['piggy'] = (fila, columna)
            elif laberinto[fila][columna] == 'G':
                posiciones['galleta'] = (fila, columna)
    return posiciones

# Inicializar las posiciones
posiciones = obtener_posicion(laberinto)


# Movimientos posibles: arriba, abajo, izquierda, derecha
movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Función para comprobar si una posición está dentro de los límites del laberinto
def es_valida(fila, columna, laberinto):
    return 0 <= fila < len(laberinto) and 0 <= columna < len(laberinto[0]) and laberinto[fila][columna] != '#'

# Función para dibujar el laberinto
def dibujar_laberinto(ventana, laberinto):
    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            celda = laberinto[fila][columna]
            if celda == '#':  # Obstáculo
                pygame.draw.rect(ventana, NEGRO, 
                                 (columna * TAMANO_CELDA, fila * TAMANO_CELDA, 
                                  TAMANO_CELDA, TAMANO_CELDA))
            elif celda == 'R':  # René
                ventana.blit(imagen_rene, (columna * TAMANO_CELDA, fila * TAMANO_CELDA))
            elif celda == 'P':  # Piggy
                ventana.blit(imagen_piggy, (columna * TAMANO_CELDA, fila * TAMANO_CELDA))
            elif celda == 'E':  # Elmo
                ventana.blit(imagen_elmo, (columna * TAMANO_CELDA, fila * TAMANO_CELDA))
            elif celda == 'G':  # Galleta
                ventana.blit(imagen_galleta, (columna * TAMANO_CELDA, fila * TAMANO_CELDA))
            else:  # Espacio vacío
                pygame.draw.rect(ventana, BLANCO, 
                                 (columna * TAMANO_CELDA, fila * TAMANO_CELDA, 
                                  TAMANO_CELDA, TAMANO_CELDA))
            pygame.draw.rect(ventana, NEGRO, 
                             (columna * TAMANO_CELDA, fila * TAMANO_CELDA, 
                              TAMANO_CELDA, TAMANO_CELDA), 1)

#FUNCION DE PROFUNDIDAD LIMITADA PARA RENE
def busqueda_profundidad_limitada(laberinto, inicio, objetivo, max_profundidad):
    # Algoritmo de DFS Limitado usando una lista para almacenar las posiciones visitadas
    def dls(posicion_actual, objetivo, profundidad_actual, visitados):
        # Si alcanzamos el límite de profundidad, no buscamos más
        if profundidad_actual >= limite_profundidad:
            return None
        
        # Si encontramos el objetivo, devolvemos el camino
        if posicion_actual == objetivo:
            return [posicion_actual]
        
        # Agregar la posición actual a los visitados
        visitados.append(posicion_actual)

        # Inicializar el nodo en el árbol (opcional, solo para depuración)
        if posicion_actual not in arbol:
            arbol[posicion_actual] = []

        # Explorando movimientos posibles
        for movimiento in movimientos:
            nueva_fila = posicion_actual[0] + movimiento[0]
            nueva_columna = posicion_actual[1] + movimiento[1]
            nuevo_estado = (nueva_fila, nueva_columna)

            # Verifica que la nueva posición sea válida y no sea un estado ya visitado
            if es_valida(nueva_fila, nueva_columna, laberinto) and nuevo_estado not in visitados:
                # Agregar el nuevo estado al árbol de búsqueda
                arbol[posicion_actual].append(nuevo_estado)

                # Llamada recursiva con el nuevo estado
                resultado = dls(nuevo_estado, objetivo, profundidad_actual + 1, visitados)

                # Si encontramos un resultado, lo retornamos
                if resultado:
                    return [posicion_actual] + resultado
        
        # Eliminar la posición actual de visitados después de explorar
        visitados.pop()
        return None

    for limite_profundidad in range(1, max_profundidad + 1):
        visitados = []  # Reiniciar la lista de visitados para cada profundidad
        arbol = {}  # Solo para depuración, opcional
        resultado = dls(inicio, objetivo, 0, visitados)

        # Imprimir el árbol completo (opcional)
        print(f"Árbol completo para profundidad {limite_profundidad}:")
        for nodo, hijos in arbol.items():
            print(f"{nodo}: {hijos}")

        # Si se encuentra un resultado, retornarlo
        if resultado:
            return resultado  # Solo retornamos la lista de pasos

    return None  # Si no se encontró camino dentro del límite de profundidad

#FUNCION LIMITADA POR PROFUNDIDAD PARA PIGGY
def bfs_piggy(laberinto, posicion_piggy, posicion_rene):
    cola = deque()
    cola.append((posicion_piggy, []))  # Agrega la posición inicial y el camino vacío

    visitados = set()
    visitados.add(posicion_piggy)

    while cola:
        posicion_actual, camino_actual = cola.popleft()

        # Verifica si Piggy ha encontrado a René
        if posicion_actual == posicion_rene:
            
            return camino_actual  # Retorna el camino encontrado

        # Define los movimientos posibles (arriba, abajo, izquierda, derecha)
        movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # (dy, dx)

        for movimiento in movimientos:
            nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

            # Verificar que la nueva posición esté dentro de los límites y no sea un muro
            if (0 <= nueva_posicion[0] < len(laberinto) and
                0 <= nueva_posicion[1] < len(laberinto[0]) and
                laberinto[nueva_posicion[0]][nueva_posicion[1]] != "#" and
                nueva_posicion not in visitados):

                # Agregar nueva posición y actualizar camino
                visitados.add(nueva_posicion)
                cola.append((nueva_posicion, camino_actual + [nueva_posicion]))

    return None  # Si no se encuentra un camino


def heuristica(p1, p2):
    """ Calcula la distancia Manhattan entre dos puntos. """
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def a_estrella(laberinto, inicio, objetivo):
    """ Implementación del algoritmo A* con impresiones del camino explorado. """
    filas = len(laberinto)
    columnas = len(laberinto[0])
    abiertos = []
    heapq.heappush(abiertos, (0, inicio))
    came_from = {inicio: None}
    costo_acumulado = {inicio: 0}

    print("Iniciando búsqueda A* desde:", inicio)

    while abiertos:
        _, actual = heapq.heappop(abiertos)

        print(f"Explorando nodo {actual}")

        if actual == objetivo:
            # Reconstruir y mostrar el camino encontrado
            camino = []
            while actual:
                camino.append(actual)
                actual = came_from[actual]
            camino.reverse()
            
            # Mostrar camino final en pantalla
            print("Camino encontrado hacia el objetivo:", camino)
            return camino  # Retorna el camino encontrado

        # Generar vecinos
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Movimiento arriba, abajo, izquierda, derecha
            vecino = (actual[0] + dx, actual[1] + dy)
            if 0 <= vecino[0] < filas and 0 <= vecino[1] < columnas and laberinto[vecino[0]][vecino[1]] != '#':
                nuevo_costo = costo_acumulado[actual] + 1
                if vecino not in costo_acumulado or nuevo_costo < costo_acumulado[vecino]:
                    costo_acumulado[vecino] = nuevo_costo
                    prioridad = nuevo_costo + heuristica(vecino, objetivo)
                    heapq.heappush(abiertos, (prioridad, vecino))
                    came_from[vecino] = actual

                    # Mostrar en pantalla el nodo añadido a la lista abierta
                    print(f"Añadiendo {vecino} con prioridad {prioridad} a la lista de abiertos.")

    print("No se encontró un camino al objetivo.")
    return None  # Retorna None si no hay camino

def actualizar_camino_piggy(laberinto, posicion_piggy, posicion_rene):
    camino_actual = bfs_piggy(laberinto, posicion_piggy, posicion_rene)
    return camino_actual

def podar_arbol(arbol, camino_valido):
    arbol_podado = {}
    for i in range(len(camino_valido) - 1):
        nodo = camino_valido[i]
        siguiente_nodo = camino_valido[i + 1]
        arbol_podado[nodo] = [siguiente_nodo]
    return arbol_podado

# Función para mover los personajes 
comio_galleta = False
encontro_piggy = False

def mover_personaje(laberinto, camino, personaje, camino_piggy=None, posicion_rene=None, posicion_piggy=None):
    global comio_galleta, encontro_piggy, en_seleccion_mapa
    
    if personaje == 'P' and camino_piggy is not None:
        # Generar un número aleatorio entre 1 y 10 para decidir si usar A* o BFS
        cambio_algoritmo = random.randint(1, 10)

        # Si el número es menor a 4 (40% de probabilidad), usar A*
        if cambio_algoritmo <= 4:
            print(f"Turno: {cambio_algoritmo}. Usando A* para mover a Piggy.")
            camino_piggy = a_estrella(laberinto, posicion_piggy, posicion_rene)
        else:
            print(f"Turno: {cambio_algoritmo}. Usando BFS para mover a Piggy.")
            camino_piggy = bfs_piggy(laberinto, posicion_piggy, posicion_rene)

        # Usamos el nuevo camino calculado para mover a Piggy
        if camino_piggy:
            # Solo moveremos a Piggy si hay un camino válido
            paso_piggy = camino_piggy[0]
            fila, columna = paso_piggy

            # Limpiar la posición anterior de Piggy en el laberinto
            for fila_laberinto in range(len(laberinto)):
                for columna_laberinto in range(len(laberinto[0])):
                    if laberinto[fila_laberinto][columna_laberinto] == 'P':
                        laberinto[fila_laberinto][columna_laberinto] = ' '

            # Actualizar la posición de Piggy en el laberinto
            laberinto[fila][columna] = 'P'
            posicion_piggy = (fila, columna)

            # Dibujar el laberinto actualizado
            dibujar_laberinto(ventana, laberinto)
            ventana.blit(imagen_piggy, (columna * TAMANO_CELDA, fila * TAMANO_CELDA))
            pygame.display.flip()
            pygame.time.delay(500)

            # Verificar interacciones específicas de Piggy
            if (fila, columna) == posicion_rene:
                encontro_piggy = True
                ventana.blit(imagen_rana_elmo, (columna * TAMANO_CELDA, fila * TAMANO_CELDA))
                pygame.display.flip()
                mostrar_mensaje_interaccion_piggy()
                en_seleccion_mapa = True
                return posicion_piggy, camino_piggy  # Terminamos si Piggy encuentra a René

            return posicion_piggy, camino_piggy

    else:
        # Si es René, seguimos la lógica original de movimiento
        for paso in camino:
            # Comprobar que el paso sea una tupla de longitud 2
            if not isinstance(paso, tuple) or len(paso) != 2:
                print(f"Error: paso tiene un formato incorrecto: {paso}")
                continue  # Saltar este paso si no es válido

            fila, columna = paso

            # Limpiar la posición anterior del personaje en el laberinto
            for fila_laberinto in range(len(laberinto)):
                for columna_laberinto in range(len(laberinto[0])):
                    if personaje == 'R' and laberinto[fila_laberinto][columna_laberinto] == 'R':
                        laberinto[fila_laberinto][columna_laberinto] = ' '  # Limpiar posición anterior de René
                    elif personaje == 'P' and laberinto[fila_laberinto][columna_laberinto] == 'P':
                        laberinto[fila_laberinto][columna_laberinto] = ' '  # Limpiar posición anterior de Piggy

            # Actualizar la posición del personaje en el laberinto
            laberinto[fila][columna] = personaje

            # Actualizar la posición global
            if personaje == 'R':
                posicion_rene = (fila, columna)
            elif personaje == 'P':
                posicion_piggy = (fila, columna)

            # Dibujar el estado actual del laberinto
            dibujar_laberinto(ventana, laberinto)

            # Mostrar la imagen correspondiente
            if personaje == 'R':
                if comio_galleta:
                    ventana.blit(imagen_rana_galleta, (columna * TAMANO_CELDA, fila * TAMANO_CELDA))
                else:
                    ventana.blit(imagen_rene, (columna * TAMANO_CELDA, fila * TAMANO_CELDA))
            elif personaje == 'P':
                ventana.blit(imagen_piggy, (columna * TAMANO_CELDA, fila * TAMANO_CELDA))

            pygame.display.flip()
            pygame.time.delay(500)

            # Verificar interacciones específicas de René
            if personaje == 'R':
                # Verificar si René encontró la galleta
                if (fila, columna) == tuple(posicion_galleta):
                    comio_galleta = True
                    ventana.blit(imagen_rana_galleta, (columna * TAMANO_CELDA, fila * TAMANO_CELDA))
                    pygame.display.flip()
                    pygame.time.delay(500)
                    comio_galleta = False  # Restablecer la variable después de mostrar la imagen

                # Verificar si René encontró a Piggy
                if (fila, columna) == posicion_piggy:
                    encontro_piggy = True
                    ventana.blit(imagen_rana_elmo, (columna * TAMANO_CELDA, fila * TAMANO_CELDA))
                    pygame.display.flip()
                    mostrar_mensaje_interaccion_piggy()
                    en_seleccion_mapa = True  # Permitir selección de mapa tras interacción con Piggy
                    break

            # Redibujar la imagen original si le queda camino
            if personaje == 'R' and not comio_galleta:
                dibujar_laberinto(ventana, laberinto)
                ventana.blit(imagen_rene, (columna * TAMANO_CELDA, fila * TAMANO_CELDA))
                pygame.display.flip()

    return posicion_rene, camino  # Retorna la nueva posición de René o Piggy y el camino

# Función para mostrar mensaje de interacción con Piggy
def mostrar_mensaje_interaccion_piggy():
    global en_seleccion_mapa
    fuente = pygame.font.Font(FONT, 20)
    ventana.fill(BLANCO)
    mensaje = fuente.render("Piggy atrapo a Rene! Fin del juego.", True, VERDE)
    ventana.blit(mensaje, (100, 100))
    pygame.display.flip()
    pygame.time.delay(2000)  # Mostrar el mensaje por 2 segundos
    en_seleccion_mapa = True  # Permitir selección de mapa tras interacción con Piggy

# Función para mostrar mensaje de éxito
def mostrar_mensaje_exito():
    global en_seleccion_mapa
    fuente = pygame.font.Font(None, 36)
    ventana.fill(BLANCO)
    mensaje = fuente.render("¡Rene encontro la galleta!", True, VERDE)
    ventana.blit(mensaje, (100, 100))
    pygame.display.flip()
    pygame.time.delay(2000)
    en_seleccion_mapa = True  # Permitir selección de mapa tras éxito

# Función para reiniciar posiciones
def reiniciar_laberinto():
    global laberinto, posiciones, posicion_rene, posicion_piggy, posicion_elmo, posicion_galleta
    laberinto = [fila[:] for fila in mapas[mapa_actual]]  # Copia del mapa seleccionado
    posiciones = obtener_posicion(laberinto)  # Actualiza las posiciones de personajes y objetos
    posicion_rene = posiciones["rene"]
    posicion_piggy = posiciones["piggy"]
    posicion_elmo = posiciones["elmo"]
    posicion_galleta = posiciones["galleta"]
    
# Función principal del juego
import random

def jugar(laberinto, camino_rene, camino_piggy, posicion_rene, posicion_piggy, posicion_elmo):
    global en_seleccion_mapa
    encontro_piggy = False  # Variable local para determinar si Piggy encontró a René
    
    # Inicializar índices para iterar por los caminos
    indice_rene = 0
    indice_piggy = 0

    # Iterar hasta que ambos caminos terminen o se cumplan condiciones de finalización
    while indice_rene < len(camino_rene) or indice_piggy < len(camino_piggy):
        
        # Mover a René si aún tiene pasos en su camino
        if indice_rene < len(camino_rene):
            posicion_rene = camino_rene[indice_rene]  # Actualiza la posición de René
            mover_personaje(laberinto, [posicion_rene], 'R', camino_piggy, posicion_rene, posicion_piggy)
            indice_rene += 1

        # Mover a Piggy si aún tiene pasos en su camino
        if indice_piggy < len(camino_piggy):
            posicion_piggy = camino_piggy[indice_piggy]  # Actualiza la posición de Piggy
            mover_personaje(laberinto, [posicion_piggy], 'P', camino_piggy, posicion_rene, posicion_piggy)
            indice_piggy += 1

        # Verificar si Piggy encontró a René
        if posicion_piggy == posicion_rene:
            encontro_piggy = True  # Actualizar la variable local
            en_seleccion_mapa = True  # Permitir selección de mapa tras interacción con Piggy
            break

        # Verificar si René encontró a Piggy o a Elmo para finalizar el juego
        if posicion_rene == posicion_elmo or encontro_piggy:
            break

        # Actualiza el camino de Piggy después de cada movimiento, con cambio de algoritmo
        if indice_piggy < len(camino_piggy):
            # Generar un número aleatorio entre 1 y 10 para decidir si usar A* o BFS
            cambio_algoritmo = random.randint(1, 10)

            # Si el número es menor a 4 (40% de probabilidad), usar A*
            if cambio_algoritmo <= 4:
                print(f"Turno: {cambio_algoritmo}. Usando A* para mover a Piggy.")
                camino_piggy = a_estrella(laberinto, posicion_piggy, posicion_rene)
            else:
                print(f"Turno: {cambio_algoritmo}. Usando BFS para mover a Piggy.")
                camino_piggy = bfs_piggy(laberinto, posicion_piggy, posicion_rene)

    # Mostrar mensaje de fin del juego
    if posicion_rene == posicion_elmo:
        mostrar_mensaje_exito()
        print("¡René ha encontrado a Elmo y ganó el juego!")
    elif encontro_piggy:
        mostrar_mensaje_interaccion_piggy()
        print("¡Piggy ha alcanzado a René, el juego ha terminado!")
        en_seleccion_mapa = True  # Permitir selección de mapa tras interacción con Piggy

# Interfaz gráfica
boton_jugar = Button(200, 100, "Jugar")
boton_nosotros = Button(200, 175, "Creditos")
boton_salir = Button(200, 250, "Salir")
boton_volver = Button(200, 500, "Volver")

def crear_botones_mapa():
    botones = []
    for i in range(len(mapas)):
        boton = Button(200, 100 + i * 75, f"Mapa {i + 1}")
        boton.update()
        botones.append(boton)
    return botones

# Variable para controlar el estado del juego
en_menu = True
en_nosotros = False

# Función para actualizar el estado del juego
def update(events):
    if en_menu:
        boton_jugar.update()
        boton_nosotros.update()
        boton_salir.update()
    elif en_nosotros:
        boton_volver.update()
    elif en_seleccion_mapa:
        pass  # No necesitas botones en la selección de mapa

# Función para dibujar en la ventana
def draw():
    if en_menu:
        ventana.fill(BLANCO)
        boton_jugar.draw(ventana)
        boton_nosotros.draw(ventana)
        boton_salir.draw(ventana)
    elif en_nosotros:
        nosotros()
    elif en_seleccion_mapa:
        mostrar_seleccion_mapa()  # Mostrar la selección de mapa
    pygame.display.flip()

def nosotros():
    ventana.fill(BLANCO)
    fuente = pygame.font.Font(FONT, 24)
    creditos = [
        "Desarrollado por:",
        "Luis F. Hernandez - 2160189",
        "Juan E. Vargas - 2160191",
        "Universidad del Valle",
    ]
    y = 50
    for linea in creditos:
        texto = fuente.render(linea, True, NEGRO)
        ventana.blit(texto, (50, y))
        y += 50
    boton_volver.draw(ventana)
    pygame.display.flip()
    
# Función para manejar eventos
def manejar_eventos(events):
    global en_menu, en_nosotros, en_seleccion_mapa, laberinto
    global posiciones, posicion_rene, posicion_piggy, posicion_elmo, posicion_galleta, mapa_actual
    for e in events:
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if en_menu:
            if boton_jugar.clicked:
                en_menu = False
                en_seleccion_mapa = True  # Cambia al estado de selección de mapa
            if boton_nosotros.clicked:
                en_menu = False
                en_nosotros = True
            if boton_salir.clicked:
                pygame.quit()
                sys.exit()
        elif en_seleccion_mapa:
            # Verifica cada botón de mapa
            botones_mapa = crear_botones_mapa()
            for i, boton_mapa in enumerate(botones_mapa):
                boton_mapa.update()
                if boton_mapa.clicked:
                    # Actualiza el mapa actual y reinicia el laberinto
                    mapa_actual = i
                    reiniciar_laberinto()
                    en_seleccion_mapa = False
                    en_menu = False
                    profundidad_maxima = 20
                    # Calcula los caminos para René y Piggy
                    camino_rene = busqueda_profundidad_limitada(laberinto, posicion_rene, posicion_elmo, profundidad_maxima)
                    camino_piggy = a_estrella(laberinto, posicion_piggy, posicion_rene)
                    # Llama a jugar con los parámetros correctos
                    jugar(laberinto, camino_rene, camino_piggy, posicion_rene, posicion_piggy, posicion_elmo)
            # Crear y actualizar el botón de "Volver al menú"
            boton_volver_menu = Button(200, 100 + len(mapas) * 75, "Volver al menú")
            boton_volver_menu.update()
            if boton_volver_menu.clicked:
                en_seleccion_mapa = False
                en_menu = True  # Regresar al menú principal
        elif en_nosotros:
            if boton_volver.clicked:
                en_nosotros = False
                en_menu = True  # Regresar al menú principal
                
# Función para mostrar la selección de mapa
def mostrar_seleccion_mapa():
    ventana.fill(BLANCO)
    fuente = pygame.font.Font(FONT, 24)

    # Títulos
    titulo = fuente.render("Selecciona un mapa:", True, NEGRO)
    ventana.blit(titulo, (150, 50))

    # Dibujar botones para cada mapa
    botones_mapa = crear_botones_mapa()
    for boton_mapa in botones_mapa:
        boton_mapa.draw(ventana)

    # Botón de volver al menú
    boton_volver_menu = Button(200, 100 + len(mapas) * 75, "Volver al menú")
    boton_volver_menu.draw(ventana)

    pygame.display.flip()

# Bucle principal
while True:
    events = pygame.event.get()
    manejar_eventos(events)
    update(events)
    draw()
    reloj.tick(60)

# Salir del juego
pygame.quit()
