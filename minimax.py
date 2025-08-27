import time  # Solo esta biblioteca es necesaria

class Laberinto:
    def __init__(self, filas=8, columnas=8):
        #__init__ inicializador Este método se llama AUTOMÁTICAMENTE al crear un objeto
        self.filas, self.columnas = filas, columnas #self es la identidad de cada fila y columna
        self.tablero = [['.' for _ in range(columnas)] for _ in range(filas)]
        self.gato = (0, 0)           # Gato arriba-izquierda
        self.raton = (filas-1, columnas-1)  # Ratón abajo-derecha
        self.salida = (0, columnas-1)  # Salida arriba-derecha (posición estratégica)
        self.turno = 0
        self.max_turnos = 25         # pocos turnos juegos más rápidos
        self.actualizar_tablero()
    
    def actualizar_tablero(self):
        #Dibuja el tablero con las posiciones actuales
        # Limpiar tablero - Asegurarse de que tenga el tamaño correcto
        for i in range(self.filas):
            for j in range(self.columnas):
                self.tablero[i][j] = '_'
        
        # Colocar la salida primero (para que no se sobreescriba)
        self.tablero[self.salida[0]][self.salida[1]] = '🚪'
        
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
        
        # NUEVO: El ratón puede escapar por la salida (incluso si está fuera de límites)
        if jugador == 'R' and pos == self.salida:
            return True  # ← Movimiento especial de escape
        
        # 1. No salir del tablero (caso normal)
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
        
        movimientos_validos = []
        for d in direcciones:
            nueva_pos = (pos_actual[0] + d[0], pos_actual[1] + d[1])
            if self.movimiento_valido(nueva_pos, jugador):
                movimientos_validos.append(nueva_pos)
        
        # NUEVO: El ratón siempre puede intentar escapar si está junto a la salida
        if jugador == 'R':
            # Verificar si está adyacente a la salida usando distancia Manhattan
            dist_salida = abs(pos_actual[0] - self.salida[0]) + abs(pos_actual[1] - self.salida[1])
            if dist_salida == 1:  # Está justo al lado de la salida
                movimientos_validos.append(self.salida)  # ← Añadir movimiento de escape
        
        return movimientos_validos
    
    def mover(self, jugador, nueva_pos):
        #Mueve al jugador y verifica si alguien gana
        if jugador == 'G':
            self.gato = nueva_pos
            if self.gato == self.raton:  # Gato atrapa ratón
                return 'GATO_GANA'
        else:
            # NUEVO: Verificar si el ratón escapa por la salida (victoria principal)
            if nueva_pos == self.salida:
                return 'RATON_LLEGA_SALIDA'  # ← Victoria por llegar a salida
            
            self.raton = nueva_pos
            self.turno += 1
            # NUEVO: Verificar si sobrevive todos los turnos (victoria secundaria)
            if self.turno >= self.max_turnos:
                return 'RATON_SOBREVIVE'  # ← Victoria por supervivencia
        
        self.actualizar_tablero()
        return 'CONTINUA'
    
    def evaluar_estado(self):
        #distancia entre gato y ratón 
       
        if self.gato == self.raton:
            return -1000  # Gato gana (muy malo para ratón)
        if self.raton == self.salida:
            return 1000   # Ratón gana llegando a salida (máxima prioridad)
        if self.turno >= self.max_turnos:
            return 800    # Ratón gana por supervivencia (menor prioridad)
        
        # Cálculo de distancias usando Manhattan (suma de diferencias en X e Y)
        distancia_gato_raton = abs(self.gato[0] - self.raton[0]) + abs(self.gato[1] - self.raton[1])
        distancia_raton_salida = abs(self.raton[0] - self.salida[0]) + abs(self.raton[1] - self.salida[1])
        
        # Estrategia: gato quiere minimizar distancia al ratón y maximizar distancia del ratón a salida
        puntuacion = -distancia_gato_raton * 3  # Base prioritaria (más negativo es mejor para gato)
        puntuacion += distancia_raton_salida * 2  # Bonus: ratón lejos de salida = mejor para gato
        
        return puntuacion
        
