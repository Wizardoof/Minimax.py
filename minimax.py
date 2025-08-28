import time
#  Importe typing para ayudar al IDE a entender nuestros tipos de datos
# typing es parte de Python estándar desde la versión 3.5, no es una librería externa
from typing import List, Tuple, Dict, Union

# Defini tipos personalizados para que el código sea más claro y el IDE funcione mejor
# Position representa una coordenada (fila, columna) en el tablero
Position = Tuple[int, int]
# GameState es un diccionario que guarda el estado completo del juego
GameState = Dict[str, Union[Position, int]]

class Laberinto:
    #Agregue type hints (-> None significa que no devuelve nada)
    def __init__(self, filas=8, columnas=8):
        self.filas, self.columnas = filas, columnas
        self.tablero = [['_' for _ in range(columnas)] for _ in range(filas)]
        self.gato = (0, 0)
        self.raton = (filas-1, columnas-1)
        self.salida = (0, columnas-1)
        self.turno = 0
        self.max_turnos = 25
        self.actualizar_tablero()
    
    def actualizar_tablero(self):
        for i in range(self.filas):
            for j in range(self.columnas):
                self.tablero[i][j] = '_'
        
        self.tablero[self.salida[0]][self.salida[1]] = '🚪'
        self.tablero[self.gato[0]][self.gato[1]] = '🐱'
        self.tablero[self.raton[0]][self.raton[1]] = '🐭'
    
    # Agregamos type hints - pos es una Position, jugador es string, devuelve bool
    def movimiento_valido(self, pos: Position, jugador: str) -> bool:
        fila, col = pos
        
        if jugador == 'R' and pos == self.salida:
            return True
            
        if not (0 <= fila < self.filas and 0 <= col < self.columnas):
            return False
            
        if jugador == 'G' and pos == self.raton:
            return True
            
        if jugador == 'R' and pos == self.gato:
            return False
            
        return True
    
    # Especificamos que devuelve una lista de posiciones
    def movimientos_posibles(self, jugador: str) -> List[Position]:
        pos_actual = self.gato if jugador == 'G' else self.raton
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        movimientos = []
        for d in direcciones:
            nueva_pos = (pos_actual[0] + d[0], pos_actual[1] + d[1])
            if self.movimiento_valido(nueva_pos, jugador):
                movimientos.append(nueva_pos)
        
        if jugador == 'R':
            dist_salida = abs(pos_actual[0] - self.salida[0]) + abs(pos_actual[1] - self.salida[1])
            if dist_salida == 1:
                movimientos.append(self.salida)
                
        return movimientos
    
    # MODIFICADO: Especificamos que devuelve un string (el resultado del juego)
    def mover(self, jugador: str, nueva_pos: Position) -> str:
        if jugador == 'G':
            self.gato = nueva_pos
            if self.gato == self.raton:
                return 'GATO_GANA'
        else:
            if nueva_pos == self.salida:
                return 'RATON_LLEGA_SALIDA'
            
            self.raton = nueva_pos
            self.turno += 1
            if self.turno >= self.max_turnos:
                return 'RATON_SOBREVIVE'
        
        self.actualizar_tablero()
        return 'CONTINUA'

