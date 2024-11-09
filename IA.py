import pygame
import sys
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

def obtener_posicion(laberinto):
    posiciones = {}
    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            if laberinto[fila][columna] == 'R':
                posiciones['rene'] = (fila, columna)
            elif laberinto[fila][columna] == 'E':
                posiciones['elmo'] = (fila, columna)
            elif laberinto[fila][columna] == 'P':
                posiciones['piggy'] = (fila, columna)
            elif laberinto[fila][columna] == 'G':
                posiciones['galleta'] = (fila, columna)
    return posiciones

       
posiciones = obtener_posicion(laberinto)
posicion_rene = posiciones['rene']
posicion_elmo = posiciones['elmo']
posicion_piggy = posiciones['piggy']
posicion_galleta = posiciones['galleta']

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
def mover_personaje(laberinto, camino, personaje):
    global comio_galleta, encontro_piggy, posicion_rene, posicion_piggy, posicion_elmo

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

        # Verificar interacciones específicas de René
        if personaje == 'R':
            # Verificar si René encontró la galleta
            if (fila, columna) == tuple(posicion_galleta):
                comio_galleta = True

            # Verificar si René encontró a Piggy
            if (fila, columna) == posicion_piggy:
                encontro_piggy = True
                ventana.blit(imagen_rana_elmo, (columna * TAMANO_CELDA, fila * TAMANO_CELDA))
                pygame.display.flip()
                pygame.time.delay(500)
                break

            # Verificar si René encontró a Elmo
            if (fila, columna) == posicion_elmo:
                ventana.blit(imagen_rana_elmo, (columna * TAMANO_CELDA, fila * TAMANO_CELDA))
                pygame.display.flip()
                pygame.time.delay(500)
                break

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

        # Redibujar otros elementos del laberinto
        if comio_galleta:
            ventana.blit(imagen_galleta, (posicion_galleta[1] * TAMANO_CELDA, posicion_galleta[0] * TAMANO_CELDA))
        ventana.blit(imagen_piggy, (posicion_piggy[1] * TAMANO_CELDA, posicion_piggy[0] * TAMANO_CELDA))

        pygame.display.flip()
        pygame.time.delay(500)

    # Restablecer si René comió la galleta
    if personaje == 'R' and comio_galleta:
        comio_galleta = False
        dibujar_laberinto(ventana, laberinto)
        ventana.blit(imagen_rene, (columna * TAMANO_CELDA, fila * TAMANO_CELDA))
        pygame.display.flip()

    # Mostrar mensaje de interacción con Piggy si corresponde
    if personaje == 'R' and encontro_piggy:
        mostrar_mensaje_interaccion_piggy()
        encontro_piggy = False  # Reiniciar la variable después de mostrar el mensaje


# Función para mostrar mensaje de interacción con Piggy
def mostrar_mensaje_interaccion_piggy():
    fuente = pygame.font.Font(FONT, 20)
    ventana.fill(BLANCO)
    mensaje = fuente.render("¡René encontró a Piggy!", True, AMARILLO)
    ventana.blit(mensaje, (50, 50))
    pygame.display.flip()
    pygame.time.delay(2000)  # Mostrar el mensaje por 2 segundos

# Función para mostrar mensaje de éxito
def mostrar_mensaje_exito():
    fuente = pygame.font.Font(FONT, 20)
    ventana.fill(BLANCO)
    mensaje = fuente.render("¡René encontró a Elmo!", True, VERDE)
    ventana.blit(mensaje, (50, 50))
    boton_rect = pygame.Rect(150, 200, 300, 100)
    pygame.draw.rect(ventana, AZUL, boton_rect)
    boton_texto = fuente.render("Volver a jugar", True, BLANCO)
    ventana.blit(boton_texto, (200, 230))
    pygame.display.flip()
    
    esperando_click = True
    while esperando_click:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_rect.collidepoint(evento.pos):
                    esperando_click = False