class Juego:
    # Constantes de la clase (fuera de métodos)
    VALOR_INICIAL_MIN = -1000000  # Número muy negativo para no usar inf y que tarde mucho
    VALOR_INICIAL_MAX = 1000000   # Número muy positivo same
    
    def __init__(self, laberinto):
        self.laberinto = laberinto
        self.profundidad_gato = 4  # Gato ve 4 movimientos adelante
        self.profundidad_raton = 2  # Ratón mantiene 2 inicial 
        self.umbral_evolucion = 5   # Turnos para evolucionar
        self.turnos_sobrevividos = 0
        self.nivel_evolucion = 0    # Contador de evoluciones
    
    def evolucionar_inteligencia(self):
        #Hace al ratón más inteligente cada X turnos sobrevividos
        self.turnos_sobrevividos += 1
        
        # Verificar si es tiempo de evolucionar
        if (self.turnos_sobrevividos >= self.umbral_evolucion and 
            self.profundidad_raton < 5):  # Límite máximo de inteligencia
            
            self.nivel_evolucion += 1
            vieja_profundidad = self.profundidad_raton
            self.profundidad_raton += 1
            self.turnos_sobrevividos = 0  # Resetear contador
            
            mensajes = [
                "🐭 ¡El ratón está despertando su inteligencia!",
                "🐭 ¡El ratón se está volviendo más inteligente!",
                "🐭 ¡El ratón es ahora un maestro del escape!"
            ]
            
            msg_index = min(self.nivel_evolucion - 1, len(mensajes) - 1)
            print(mensajes[msg_index])
            print(f"   Nivel de pensamiento: {vieja_profundidad} → {self.profundidad_raton} movimientos")
    
    # ==================== MÉTODOS PARA MINIMAX CON ESTADOS SIMULADOS ====================
    
    def evaluar_estado_simulado(self, estado):
        
        if estado['gato'] == estado['raton']:
            return -1000
        if estado['raton'] == estado['salida']:
            return 1000   # Máxima prioridad: llegar a salida
        if estado['turno'] >= estado['max_turnos']:
            return 800    # Menor prioridad: sobrevivir turnos
        
        # Cálculo de distancias Manhattan para la heurística
        dist_gato_raton = abs(estado['gato'][0] - estado['raton'][0]) + abs(estado['gato'][1] - estado['raton'][1])
        dist_raton_salida = abs(estado['raton'][0] - estado['salida'][0]) + abs(estado['raton'][1] - estado['salida'][1])
        
        return -dist_gato_raton * 3 + dist_raton_salida * 2
    
    def movimientos_posibles_simulados(self, estado, jugador):
        """Versión simplificada de movimientos_posibles para estados simulados"""
        pos_actual = estado['gato'] if jugador == 'G' else estado['raton']
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Arriba, abajo, izquierda, derecha
        
        movimientos = []
        for d in direcciones:
            nueva_pos = (pos_actual[0] + d[0], pos_actual[1] + d[1])
            if self.movimiento_valido_simulado(estado, nueva_pos, jugador):
                movimientos.append(nueva_pos)
        
        # El ratón puede escapar si está junto a la salida (distancia Manhattan = 1)
        if jugador == 'R':
            dist_salida = abs(pos_actual[0] - estado['salida'][0]) + abs(pos_actual[1] - estado['salida'][1])
            if dist_salida == 1 and estado['salida'] not in movimientos:
                movimientos.append(estado['salida'])
        
        return movimientos
    
    def movimiento_valido_simulado(self, estado, pos, jugador):
        """Versión simplificada de movimiento_valido para estados simulados"""
        fila, col = pos
        
        # El ratón puede escapar por la salida
        if jugador == 'R' and pos == estado['salida']:
            return True
        
        # No salir del tablero
        if not (0 <= fila < estado['filas'] and 0 <= col < estado['columnas']):
            return False
        
        # Gato puede atrapar ratón
        if jugador == 'G' and pos == estado['raton']:
            return True
        
        # Ratón no puede moverse al gato
        if jugador == 'R' and pos == estado['gato']:
            return False
        
        return True
    
    def simular_movimiento(self, estado, jugador, movimiento):
        #Crea un nuevo estado simulado después de un movimiento (usa diccionarios)
        nuevo_estado = estado.copy()  # Copiamos el diccionario (más eficiente que deepcopy)
        
        if jugador == 'G':
            nuevo_estado['gato'] = movimiento
        else:
            nuevo_estado['raton'] = movimiento
            nuevo_estado['turno'] += 1  # Solo el ratón consume turnos
        
        return nuevo_estado
    
    def minimax(self, estado, profundidad, es_maximizador):
        #Algoritmo Minimax con estados simulados (diccionarios)
        # Estados terminales del juego
        if estado['gato'] == estado['raton']:
            return -1000  # Gato gana
        if estado['raton'] == estado['salida']:
            return 1000   # Ratón gana llegando a salida
        if estado['turno'] >= estado['max_turnos']:
            return 800    # Ratón gana por supervivencia
        
        # Límite de profundidad alcanzado, usar evaluación heurística
        if profundidad == 0:
            return self.evaluar_estado_simulado(estado)
        
        mejor_valor = self.VALOR_INICIAL_MIN if es_maximizador else self.VALOR_INICIAL_MAX
        
        jugador = 'R' if es_maximizador else 'G'
        for movimiento in self.movimientos_posibles_simulados(estado, jugador):
            nuevo_estado = self.simular_movimiento(estado, jugador, movimiento)
            
            valor = self.minimax(nuevo_estado, profundidad-1, not es_maximizador)
            
            if es_maximizador:
                mejor_valor = max(mejor_valor, valor)
            else:
                mejor_valor = min(mejor_valor, valor)
        
        return mejor_valor
    
    def mejor_movimiento(self, jugador):
        #Encuentra el mejor movimiento usando Minimax
        movimientos = self.laberinto.movimientos_posibles(jugador)
        if not movimientos:
            return self.laberinto.gato if jugador == 'G' else self.laberinto.raton
        
        # Crear estado inicial como diccionario para la simulación Minimax
        estado_inicial = {
            'gato': self.laberinto.gato,
            'raton': self.laberinto.raton,
            'salida': self.laberinto.salida,
            'turno': self.laberinto.turno,
            'max_turnos': self.laberinto.max_turnos,
            'filas': self.laberinto.filas,
            'columnas': self.laberinto.columnas
        }
        
        if jugador == 'R':
            # Para ratón: usar profundidad_actual (evoluciona)
            self.evolucionar_inteligencia()
            profundidad = self.profundidad_raton - 1
            es_maximizador = False  # Siguiente turno es del gato (minimizador)
            mejor_valor = self.VALOR_INICIAL_MIN
        else:
            # Para gato: usar profundidad_base (constante)
            profundidad = self.profundidad_gato - 1
            es_maximizador = True   # Siguiente turno es del ratón (maximizador)
            mejor_valor = self.VALOR_INICIAL_MAX
        
        mejor_mov = movimientos[0]  # Movimiento por defecto
        
        # Evaluar cada movimiento posible con Minimax
        for movimiento in movimientos:
            nuevo_estado = self.simular_movimiento(estado_inicial, jugador, movimiento)
            valor = self.minimax(nuevo_estado, profundidad, es_maximizador)
            
            # Ratón busca maximizar, Gato busca minimizar
            if (jugador == 'R' and valor > mejor_valor) or (jugador == 'G' and valor < mejor_valor):
                mejor_valor = valor
                mejor_mov = movimiento
        
        return mejor_mov
    
    def jugar_turno_ia_vs_ia(self):
        #Un turno completo: ratón y luego gato (ambos IA)
        # Ratón se mueve
        resultado = self.laberinto.mover('R', self.mejor_movimiento('R'))
        if resultado != 'CONTINUA':
            return resultado
        
        # Gato se mueve
        return self.laberinto.mover('G', self.mejor_movimiento('G'))

