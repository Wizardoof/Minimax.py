# Variables globales del juego
columnas = 5
filas = 5
tablero = []
gato_fila = 0                # Gato en esquina superior izquierda
gato_col = 0
raton_fila = filas - 1      # Ratón en esquina inferior derecha
raton_col = columnas - 1
salida_fila = filas // 2    # Puerta en el centro
salida_col = columnas // 2

def crear_tablero():
    """
    Inicializa el juego: crea tablero vacío y coloca gato, ratón y puerta.
    """
    global tablero # Sin global tablero: La función crearía su propia variable tablero local que se perdería al terminar la función, y la variable global seguiría vacía
    # Crear matriz 5x5 llena de cuadros blancos
    tablero = [] 
    for i in range(filas):
        fila = []
        for j in range(columnas):
            fila.append("⬜")
        tablero.append(fila)
    
    # Colocar elementos en sus posiciones iniciales
    tablero[salida_fila][salida_col] = '🚪'  # Puerta de salida
    tablero[gato_fila][gato_col] = '🐱'       # Gato
    tablero[raton_fila][raton_col] = '🐭'     # Ratón

def mostrar_tablero():
    """
    Imprime el estado actual del tablero en pantalla.
    """
    for fila in tablero:
        linea = ""
        for casilla in fila:
            linea = linea + casilla + " "
        print(linea)
    print()  # Línea en blanco para separar turnos

def es_movimiento_valido(nueva_fila, nueva_col, jugador):
    """
    Verifica si un movimiento es legal.
    - Debe estar dentro del tablero
    - El gato no puede entrar en la puerta
    """
    # Verificar límites del tablero
    if nueva_fila < 0 or nueva_fila >= filas:
        return False
    if nueva_col < 0 or nueva_col >= columnas:
        return False
    
    # El gato no puede entrar en la puerta (solo el ratón puede)
    if tablero[nueva_fila][nueva_col] == '🚪' and jugador == 'G':
        return False
    
    return True

def mover_jugador(jugador, nueva_fila, nueva_col):
    """
    Mueve gato o ratón a nueva posición.
    - Borra de posición anterior
    - Actualiza coordenadas globales
    - Dibuja en nueva posición
    """
    global gato_fila, gato_col, raton_fila, raton_col
    
    if jugador == 'G':
        # Borrar gato de posición actual y moverlo
        tablero[gato_fila][gato_col] = '⬜'
        gato_fila = nueva_fila
        gato_col = nueva_col
        tablero[gato_fila][gato_col] = '🐱'
    else:  # jugador == 'R'
        # Borrar ratón de posición actual y moverlo
        tablero[raton_fila][raton_col] = '⬜'
        raton_fila = nueva_fila
        raton_col = nueva_col
        tablero[raton_fila][raton_col] = '🐭'

def obtener_movimientos_posibles(jugador):
    """
    Calcula todas las casillas válidas donde puede moverse un jugador.
    Prueba las 4 direcciones: arriba, abajo, izquierda, derecha.
    """
    # Obtener posición actual del jugador
    if jugador == 'G':
        pos_actual_fila = gato_fila
        pos_actual_col = gato_col
    else:
        pos_actual_fila = raton_fila
        pos_actual_col = raton_col
    
    # Probar las 4 direcciones posibles
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # arriba, abajo, izq, der
    movimientos = []
    
    for direccion in direcciones:
        nueva_fila = pos_actual_fila + direccion[0]
        nueva_col = pos_actual_col + direccion[1]
        
        if es_movimiento_valido(nueva_fila, nueva_col, jugador):
            movimientos.append((nueva_fila, nueva_col))
    
    return movimientos

def verificar_estado_final():
    """
    Revisa si el juego terminó y quién ganó.
    - Gato gana si alcanza al ratón
    - Ratón gana si llega a la puerta
    - Cadena vacía si el juego continúa
    """
    # Gato gana si está en la misma casilla que el ratón
    if gato_fila == raton_fila and gato_col == raton_col:
        return "Gato gana"
    
    # Ratón gana si llega a la puerta de salida
    if raton_fila == salida_fila and raton_col == salida_col:
        return "Ratón gana"
    
    # Juego continúa
    return ""

def copiar_estado_juego():
    """
    Crea una "foto" del estado actual del juego.
    Necesario para que el Minimax pueda simular movimientos sin afectar el juego real.
    """
    # Crear copia profunda del tablero (no solo referencia)
    tablero_copia = []
    for fila in tablero:
        fila_copia = []
        for casilla in fila:
            fila_copia.append(casilla)
        tablero_copia.append(fila_copia)
    
    # Retornar toda la información del estado actual
    return (tablero_copia, gato_fila, gato_col, raton_fila, raton_col)

def restaurar_estado_juego(estado):
    """
    Restaura el juego a un estado previo.
    Usado por Minimax para "deshacer" simulaciones y volver al estado real.
    """
    global tablero, gato_fila, gato_col, raton_fila, raton_col
    
    # Extraer datos del estado guardado
    tablero_copia, gato_f, gato_c, raton_f, raton_c = estado
    
    # Restaurar todas las variables globales
    tablero = tablero_copia
    gato_fila = gato_f
    gato_col = gato_c
    raton_fila = raton_f
    raton_col = raton_c