class Juego:
    VALOR_INICIAL_MIN = -1000000
    VALOR_INICIAL_MAX = 1000000
    
    # MODIFICADO: Especificamos el tipo del parámetro laberinto
    def __init__(self, laberinto: Laberinto):
        self.laberinto = laberinto
        self.profundidad_gato = 4
        self.profundidad_raton = 2
        self.umbral_evolucion = 5
        self.turnos_sobrevividos = 0
        self.nivel_evolucion = 0
    
    def evolucionar_inteligencia(self):
        self.turnos_sobrevividos += 1
        
        if (self.turnos_sobrevividos >= self.umbral_evolucion and 
            self.profundidad_raton < 5):
            
            self.nivel_evolucion += 1
            vieja_profundidad = self.profundidad_raton
            self.profundidad_raton += 1
            self.turnos_sobrevividos = 0
            
            mensajes = [
                "¡El ratón está despertando su inteligencia!",
                "¡El ratón se está volviendo más inteligente!",
                "¡El ratón es ahora un maestro del escape!"
            ]
            
            msg_index = min(self.nivel_evolucion - 1, len(mensajes) - 1)
            print(f"🐭 {mensajes[msg_index]}")
            print(f"   Nivel de pensamiento: {vieja_profundidad} → {self.profundidad_raton} movimientos")
    
    # MODIFICADO: Agregamos type hints para el estado simulado y sus parámetros
    def movimiento_valido_simulado(self, estado: GameState, pos: Position, jugador: str) -> bool:
        fila, col = pos
        
        if jugador == 'R' and pos == estado['salida']:
            return True
            
        if not (0 <= fila < estado['filas'] and 0 <= col < estado['columnas']):
            return False
            
        if jugador == 'G' and pos == estado['raton']:
            return True
            
        if jugador == 'R' and pos == estado['gato']:
            return False
            
        return True
    
    def movimientos_posibles_simulados(self, estado: GameState, jugador: str) -> List[Position]:
        # AGREGADO: type: ignore le dice al IDE que ignore la advertencia de tipo aquí
        # Esto es necesario porque el diccionario puede contener diferentes tipos
        pos_actual = estado['gato'] if jugador == 'G' else estado['raton']  # type: ignore
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        movimientos = []
        for d in direcciones:
            nueva_pos = (pos_actual[0] + d[0], pos_actual[1] + d[1])
            if self.movimiento_valido_simulado(estado, nueva_pos, jugador):
                movimientos.append(nueva_pos)
        
        if jugador == 'R':
            # AGREGADO: Extraemos la posición de salida del estado con type hint
            salida_pos = estado['salida']  # type: ignore
            dist_salida = abs(pos_actual[0] - salida_pos[0]) + abs(pos_actual[1] - salida_pos[1])
            if dist_salida == 1:
                movimientos.append(salida_pos)
        
        return movimientos
    
    def simular_movimiento(self, estado: GameState, jugador: str, movimiento: Position) -> GameState:
        nuevo_estado = estado.copy()
        
        if jugador == 'G':
            nuevo_estado['gato'] = movimiento
        else:
            nuevo_estado['raton'] = movimiento
            if movimiento != estado['salida']:
                # AGREGADO: Convertimos a int para asegurar el tipo correcto
                nuevo_estado['turno'] = int(nuevo_estado['turno']) + 1  # type: ignore
        
        return nuevo_estado
    
    def evaluar_estado_simulado(self, estado: GameState) -> int:
        # AGREGADO: Extraemos los valores del estado con conversiones de tipo explícitas
        # Esto ayuda al IDE a entender qué tipo de dato esperamos
        gato_pos = estado['gato']  # type: ignore
        raton_pos = estado['raton']  # type: ignore
        salida_pos = estado['salida']  # type: ignore
        turno = int(estado['turno'])  # type: ignore
        max_turnos = int(estado['max_turnos'])  # type: ignore
        
        if gato_pos == raton_pos:
            return -1000
        if raton_pos == salida_pos:
            return 1000
        if turno >= max_turnos:
            return 800
        
        dist_gato_raton = abs(gato_pos[0] - raton_pos[0]) + abs(gato_pos[1] - raton_pos[1])
        dist_raton_salida = abs(raton_pos[0] - salida_pos[0]) + abs(raton_pos[1] - salida_pos[1])
        
        return -dist_gato_raton * 3 + dist_raton_salida * 2
    
    def minimax(self, estado: GameState, profundidad: int, es_maximizador: bool) -> int:
        # AGREGADO: Extraemos las posiciones del estado para mayor claridad
        gato_pos = estado['gato']  # type: ignore
        raton_pos = estado['raton']  # type: ignore
        salida_pos = estado['salida']  # type: ignore
        turno = int(estado['turno'])  # type: ignore
        max_turnos = int(estado['max_turnos'])  # type: ignore
        
        if gato_pos == raton_pos:
            return -1000
        if raton_pos == salida_pos:
            return 1000
        if turno >= max_turnos:
            return 800
        
        if profundidad == 0:
            return self.evaluar_estado_simulado(estado)
        
        if es_maximizador:
            mejor_valor = self.VALOR_INICIAL_MIN
            for movimiento in self.movimientos_posibles_simulados(estado, 'R'):
                nuevo_estado = self.simular_movimiento(estado, 'R', movimiento)
                valor = self.minimax(nuevo_estado, profundidad-1, False)
                mejor_valor = max(mejor_valor, valor)
            return mejor_valor
        else:
            mejor_valor = self.VALOR_INICIAL_MAX
            for movimiento in self.movimientos_posibles_simulados(estado, 'G'):
                nuevo_estado = self.simular_movimiento(estado, 'G', movimiento)
                valor = self.minimax(nuevo_estado, profundidad-1, True)
                mejor_valor = min(mejor_valor, valor)
            return mejor_valor
    
    def mejor_movimiento(self, jugador: str) -> Position:
        movimientos = self.laberinto.movimientos_posibles(jugador)
        if not movimientos:
            return self.laberinto.gato if jugador == 'G' else self.laberinto.raton
        
        # AGREGADO: Creamos el estado inicial con type hint para mayor claridad
        # Este diccionario contiene toda la información necesaria para simular el juego
        estado_inicial: GameState = {
            'gato': self.laberinto.gato,
            'raton': self.laberinto.raton,
            'salida': self.laberinto.salida,
            'turno': self.laberinto.turno,
            'max_turnos': self.laberinto.max_turnos,
            'filas': self.laberinto.filas,
            'columnas': self.laberinto.columnas
        }
        
        if jugador == 'R':
            self.evolucionar_inteligencia()
            profundidad = self.profundidad_raton - 1
            es_maximizador = False
            mejor_valor = self.VALOR_INICIAL_MIN
        else:
            profundidad = self.profundidad_gato - 1
            es_maximizador = True
            mejor_valor = self.VALOR_INICIAL_MAX
        
        mejor_mov = movimientos[0]
        
        for movimiento in movimientos:
            nuevo_estado = self.simular_movimiento(estado_inicial, jugador, movimiento)
            valor = self.minimax(nuevo_estado, profundidad, es_maximizador)
            
            if (jugador == 'R' and valor > mejor_valor) or (jugador == 'G' and valor < mejor_valor):
                mejor_valor = valor
                mejor_mov = movimiento
        
        return mejor_mov

