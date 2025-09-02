def crear_juego(filas=5, columnas=5):
    """
    Inicializa el estado del juego:
    - Crea un tablero vacío de filas x columnas.
    - Coloca el gato (esquina sup. izq), el ratón (esquina inf. der) y la salida (centro).
    Devuelve un diccionario con todo el estado del juego.
    """
    tablero = [["." for _ in range(columnas)] for _ in range(filas)]

    gato = (0, 0)  # posición inicial del gato
    raton = (filas - 1, columnas - 1)  # posición inicial del ratón
    salida = (filas // 2, columnas // 2)  # salida en el centro

    # Colocar los símbolos en el tablero
    tablero[salida[0]][salida[1]] = "🚪"
    tablero[gato[0]][gato[1]] = "🐱"
    tablero[raton[0]][raton[1]] = "🐭"

    return {
        "filas": filas,
        "columnas": columnas,
        "tablero": tablero,
        "gato": gato,
        "raton": raton,
        "salida": salida,
    }


def mostrar_tablero(juego):
    """Imprime el tablero actual en consola."""
    for fila in juego["tablero"]:
        print(" ".join(fila))
    print()


def es_movimiento_valido(juego, nueva_fila, nueva_col, jugador):
    """
    Verifica si un movimiento es válido:
    - Debe estar dentro de los límites del tablero.
    - El gato no puede entrar en la puerta (🚪).
    """
    filas, columnas = juego["filas"], juego["columnas"]

    if not (0 <= nueva_fila < filas and 0 <= nueva_col < columnas):
        return False

    if juego["tablero"][nueva_fila][nueva_col] == "🚪" and jugador == "G":
        return False

    return True


def mover_jugador(juego, jugador, nueva_fila, nueva_col):
    """
    Mueve al gato o al ratón a una nueva casilla.
    Actualiza tanto la posición del jugador como el tablero.
    """
    tablero = juego["tablero"]

    if jugador == "G":
        fila, col = juego["gato"]
        tablero[fila][col] = "."
        juego["gato"] = (nueva_fila, nueva_col)
        tablero[nueva_fila][nueva_col] = "🐱"
    else:  # Ratón
        fila, col = juego["raton"]
        tablero[fila][col] = "."
        juego["raton"] = (nueva_fila, nueva_col)
        tablero[nueva_fila][nueva_col] = "🐭"


def obtener_movimientos_posibles(juego, jugador):
    """
    Devuelve una lista de casillas válidas a las que puede moverse un jugador.
    (arriba, abajo, izquierda, derecha).
    """
    pos_f, pos_c = juego["gato"] if jugador == "G" else juego["raton"]

    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    movimientos = []

    for df, dc in direcciones:
        nf, nc = pos_f + df, pos_c + dc
        if es_movimiento_valido(juego, nf, nc, jugador):
            movimientos.append((nf, nc))

    return movimientos


def verificar_estado_final(juego):
    """
    Determina si el juego terminó:
    - El gato atrapa al ratón → Gato gana.
    - El ratón llega a la salida → Ratón gana.
    - Si ninguno, el juego sigue.
    """
    if juego["gato"] == juego["raton"]:
        return "Gato gana"

    if juego["raton"] == juego["salida"]:
        return "Ratón gana"

    return ""


def copiar_estado_juego(juego):
    """
    Devuelve una copia profunda del estado de juego.
    (Necesario para simular jugadas con Minimax sin alterar el tablero real).
    """
    return {
        "filas": juego["filas"],
        "columnas": juego["columnas"],
        "tablero": [fila.copy() for fila in juego["tablero"]],
        "gato": juego["gato"],
        "raton": juego["raton"],
        "salida": juego["salida"],
    }


def minimax(juego, profundidad, maximizando):
    """
    Algoritmo Minimax (versión simple):
    - El ratón busca maximizar sus chances de ganar.
    - El gato no tiene IA en esta versión (siempre devuelve 0).
    """
    estado = verificar_estado_final(juego)
    if estado == "Ratón gana":
        return 10 - profundidad  # mejor si gana rápido
    elif estado == "Gato gana":
        return profundidad - 10  # peor si pierde rápido

    if profundidad == 0:
        return 0  # límite de búsqueda

    if maximizando:  # turno del ratón
        mejor_valor = -10**9
        for nf, nc in obtener_movimientos_posibles(juego, "R"):
            sim = copiar_estado_juego(juego)
            mover_jugador(sim, "R", nf, nc)
            valor = minimax(sim, profundidad - 1, False)
            mejor_valor = max(mejor_valor, valor)
        return mejor_valor
    else:
        # El gato no decide con Minimax (solo jugador humano)
        return 0


def obtener_mejor_movimiento_raton(juego, profundidad):
    """
    Usa Minimax para elegir el movimiento que más favorece al ratón.
    """
    mejor_valor = -10**9
    mejor_movimiento = None

    for nf, nc in obtener_movimientos_posibles(juego, "R"):
        sim = copiar_estado_juego(juego)
        mover_jugador(sim, "R", nf, nc)
        valor = minimax(sim, profundidad - 1, False)

        if valor > mejor_valor:
            mejor_valor = valor
            mejor_movimiento = (nf, nc)

    return mejor_movimiento


def jugar():
    """
    Bucle principal del juego:
    - El humano mueve al gato (con W/A/S/D).
    - La IA mueve al ratón (usando Minimax).
    - Termina cuando alguien gana o se llega al límite de turnos.
    """
    juego = crear_juego(filas=5, columnas=5)
    turno_gato = True
    MAX_TURNOS = 25
    turno_actual = 0

    print("🎮 ¡JUEGO GATO vs RATÓN!")
    print("🐱 Gato (TÚ): Usa W/A/S/D para mover")
    print("🐭 Ratón (IA): Trata de llegar a la puerta 🚪\n")

    direc = {"W": (-1, 0), "S": (1, 0), "A": (0, -1), "D": (0, 1)}

    while True:
        mostrar_tablero(juego)
        print(f"Turno {turno_actual + 1} de {MAX_TURNOS}")

        # ¿Fin del juego?
        resultado = verificar_estado_final(juego)
        if resultado:
            print(f"🏆 {resultado}")
            break
        if turno_actual >= MAX_TURNOS:
            print("🤝 Empate: el ratón no escapó a tiempo.")
            break

        if turno_gato:
            # Turno humano → mover al gato
            tecla = input("Tu turno (Gato 🐱). W/A/S/D: ").upper()
            if tecla not in direc:
                print("❌ Tecla inválida.\n")
                continue

            df, dc = direc[tecla]
            gf, gc = juego["gato"]
            nueva_fila, nueva_col = gf + df, gc + dc

            if es_movimiento_valido(juego, nueva_fila, nueva_col, "G"):
                mover_jugador(juego, "G", nueva_fila, nueva_col)
                turno_gato = False
                turno_actual += 1
            else:
                print("❌ Movimiento inválido.\n")
        else:
            # Turno IA → mover al ratón
            print("🤖 Turno del Ratón (IA pensando...)")
            mejor_mov = obtener_mejor_movimiento_raton(juego, profundidad=3)
            if mejor_mov:
                mover_jugador(juego, "R", mejor_mov[0], mejor_mov[1])
                print(f"🐭 Ratón se movió a {mejor_mov}\n")
            turno_gato = True
            turno_actual += 1


if __name__ == "__main__":
    jugar()
