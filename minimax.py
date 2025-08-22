import random
import copy
import time

class Laberinto:
    def __init__(self, filas=8, columnas=8):
        #__init__ inicializador Este método se llama AUTOMÁTICAMENTE al crear un objeto
        self.filas, self.columnas = filas, columnas #self es la identidad de cada fila y columna
        self.tablero = [['.' for _ in range(columnas)] for _ in range(filas)]
        self.gato = (0, 0)           # Gato arriba-izquierda
        self.raton = (filas-1, columnas-1)  # Ratón abajo-derecha
        self.turno = 0
        self.max_turnos = 20         # pocos turnos juegos más rápidos
        self.actualizar_tablero()
    
    def actualizar_tablero(self):
        #Dibuja el tablero con las posiciones actuales
        # Limpiar tablero - Asegurarse de que tenga el tamaño correcto
        for i in range(self.filas):
            for j in range(self.columnas):
                self.tablero[i][j] = '.'
        
        # Colocar jugadores (verificar que estén dentro de los nuevos límites)
        if 0 <= self.gato[0] < self.filas and 0 <= self.gato[1] < self.columnas:
            self.tablero[self.gato[0]][self.gato[1]] = '🐱'
        else:
            # Reposicionar gato si está fuera de límites
            self.gato = (0, 0)
            self.tablero[0][0] = '🐱'
        
        if 0 <= self.raton[0] < self.filas and 0 <= self.raton[1] < self.columnas:
            self.tablero[self.raton[0]][self.raton[1]] = '🐭'
        else:
            # Reposicionar ratón si está fuera de límites
            self.raton = (self.filas-1, self.columnas-1)
            self.tablero[self.filas-1][self.columnas-1] = '🐭'
    
    def movimiento_valido(self, pos, jugador):
        #Verifica si un movimiento es permitido
        #pos=posicion, col=columna
        fila, col = pos
        # 1. No salir del tablero
        if not (0 <= fila < self.filas and 0 <= col < self.columnas):
            return False
        # 2. Gato puede atrapar ratón
        if jugador == 'G' and pos == self.raton:
            return True
        # 3. Ratón no puede moverse al gato
        if jugador == 'R' and pos == self.gato:
            return False
        return True
    
    def movimientos_posibles(self, jugador):
        #Lista de movimientos válidos (4 direcciones)
        pos_actual = self.gato if jugador == 'G' else self.raton
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Arriba, abajo, izquierda, derecha
        
        return [
            (pos_actual[0] + d[0], pos_actual[1] + d[1])
            for d in direcciones
            if self.movimiento_valido((pos_actual[0] + d[0], pos_actual[1] + d[1]), jugador)
        ]
    
    def mover(self, jugador, nueva_pos):
        #Mueve al jugador y verifica si alguien gana
        if jugador == 'G':
            self.gato = nueva_pos
            if self.gato == self.raton:  # Gato atrapa ratón
                return 'GATO_GANA'
        else:
            self.raton = nueva_pos
            self.turno += 1
            if self.turno >= self.max_turnos:  # Ratón sobrevive
                return 'RATON_ESCAPA'
        
        self.actualizar_tablero()
        return 'CONTINUA'
    
    def evaluar_estado(self):
        #distancia entre gato y ratón 
       
       
        if self.gato == self.raton:
            return -1000  # Gato gana (muy malo para ratón)
        if self.turno >= self.max_turnos:
            return 1000   # Ratón gana (muy bueno para ratón)
        
        distancia = abs(self.gato[0] - self.raton[0]) + abs(self.gato[1] - self.raton[1])
        puntuacion = -distancia * 3  # Base: el gato quiere minimizar distancia
        
        # Bonus por arrinconar al ratón cerca de bordes
        raton_cerca_borde = (
            self.raton[0] <= 1 or self.raton[0] >= self.filas - 2 or
            self.raton[1] <= 1 or self.raton[1] >= self.columnas - 2
        )
        
        if raton_cerca_borde:
            puntuacion -= 25  # Bonus para gato (más negativo es mejor)
        
        # Bonus por estar en la misma fila o columna (estrategia de acorralamiento)
        if self.gato[1] == self.raton[1]:  # Misma columna
            puntuacion -= 15
        if self.gato[0] == self.raton[0]:  # Misma fila
            puntuacion -= 15
        
        return puntuacion
        