# MODIFICADO: Agregamos type hint para el parámetro
def mostrar_tablero_simple(laberinto: Laberinto):
    print(f"\nTurno: {laberinto.turno}/{laberinto.max_turnos}")
    for fila in laberinto.tablero:
        print(' '.join(fila))

def obtener_movimiento_jugador(laberinto: Laberinto, jugador: str) -> Position:
    print(f"\nTurno del {'Gato' if jugador == 'G' else 'Ratón'}")
    print("W=Arriba, A=Izquierda, S=Abajo, D=Derecha")
    
    movimientos = {'W': (-1, 0), 'A': (0, -1), 'S': (1, 0), 'D': (0, 1)}
    
    while True:
        tecla = input("Movimiento (W/A/S/D): ").upper()
        
        if tecla in movimientos:
            pos_actual = laberinto.gato if jugador == 'G' else laberinto.raton
            dx, dy = movimientos[tecla]
            nueva_pos = (pos_actual[0] + dx, pos_actual[1] + dy)
            
            if laberinto.movimiento_valido(nueva_pos, jugador):
                return nueva_pos
            print("Movimiento inválido. Intente otra dirección.")
        else:
            print("Tecla no válida. Use W, A, S o D.")

def simulacion_automatica():
    lab = Laberinto(8, 8)
    juego = Juego(lab)
    
    print("=== IA vs IA ===")
    print("Gato vs Ratón")
    
    while True:
        mostrar_tablero_simple(lab)
        time.sleep(1)
        
        # Ratón se mueve
        mov_raton = juego.mejor_movimiento('R')
        resultado = lab.mover('R', mov_raton)
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            if resultado == 'GATO_GANA':
                print("¡Gato gana! Atrapó al ratón")
            elif resultado == 'RATON_LLEGA_SALIDA':
                print("¡Ratón gana! Llegó a la salida")
            else:
                print("¡Ratón gana! Sobrevivió los turnos")
            break
        
        mostrar_tablero_simple(lab)
        time.sleep(1)
        
        # Gato se mueve
        mov_gato = juego.mejor_movimiento('G')
        resultado = lab.mover('G', mov_gato)
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            if resultado == 'GATO_GANA':
                print("¡Gato gana! Atrapó al ratón")
            elif resultado == 'RATON_LLEGA_SALIDA':
                print("¡Ratón gana! Llegó a la salida")
            else:
                print("¡Ratón gana! Sobrevivió los turnos")
            break