def minimax(profundidad, maximizando):
    """
    Inteligencia artificial que decide el mejor movimiento para el ratón.
    - Simula jugadas futuras sin cambiar el juego real
    - Números positivos = bueno para ratón, negativos = bueno para gato
    - Profundidad controla qué tan lejos "piensa" hacia el futuro
    """
    # Verificar si alguien ya ganó
    estado = verificar_estado_final()
    if estado == "Ratón gana":
        return 10 - profundidad  # Mejor si gana rápido
    elif estado == "Gato gana":
        return profundidad - 10  # Peor si pierde rápido
    if profundidad == 0:
        return 0  # Sin tiempo para decidir = empate
    
    if maximizando: #¿QUÉ TAN BUENO es este movimiento?
        # Turno del ratón: buscar el mejor movimiento posible
        mejor_valor = -999999  # Empezar pesimista
        movimientos = obtener_movimientos_posibles('R')
        
        for movimiento in movimientos:
            # Simular este movimiento y evaluarlo para ver si es el mejor 
            estado_previo = copiar_estado_juego()  #  Guardar estado
            mover_jugador('R', movimiento[0], movimiento[1])  #  Simular movimientos posibles y ver cual es el mejor 
            valor = minimax(profundidad - 1, False)  #  Evaluar recursivamente por eso se llama a si misma 
                        #"Un turno menos"  "Ahora le toca al gato"
            restaurar_estado_juego(estado_previo)  #  Deshacer simulación
            
            if valor > mejor_valor:
                mejor_valor = valor
        
        return mejor_valor
    else:
        # En esta versión, el gato no usa IA
        return 0

def obtener_mejor_movimiento_raton(profundidad): #"¿A DÓNDE me muevo?"
    """
    Encuentra el movimiento óptimo para el ratón usando Minimax.
    Prueba todos los movimientos posibles y elige el que da mejor resultado.
    """
    mejor_valor = -999999
    mejor_movimiento = None
    
    movimientos = obtener_movimientos_posibles('R')
    
    for movimiento in movimientos:
        # Simular y evaluar cada movimiento posible
        estado_previo = copiar_estado_juego()  #  Guardar
        mover_jugador('R', movimiento[0], movimiento[1])  #  Probar movimiento
        valor = minimax(profundidad - 1, False)  #  Evaluar
        restaurar_estado_juego(estado_previo)  #  Deshacer
        
        # Quedarse con el mejor movimiento encontrado
        if valor > mejor_valor:
            mejor_valor = valor
            mejor_movimiento = movimiento
    
    return mejor_movimiento

def jugar():
    """
    Función principal que ejecuta todo el juego.
    - Inicializa tablero
    - Alterna turnos entre jugador humano (gato) e IA (ratón)
    - Controla límite de turnos y condiciones de victoria
    """
    # Configuración inicial
    crear_tablero()
    turno_gato = True  # El gato siempre empieza o va a ser injusto
    MAX_TURNOS = 25
    turno_actual = 0
    
    # Mostrar instrucciones
    print("🎮 ¡JUEGO GATO vs RATÓN!")
    print("🐱 Gato (TÚ): Usa W/A/S/D para mover")
    print("🐭 Ratón (IA): Trata de llegar a la puerta 🚪")
    print("🎯 Objetivo: Gato debe atrapar al ratón antes de que escape")
    print()
    
    # Bucle principal del juego
    while True:
        # Mostrar estado actual
        mostrar_tablero()
        print(f"Turno {turno_actual + 1} de {MAX_TURNOS}")
        
        # Verificar condiciones de fin de juego
        resultado = verificar_estado_final()
        if resultado != "":
            print(f"🏆 {resultado}")
            break
        
        if turno_actual >= MAX_TURNOS:
            print(" El ratón no escapo termino en empate.")
            break
        
        if turno_gato:
            # Turno del jugador humano (controla el gato)
            print("Tu turno (Gato 🐱). Movimiento:")
            tecla = input("W=Arriba, S=Abajo, A=Izquierda, D=Derecha: ")
            tecla = tecla.upper()
            
            # Convertir tecla a coordenadas
            movimiento_valido = False
            if tecla == 'W':  # Arriba
                nueva_fila, nueva_col = gato_fila - 1, gato_col
                movimiento_valido = True
            elif tecla == 'S':  # Abajo
                nueva_fila, nueva_col = gato_fila + 1, gato_col
                movimiento_valido = True
            elif tecla == 'A':  # Izquierda
                nueva_fila, nueva_col = gato_fila, gato_col - 1
                movimiento_valido = True
            elif tecla == 'D':  # Derecha
                nueva_fila, nueva_col = gato_fila, gato_col + 1
                movimiento_valido = True
            else:
                print("❌ Tecla inválida. Usa solo W/A/S/D")
                continue
            
            # Ejecutar movimiento si es válido
            if movimiento_valido and es_movimiento_valido(nueva_fila, nueva_col, 'G'):
                mover_jugador('G', nueva_fila, nueva_col)
                turno_gato = False  # Cambiar al ratón
                turno_actual = turno_actual + 1
            else:
                print("❌ Movimiento inválido. No puedes ir ahí.")
        
        else:
            # Turno de la IA (controla el ratón)
            print("🤖 Turno del Ratón (IA calculando...)")
            
            # La IA usa Minimax para decidir el mejor movimiento
            mejor_mov = obtener_mejor_movimiento_raton(3)  # Profundidad 3 = piensa 3 turnos adelante
            
            if mejor_mov != None:
                mover_jugador('R', mejor_mov[0], mejor_mov[1])
                print(f"🐭 Ratón se movió a posición ({mejor_mov[0]}, {mejor_mov[1]})")
            
            turno_gato = True  # Cambiar al gato
            turno_actual = turno_actual + 1

# Ejecutar el juego cuando se ejecuta este archivo
if __name__ == "__main__":
    jugar()