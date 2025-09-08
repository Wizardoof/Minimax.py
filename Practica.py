
def crear_tablero(filas=5, columnas=5):
    """Crea un tablero vacío con las dimensiones dadas y la salida."""
    
    
    tablero = [["." for _ in range(columnas)] for _ in range(filas)]

    
    gato = (0, 0)  # posición inicial del gato
    raton = (filas - 1, columnas - 1)  # posición inicial del ratón
    salida = (filas // 2, columnas // 2)  # salida en el centro


    tablero[gato[0]][gato[1]] = "🐱"
    tablero[raton[0]][raton[1]] = "🐭"
    tablero[salida[0]][salida[1]] = "🚪"


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

    if __name__ == "__main__":
        juego = crear_tablero()
        mostrar_tablero(juego)