# ==================== FUNCIONES DE INTERFAZ ====================

def mostrar_tablero_simple(laberinto):
    #Muestra el tablero de forma simple
    print(f"Turno: {laberinto.turno}/{laberinto.max_turnos}")
    print(f"Ratón 🐭 busca llegar a 🚪 (salida)")
    for fila in laberinto.tablero:
        print(' '.join(fila))
    
def obtener_movimiento_jugador(laberinto, jugador):
    #Pide movimiento al jugador humano
    print(f"\nTurno del {'Gato 🐱' if jugador == 'G' else 'Ratón 🐭'}")
    print("W=Arriba, A=Izquierda, S=Abajo, D=Derecha")
    print(f"Objetivo: {'Atrapar al ratón' if jugador == 'G' else 'Llegar a 🚪'}")
    

    movimientos = {'W': (-1, 0), 'A': (0, -1), 'S': (1, 0), 'D': (0, 1)}
    
    while True:
        tecla = input("Movimiento (W/A/S/D): ").upper() #convierte si el input es minuscula a mayuscula automaticamente
        
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
    print("Objetivo: Ratón debe llegar a 🚪 (salida)")
    while True:
        mostrar_tablero_simple(lab)
        time.sleep(1)
        
        resultado = juego.jugar_turno_ia_vs_ia()
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            if resultado == 'GATO_GANA':
                print("¡Gato gana! Atrapó al ratón 🐱")
            elif resultado == 'RATON_LLEGA_SALIDA':
                print("¡Ratón gana! Llegó a la salida 🚪")
            else:
                print("¡Ratón gana! Sobrevivió todos los turnos ⏰")
            break