# Función para reiniciar posiciones
def reiniciar_posiciones():
    obtener_posicion(laberinto)
    ventana.blit(imagen_piggy, (posicion_piggy[1] * TAMANO_CELDA, posicion_piggy[0] * TAMANO_CELDA))
    ventana.blit(imagen_galleta, (posicion_galleta[1] * TAMANO_CELDA, posicion_galleta[0] * TAMANO_CELDA))
    ventana.blit(imagen_rana_elmo, (posicion_elmo[1] * TAMANO_CELDA, posicion_elmo[0] * TAMANO_CELDA)) 
    pygame.display.flip()

# Función principal del juego
def jugar(laberinto, camino_rene, camino_piggy, posicion_rene, posicion_piggy):
    global encontro_piggy  # Variable global para determinar si Piggy encontró a René

    # Inicializar índices para iterar por los caminos
    indice_rene = 0
    indice_piggy = 0

    # Iterar hasta que ambos caminos terminen o se cumplan condiciones de finalización
    while indice_rene < len(camino_rene) or indice_piggy < len(camino_piggy):
        
        # Mover a René si aún tiene pasos en su camino
        if indice_rene < len(camino_rene):
            posicion_rene = camino_rene[indice_rene]  # Actualiza la posición de René
            mover_personaje(laberinto, [posicion_rene], 'R')
            indice_rene += 1
            
            # Verificar si René encontró a Piggy o a Elmo para finalizar el juego
            if encontro_piggy or posicion_rene == posicion_elmo:
                print("René ha terminado el juego.")
                break

        # Mover a Piggy si aún tiene pasos en su camino
        if indice_piggy < len(camino_piggy):
            posicion_piggy = camino_piggy[indice_piggy]  # Actualiza la posición de Piggy
            mover_personaje(laberinto, [posicion_piggy], 'P')
            indice_piggy += 1
            
            # Verificar si Piggy encontró a René
            if posicion_piggy == posicion_rene:
                print("¡Piggy ha atrapado a René!")
                break

        # Actualiza el camino de Piggy después de cada movimiento
        camino_piggy = actualizar_camino_piggy(laberinto, posicion_piggy, posicion_rene)

    # Mostrar mensaje de fin del juego
    if posicion_rene == posicion_elmo:
        print("¡René ha encontrado a Elmo y ganó el juego!")
    elif posicion_piggy == posicion_rene:
        print("¡Piggy ha alcanzado a René, el juego ha terminado!")


# Interfaz gráfica
boton_jugar = Button(200, 100, "Jugar")
boton_nosotros = Button(200, 175, "Creditos")
boton_salir = Button(200, 250, "Salir")
boton_volver = Button(200, 500, "Volver")

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
    global en_menu
    global en_nosotros
    global en_seleccion_mapa
    global laberinto
    global posiciones
    global posicion_rene
    global posicion_piggy
    global posicion_elmo
    global posicion_galleta

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
            # Aquí verifica cada botón de mapa
            for i in range(len(mapas)):
                boton_mapa = Button(200, 100 + i * 75, f"Mapa {i + 1}")
                boton_mapa.update()  # Actualiza el estado del botón
                if boton_mapa.clicked:
                    laberinto = mapas[i]  # Selecciona el mapa
                    posiciones = obtener_posicion(laberinto)
                    posicion_rene = posiciones['rene']
                    posicion_elmo = posiciones['elmo']
                    posicion_piggy = posiciones['piggy']
                    posicion_galleta = posiciones['galleta']
                    profundidad_maxima = 20

                    # Calcula los caminos para René y Piggy
                    camino_rene = busqueda_profundidad_limitada(laberinto, posicion_rene, posicion_elmo, profundidad_maxima)
                    camino_piggy = bfs_piggy(laberinto, posicion_piggy, posicion_rene)

                    # Llama a jugar pasando el camino y las posiciones actuales de René y Piggy
                    jugar(laberinto, camino_rene, camino_piggy, posicion_rene, posicion_piggy)  # Inicia el juego con los parámetros correctos

            # Botón de volver al menú
            boton_volver_menu = Button(200, 100 + len(mapas) * 75, "Volver al menú")
            boton_volver_menu.update()  # Asegúrate de que se actualice
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
    for i, mapa in enumerate(mapas):
        boton_mapa = Button(200, 100 + i * 75, f"Mapa {i + 1}")
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