def jugar_como_raton():
    lab = Laberinto(8, 8)
    juego = Juego(lab)
    
    print("=== Tú como Ratón vs IA Gato ===")
    
    while True:
        mostrar_tablero_simple(lab)
        
        # Jugador (ratón) se mueve
        mov_raton = obtener_movimiento_jugador(lab, 'R')
        resultado = lab.mover('R', mov_raton)
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            if resultado == 'GATO_GANA':
                print("¡Perdiste! El gato te atrapó")
            elif resultado == 'RATON_LLEGA_SALIDA':
                print("¡Ganaste! Llegaste a la salida")
            else:
                print("¡Ganaste! Sobreviviste todos los turnos")
            break
        
        # IA (gato) se mueve
        mov_gato = juego.mejor_movimiento('G')
        resultado = lab.mover('G', mov_gato)
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            if resultado == 'GATO_GANA':
                print("¡Perdiste! El gato te atrapó")
            elif resultado == 'RATON_LLEGA_SALIDA':
                print("¡Ganaste! Llegaste a la salida")
            else:
                print("¡Ganaste! Sobreviviste todos los turnos")
            break

def jugar_como_gato():
    lab = Laberinto(8, 8)
    juego = Juego(lab)
    
    print("=== Tú como Gato vs IA Ratón ===")
    
    while True:
        mostrar_tablero_simple(lab)
        
        # IA (ratón) se mueve
        mov_raton = juego.mejor_movimiento('R')
        resultado = lab.mover('R', mov_raton)
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            if resultado == 'GATO_GANA':
                print("¡Ganaste! Atrapaste al ratón")
            elif resultado == 'RATON_LLEGA_SALIDA':
                print("¡Perdiste! El ratón llegó a la salida")
            else:
                print("¡Perdiste! El ratón sobrevivió")
            break
        
        mostrar_tablero_simple(lab)
        
        # Jugador (gato) se mueve
        mov_gato = obtener_movimiento_jugador(lab, 'G')
        resultado = lab.mover('G', mov_gato)
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            if resultado == 'GATO_GANA':
                print("¡Ganaste! Atrapaste al ratón")
            elif resultado == 'RATON_LLEGA_SALIDA':
                print("¡Perdiste! El ratón llegó a la salida")
            else:
                print("¡Perdiste! El ratón sobrevivió")
            break

def menu_principal():
    while True:
        print("\n=== LABERINTO GATO Y RATÓN ===")
        print("1. Ver IA vs IA")
        print("2. Jugar como Ratón")
        print("3. Jugar como Gato")
        print("4. Salir")
        
        opcion = input("Elige (1-4): ")
        
        if opcion == '1':
            simulacion_automatica()
        elif opcion == '2':
            jugar_como_raton()
        elif opcion == '3':
            jugar_como_gato()
        elif opcion == '4':
            print("¡Gracias por jugar!")
            break
        else:
            print("Opción no válida")

if __name__ == "__main__":
    menu_principal()