class Juego:
    # Constantes de la clase (fuera de métodos)
    VALOR_INICIAL_MIN = -1000000  # Número muy negativo para no usar inf y que tarde mucho
    VALOR_INICIAL_MAX = 1000000   # Número muy positivo same
    
    def __init__(self, laberinto):
        self.laberinto = laberinto
        self.profundidad_base = 4  # Gato ve 4 movimientos adelante (antes 2) y siempre perdia 
        self.profundidad_actual = 2  # Ratón mantiene 2 inicial 
        self.umbral_evolucion = 5   # Turnos para evolucionar
        self.turnos_sobrevividos = 0
        self.nivel_evolucion = 0    # Contador de evoluciones
    
    def evolucionar_inteligencia(self):
        #Hace al ratón más inteligente cada X turnos sobrevividos
        self.turnos_sobrevividos += 1
        
        # Verificar si es tiempo de evolucionar
        if self.turnos_sobrevividos >= self.umbral_evolucion:
            if self.profundidad_actual < 5:  # Límite máximo de inteligencia
                self.nivel_evolucion += 1
                vieja_profundidad = self.profundidad_actual
                self.profundidad_actual += 1
                self.turnos_sobrevividos = 0
                
                mensajes = [
                    "🐭 ¡El ratón está despertando su inteligencia!",
                    "🐭 ¡El ratón se está volviendo más inteligente!",
                    "🐭 ¡El ratón es ahora un maestro del escape!"
                ]
                
                msg_index = min(self.nivel_evolucion - 1, len(mensajes) - 1)
                print(mensajes[msg_index])
                print(f"   Nivel de pensamiento: {vieja_profundidad} → {self.profundidad_actual} movimientos")
    
    def minimax(self, estado, profundidad, es_maximizador):
        #Algoritmo Minimax
        #  ¿como terminó el juego?
        if estado.gato == estado.raton:
            return -1000  # Más extremo (antes -100) y no se movia el gato los valores eran pocos para poder elegir el mejor movimiento
        if estado.turno >= estado.max_turnos:
            return 1000   # Más extremo (antes 100) lo mismo
        
        if profundidad == 0:
            return estado.evaluar_estado()
        
        if es_maximizador:  # Ratón (busca max)
            mejor_valor = self.VALOR_INICIAL_MIN 
            for movimiento in estado.movimientos_posibles('R'):
                nuevo_estado = copy.deepcopy(estado) #deepcopy para crear una copia del tablero entero para simular movimientos futuros
                nuevo_estado.mover('R', movimiento)
                valor = self.minimax(nuevo_estado, profundidad-1, False)
                mejor_valor = max(mejor_valor, valor)
            return mejor_valor
            
        else:  # Gato (busca mini)
             mejor_valor = self.VALOR_INICIAL_MAX
             for movimiento in estado.movimientos_posibles('G'):
                nuevo_estado = copy.deepcopy(estado)
                nuevo_estado.mover('G', movimiento)
                valor = self.minimax(nuevo_estado, profundidad-1, True)
                mejor_valor = min(mejor_valor, valor)
             return mejor_valor
    
    
    
    def mejor_movimiento(self, jugador):
        movimientos = self.laberinto.movimientos_posibles(jugador)
        if not movimientos:
            return self.laberinto.gato if jugador == 'G' else self.laberinto.raton
        
        mejor_mov = None
        
        if jugador == 'R':
            # Para ratón: usar profundidad_actual asi (evoluciona)
            self.evolucionar_inteligencia()
            mejor_valor = self.VALOR_INICIAL_MIN
            for movimiento in movimientos:
                nuevo_estado = copy.deepcopy(self.laberinto)
                nuevo_estado.mover('R', movimiento)
                valor = self.minimax(nuevo_estado, self.profundidad_actual-1, False)
                if valor > mejor_valor:
                    mejor_valor = valor
                    mejor_mov = movimiento
        else:
            # Para gato: usar profundidad_base (constante) con estrategia mejorada
            mejor_valor = self.VALOR_INICIAL_MAX
            mejor_mov = None
            
            # Ordenar movimientos por proximidad al ratón
            def distancia_a_raton(pos):
                return abs(pos[0] - self.laberinto.raton[0]) + abs(pos[1] - self.laberinto.raton[1])
            
        
            
            for movimiento in sorted(movimientos, key=distancia_a_raton):
                nuevo_estado = copy.deepcopy(self.laberinto)
                nuevo_estado.mover('G', movimiento)
                valor = self.minimax(nuevo_estado, self.profundidad_base-1, True)
                if valor < mejor_valor:
                    mejor_valor = valor
                    mejor_mov = movimiento
        
        return mejor_mov if mejor_mov is not None else movimientos[0]
    
    
    
    
    def jugar_turno_ia_vs_ia(self):
        #Un turno completo: ratón y luego gato (ambos IA)
        # Ratón se mueve
        mov_raton = self.mejor_movimiento('R')
        resultado = self.laberinto.mover('R', mov_raton)
        if resultado != 'CONTINUA':
            return resultado
        
        # Gato se mueve
        mov_gato = self.mejor_movimiento('G')
        resultado = self.laberinto.mover('G', mov_gato)
        return resultado