def jugar_como_raton():
    #Modo: Jugador como ratón vs IA gato
    lab = Laberinto(8, 8)
    juego = Juego(lab)
    
    print("=== Tú como Ratón vs IA Gato ===")
    print("🐭 Tú vs 🐱 IA")
    print("Objetivo: Llegar a 🚪 antes de que te atrapen")
    while True:
        mostrar_tablero_simple(lab)
        
        # Jugador (ratón)
        mov_raton = obtener_movimiento_jugador(lab, 'R')
        resultado = lab.mover('R', mov_raton)
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            if resultado == 'RATON_LLEGA_SALIDA':
                print("¡Ganaste! Llegaste a la salida 🚪")
            elif resultado == 'RATON_SOBREVIVE':
                print("¡Ganaste! Sobreviviste todos los turnos ⏰")
            else:
                print("¡Perdiste! El gato te atrapó 🐱")
            break
        
        # IA (gato) - ahora más inteligente
        mov_gato = juego.mejor_movimiento('G')
        resultado = lab.mover('G', mov_gato)
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            print("¡Perdiste! El gato te atrapó 🐱")
            break

def jugar_como_gato():
    #Modo: Jugador como gato vs IA ratón
    lab = Laberinto(8, 8)
    juego = Juego(lab)
    
    print("=== Tú como Gato vs IA Ratón ===")
    print("🐱 Tú vs 🐭 IA")
    print("Objetivo: Atrapar al ratón antes de que escape")
    while True:
        mostrar_tablero_simple(lab)
        
        # IA (ratón) - evoluciona en inteligencia
        mov_raton = juego.mejor_movimiento('R')
        resultado = lab.mover('R', mov_raton)
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            if resultado == 'RATON_LLEGA_SALIDA':
                print("¡Perdiste! El ratón llegó a la salida 🚪")
            else:
                print("¡Perdiste! El ratón sobrevivió todos los turnos ⏰")
            break
        
        # Jugador (gato)
        mov_gato = obtener_movimiento_jugador(lab, 'G')
        resultado = lab.mover('G', mov_gato)
        if resultado != 'CONTINUA':
            mostrar_tablero_simple(lab)
            print("¡Ganaste! Atrapaste al ratón 🐱")
            break

def menu_principal():
    #Menú para elegir modo de juego
    while True:
        print("=== LABERINTO GATO Y RATÓN ===")
        print("🎯 Objetivo principal: El ratón debe llegar a la salida 🚪")
        print("⏰ Objetivo secundario: Sobrevivir 20 turnos")
        print("🐱 El gato debe atrapar al ratón antes de que escape")
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