
from typing import List, Tuple

Position = Tuple[int, int]

class Laberinto:
    def __init__(self, ancho: int, alto: int):
        self.ancho = ancho
        self.alto = alto
        self.tablero = [["⬜" for _ in range(ancho)] for _ in range(alto)]
        
        # Posiciones iniciales
        self.gato = (0, 0)
        self.raton = (alto - 1, ancho - 1)
        self.salida = (alto // 2, ancho // 2)

        # Dibujar elementos en el tablero
        self.tablero[self.salida[0]][self.salida[1]] = '🚪'
        self.tablero[self.gato[0]][self.gato[1]] = '🐱'
        self.tablero[self.raton[0]][self.raton[1]] = '🐭'

    def mostrar(self):
        for fila in self.tablero:
            print(" ".join(fila))
        print()

    def movimiento_valido(self, pos: Position, jugador: str) -> bool:
        x, y = pos
        if x < 0 or x >= self.alto or y < 0 or y >= self.ancho:
            return False
        if self.tablero[x][y] == '🚪' and jugador == 'G':
            return False
        return True

    def mover_jugador(self, jugador: str, nueva_pos: Position):
        if jugador == 'G':
            self.tablero[self.gato[0]][self.gato[1]] = '⬜'
            self.gato = nueva_pos
            self.tablero[self.gato[0]][self.gato[1]] = '🐱'
        else:
            self.tablero[self.raton[0]][self.raton[1]] = '⬜'
            self.raton = nueva_pos
            self.tablero[self.raton[0]][self.raton[1]] = '🐭'

    def movimientos_posibles(self, jugador: str) -> List[Position]:
        pos_actual = self.gato if jugador == 'G' else self.raton
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        movimientos = []
        for d in direcciones:
            nueva_pos = (pos_actual[0] + d[0], pos_actual[1] + d[1])
            if self.movimiento_valido(nueva_pos, jugador):
                movimientos.append(nueva_pos)
        return movimientos

    def estado_final(self) -> str:
        if self.gato == self.raton:
            return "Gato gana"
        if self.raton == self.salida:
            return "Ratón gana"
        return ""

# 🔹 NUEVO: Minimax solo para el ratón (el gato ya no tiene IA)
def minimax(laberinto: Laberinto, profundidad: int, maximizando: bool) -> int:
    estado = laberinto.estado_final()
    if estado == "Ratón gana":
        return 10 - profundidad
    elif estado == "Gato gana":
        return profundidad - 10
    if profundidad == 0:
        return 0

    if maximizando:
        max_eval = float('-inf')
        for mov in laberinto.movimientos_posibles('R'):
            copia = copiar_laberinto(laberinto)
            copia.mover_jugador('R', mov)
            evaluacion = minimax(copia, profundidad - 1, False)
            max_eval = max(max_eval, evaluacion)
        return max_eval
    else:
        # 🔹 El gato ya no usa IA, así que solo retorna 0 aquí
        return 0

def mejor_movimiento_raton(laberinto: Laberinto, profundidad: int) -> Position:
    mejor_eval = float('-inf')
    mejor_mov = None
    for mov in laberinto.movimientos_posibles('R'):
        copia = copiar_laberinto(laberinto)
        copia.mover_jugador('R', mov)
        evaluacion = minimax(copia, profundidad - 1, False)
        if evaluacion > mejor_eval:
            mejor_eval = evaluacion
            mejor_mov = mov
    return mejor_mov

# 🔹 Copiar el estado del laberinto
def copiar_laberinto(original: Laberinto) -> Laberinto:
    copia = Laberinto(original.ancho, original.alto)
    copia.tablero = [fila[:] for fila in original.tablero]
    copia.gato = original.gato
    copia.raton = original.raton
    copia.salida = original.salida
    return copia

# 🔹 Juego principal: el jugador humano controla al gato, el ratón usa IA
def jugar():
    lab = Laberinto(5, 5)
    turno_gato = True

    while True:
        lab.mostrar()
        estado = lab.estado_final()
        if estado:
            print(estado)
            break

        if turno_gato:
            print("Tu turno (Gato 🐱). Usa W/A/S/D para mover.")
            tecla = input("Movimiento: ").upper()
            movimientos = {'W': (-1, 0), 'S': (1, 0), 'A': (0, -1), 'D': (0, 1)}
            if tecla in movimientos:
                nueva_pos = (lab.gato[0] + movimientos[tecla][0], lab.gato[1] + movimientos[tecla][1])
                if lab.movimiento_valido(nueva_pos, 'G'):
                    lab.mover_jugador('G', nueva_pos)
                    turno_gato = False
                else:
                    print("Movimiento inválido.")
            else:
                print("Tecla inválida.")
        else:
            print("Turno del Ratón 🐭 (IA)...")
            mov = mejor_movimiento_raton(lab, 3)
            if mov:
                lab.mover_jugador('R', mov)
            turno_gato = True

if __name__ == "__main__":
    jugar()