def mostrar_tablero_simple(laberinto):
    #Muestra el tablero de forma simple
    print(f"\nTurno: {laberinto.turno}/{laberinto.max_turnos}")
    for fila in laberinto.tablero:
        print(' '.join(fila))
    
    

def obtener_movimiento_jugador(laberinto, jugador):
    #Pide movimiento al jugador humano
    print(f"\nTurno del {'Gato' if jugador == 'G' else 'Ratón'}")
    print("W=Arriba, A=Izquierda, S=Abajo, D=Derecha")
    

    movimientos = {'W': (-1, 0), 'A': (0, -1), 'S': (1, 0), 'D': (0, 1)}
    
    while True:
        tecla = input("Movimiento (W/A/S/D): ").upper()
        
        if tecla in movimientos:
            pos_actual = laberinto.gato if jugador == 'G' else laberinto.raton
            movimiento = movimientos[tecla]
            nueva_pos = (pos_actual[0] + movimiento[0], pos_actual[1] + movimiento[1])
            
            if laberinto.movimiento_valido(nueva_pos, jugador):
                return nueva_pos
            else:
                print("Movimiento inválido. Intente otra dirección.")
        else:
            print("Tecla no válida. Use W, A, S o D.")

def simulacion_automatica():
    #Modo: IA vs IA 
    lab = Laberinto(8, 8)
    juego = Juego(lab)
    
    print("=== IA vs IA ===")
    print("🐱 Gato  vs 🐭 Ratón")
    while True:
        mostrar_tablero_simple(lab)
        time.sleep(1)
        
        resultado = juego.jugar_turno_ia_vs_ia()
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            print("¡Gato gana!" if resultado == 'GATO_GANA' else "¡Ratón escapo!")
            break

def jugar_como_raton():
    #Modo: Jugador como ratón vs IA gato
    lab = Laberinto(8, 8)
    juego = Juego(lab)
    
    print("=== Tú como Ratón vs IA Gato ===")
    print("🐭 Tú vs 🐱 IA")
    while True:
        mostrar_tablero_simple(lab)
        
        # Jugador (ratón)
        mov_raton = obtener_movimiento_jugador(lab, 'R')
        resultado = lab.mover('R', mov_raton)
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            print("¡Ganaste!" if resultado == 'RATON_ESCAPA' else "¡Perdiste!")
            break
        
        # IA (gato) - ahora más inteligente
        mov_gato = juego.mejor_movimiento('G')
        resultado = lab.mover('G', mov_gato)
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            print("¡Perdiste! El gato te atrapó")
            break

def jugar_como_gato():
    #Modo: Jugador como gato vs IA ratón
    lab = Laberinto(8, 8)
    juego = Juego(lab)
    
    print("=== Tú como Gato vs IA Ratón ===")
    print("🐱 Tú vs 🐭 IA")
    while True:
        mostrar_tablero_simple(lab)
        
        # IA (ratón) - evoluciona en inteligencia
        mov_raton = juego.mejor_movimiento('R')
        resultado = lab.mover('R', mov_raton)
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            print("¡Perdiste! El ratón escapó")
            break
        
        # Jugador (gato)
        mov_gato = obtener_movimiento_jugador(lab, 'G')
        resultado = lab.mover('G', mov_gato)
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            print("¡Ganaste! Atrapaste al ratón")
            break

def menu_principal():
    #Menú para elegir modo de juego
    while True:
        print("\n=== LABERINTO GATO Y RATÓN ===")
        print("1. Ver IA vs IA (Gato inteligente vs Ratón evolutivo)")
        print("2. Jugar como Ratón (vs IA Gato inteligente)")
        print("3. Jugar como Gato (vs IA Ratón evolutivo)")
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
            print("Opción no válida vuelva a intentar")

# Ejecutar el juego
if __name__ == "__main__":
    menu_principal()