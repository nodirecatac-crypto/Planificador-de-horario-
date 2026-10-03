# ==============================================================
# PLANIFICADOR DE HORARIOS ACADÉMICOS
# Proyecto final: estrategia voraz + Backtracking con poda
#
# Modelo (CSP): cada curso es una variable cuyo valor es la terna
# (día, hora, aula). Restricciones:
#   R1. Un docente no puede tener dos cursos en el mismo día y hora.
#   R2. Un aula no puede asignarse a dos cursos en el mismo día y hora.
#   R3. La capacidad del aula debe ser >= cantidad de estudiantes.
# ==============================================================

# --------------------------------------------------------------
# Datos del sistema (configurables desde el menú)
# --------------------------------------------------------------
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

turnos = {
    "Mañana": ["08:00-09:30", "09:40-11:10", "11:20-12:50"],
    "Tarde": ["14:00-15:30", "15:40-17:10", "17:20-18:50"],
    "Noche": ["19:00-20:30", "20:40-22:10"],
}

aulas = [
    {"nombre": "A-101", "capacidad": 30},
    {"nombre": "A-102", "capacidad": 40},
    {"nombre": "B-201", "capacidad": 60},
]

cursos = []  # cada curso: {"nombre", "docente", "estudiantes", "turno"}

# Contadores del Backtracking (nodos explorados y podas realizadas)
estadisticas = {"nodos": 0, "podas": 0}


# --------------------------------------------------------------
# Utilidades de entrada y salida
# --------------------------------------------------------------
def leer_entero(mensaje, minimo=1):
    """Pide un entero >= minimo; repite hasta recibir un dato válido."""
    while True:
        texto = input(mensaje).strip()
        try:
            valor = int(texto)
        except ValueError:
            print("   Dato inválido. Ingrese un número entero.")
            continue
        if valor < minimo:
            print(f"   Ingrese un número mayor o igual que {minimo}.")
            continue
        return valor


def elegir_turno(actual=None):
    """Muestra los turnos numerados y devuelve el elegido.
    Si 'actual' no es None, Enter conserva el turno actual."""
    nombres = list(turnos)
    for i, nombre in enumerate(nombres, 1):
        print(f"   {i}. {nombre}")
    while True:
        texto = input("   Turno (número): ").strip()
        if texto == "" and actual is not None:
            return actual
        try:
            numero = int(texto)
        except ValueError:
            print("   Dato inválido. Ingrese el número del turno.")
            continue
        if 1 <= numero <= len(nombres):
            return nombres[numero - 1]
        print("   Número fuera de rango.")


def normalizar_docente(nombre):
    """Si el docente ya existe (sin distinguir mayúsculas), reutiliza su
    escritura para que la restricción R1 detecte al mismo docente."""
    for curso in cursos:
        if curso["docente"].casefold() == nombre.casefold():
            return curso["docente"]
    return nombre


def listar_cursos():
    print()
    if not cursos:
        print("[!] No hay cursos registrados.")
        return
    print(f"{'N°':<4}{'Curso':<29}{'Docente':<18}{'Est.':<6}Turno")
    for i, c in enumerate(cursos, 1):
        print(f"{i:<4}{c['nombre']:<29}{c['docente']:<18}"
              f"{c['estudiantes']:<6}{c['turno']}")


def pedir_numero_curso(mensaje):
    """Devuelve el índice (base 0) del curso elegido o None si no existe."""
    numero = leer_entero(mensaje, minimo=0)
    if 1 <= numero <= len(cursos):
        return numero - 1
    print("[!] Número fuera de rango.")
    return None


# --------------------------------------------------------------
# Gestión de cursos
# --------------------------------------------------------------
def registrar_curso():
    print("\n--- Registrar curso ---")
    nombre = input("Nombre del curso: ").strip()
    docente = input("Docente: ").strip()
    if not nombre or not docente:
        print("[!] El nombre del curso y el docente no pueden quedar vacíos.")
        return
    if any(c["nombre"].casefold() == nombre.casefold() for c in cursos):
        print("[!] Ya existe un curso con ese nombre.")
        return
    docente = normalizar_docente(docente)
    estudiantes = leer_entero("Cantidad de estudiantes: ")
    turno = elegir_turno()
    cursos.append({"nombre": nombre, "docente": docente,
                   "estudiantes": estudiantes, "turno": turno})
    print("Curso registrado correctamente.")


def editar_curso():
    listar_cursos()
    if not cursos:
        return
    indice = pedir_numero_curso("N° de curso a editar: ")
    if indice is None:
        return
    curso = cursos[indice]

    docente = input(f"Docente [{curso['docente']}]: ").strip()
    if docente:
        curso["docente"] = normalizar_docente(docente)

    while True:
        texto = input(f"Estudiantes [{curso['estudiantes']}]: ").strip()
        if texto == "":
            break
        try:
            cantidad = int(texto)
        except ValueError:
            print("   Dato inválido. Ingrese un número entero.")
            continue
        if cantidad < 1:
            print("   Ingrese un número mayor o igual que 1.")
            continue
        curso["estudiantes"] = cantidad
        break

    curso["turno"] = elegir_turno(actual=curso["turno"])
    print("Curso actualizado.")


def eliminar_curso():
    listar_cursos()
    if not cursos:
        return
    indice = pedir_numero_curso("N° de curso a eliminar: ")
    if indice is None:
        return
    curso = cursos.pop(indice)
    print(f"Curso '{curso['nombre']}' eliminado.")


# --------------------------------------------------------------
# Configuración de días, turnos y aulas
# --------------------------------------------------------------
def configurar_dias():
    texto = input("Días disponibles separados por coma "
                  "(ej. Lunes,Martes,Jueves): ")
    nuevos = [d.strip().capitalize() for d in texto.split(",") if d.strip()]
    if not nuevos:
        print("[!] No se realizaron cambios.")
        return
    dias[:] = list(dict.fromkeys(nuevos))  # sin repetidos, conserva el orden
    print("Días configurados: " + ", ".join(dias))


def franja_valida(franja):
    """Verifica el formato HH:MM-HH:MM con inicio anterior al fin."""
    try:
        inicio, fin = franja.split("-")
        h1, m1 = (int(x) for x in inicio.split(":"))
        h2, m2 = (int(x) for x in fin.split(":"))
    except ValueError:
        return False
    if not (0 <= h1 < 24 and 0 <= h2 < 24 and 0 <= m1 < 60 and 0 <= m2 < 60):
        return False
    return h1 * 60 + m1 < h2 * 60 + m2


def configurar_turnos():
    print("\nTurnos y franjas actuales:")
    for nombre, franjas in turnos.items():
        print(f"   {nombre}: {', '.join(franjas)}")
    nombres = "/".join(turnos)
    elegido = input(f"Turno a modificar ({nombres}): ").strip()
    turno = next((t for t in turnos if t.casefold() == elegido.casefold()),
                 None)
    if turno is None:
        print("[!] Turno no válido.")
        return
    texto = input("Franjas separadas por coma "
                  "(ej. 08:00-09:30,09:40-11:10): ")
    franjas = [f.strip() for f in texto.split(",") if f.strip()]
    if not franjas or not all(franja_valida(f) for f in franjas):
        print("[!] Franjas no válidas. Use el formato HH:MM-HH:MM.")
        return
    turnos[turno] = list(dict.fromkeys(franjas))
    print(f"Turno {turno}: {', '.join(turnos[turno])}")


def configurar_aulas():
    print("\nAulas actuales:")
    for aula in aulas:
        print(f"   {aula['nombre']} (capacidad {aula['capacidad']})")
    nombre = input("Nombre de nueva aula (Enter para omitir): ").strip()
    if not nombre:
        return
    capacidad = leer_entero("Capacidad máxima: ")
    for aula in aulas:
        if aula["nombre"].casefold() == nombre.casefold():
            aula["capacidad"] = capacidad
            print("Aula actualizada.")
            return
    aulas.append({"nombre": nombre, "capacidad": capacidad})
    print("Aula registrada.")


# --------------------------------------------------------------
# Algoritmo: estrategia voraz + Backtracking con poda
# --------------------------------------------------------------
def ordenar_cursos(lista_cursos):
    """Ordena los cursos de mayor a menor cantidad de estudiantes."""
    return sorted(lista_cursos, key=lambda c: c["estudiantes"], reverse=True)


def generar_opciones(curso):
    """Opciones (día, hora, aula) válidas para un curso."""
    opciones = []
    for dia in dias:
        for hora in turnos[curso["turno"]]:
            for aula in aulas:
                if aula["capacidad"] >= curso["estudiantes"]:
                    opciones.append({
                        "curso": curso["nombre"],
                        "docente": curso["docente"],
                        "estudiantes": curso["estudiantes"],
                        "dia": dia,
                        "turno": curso["turno"],
                        "hora": hora,
                        "aula": aula["nombre"],
                    })
    return opciones


def hay_conflicto(opcion, asignacion):
    """True si la opción choca con una asignación ya realizada."""
    for a in asignacion:
        if a["dia"] == opcion["dia"] and a["hora"] == opcion["hora"]:
            if a["docente"] == opcion["docente"]:   # mismo docente
                return True
            if a["aula"] == opcion["aula"]:         # misma aula
                return True
    return False


def backtracking(lista_cursos, indice, asignacion):
    """Asigna cursos desde 'indice'; True si hay solución completa."""
    estadisticas["nodos"] += 1
    if indice == len(lista_cursos):             # caso base
        return True

    for opcion in generar_opciones(lista_cursos[indice]):
        if hay_conflicto(opcion, asignacion):   # PODA
            estadisticas["podas"] += 1
            continue
        asignacion.append(opcion)               # decisión
        if backtracking(lista_cursos, indice + 1, asignacion):
            return True
        asignacion.pop()                        # retroceso
    return False


# --------------------------------------------------------------
# Generación y presentación del horario
# --------------------------------------------------------------
def generar_horario():
    if not cursos:
        print("\n[!] Registre al menos un curso.")
        return

    estadisticas["nodos"] = 0
    estadisticas["podas"] = 0
    ordenados = ordenar_cursos(cursos)
    asignacion = []

    if not backtracking(ordenados, 0, asignacion):
        print("\n[!] No se encontró una asignación completa.")
        print("    Revise los días, turnos, aulas o la capacidad de las aulas.")
        return

    orden_dias = {d: i for i, d in enumerate(dias)}
    ancho = 86
    print("\n" + "=" * ancho)
    print("HORARIO ACADÉMICO GENERADO".center(ancho))
    print("=" * ancho)
    print(f"{'Día':<10}{'Hora':<14}{'Curso':<26}{'Docente':<18}"
          f"{'Est.':<6}Aula")
    print("-" * ancho)
    for x in sorted(asignacion,
                    key=lambda a: (orden_dias[a["dia"]], a["hora"])):
        print(f"{x['dia']:<10}{x['hora']:<14}{x['curso']:<26}"
              f"{x['docente']:<18}{x['estudiantes']:<6}{x['aula']}")
    print("-" * ancho)
    print(f"Cursos asignados: {len(asignacion)} | "
          f"Nodos explorados: {estadisticas['nodos']} | "
          f"Podas: {estadisticas['podas']}")


# --------------------------------------------------------------
# Menú principal
# --------------------------------------------------------------
def mostrar_menu():
    print("\n" + "=" * 45)
    print("  PLANIFICADOR DE HORARIOS ACADÉMICOS")
    print("=" * 45)
    print(" 1. Registrar curso       5. Configurar días")
    print(" 2. Editar curso          6. Configurar turnos")
    print(" 3. Eliminar curso        7. Configurar aulas")
    print(" 4. Listar cursos         8. Generar horario")
    print(" 0. Salir")


def menu():
    acciones = {
        "1": registrar_curso,
        "2": editar_curso,
        "3": eliminar_curso,
        "4": listar_cursos,
        "5": configurar_dias,
        "6": configurar_turnos,
        "7": configurar_aulas,
        "8": generar_horario,
    }
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()
        if opcion == "0":
            print("Programa finalizado.")
            break
        accion = acciones.get(opcion)
        if accion:
            accion()
        else:
            print("[!] Opción no válida.")


if __name__ == "__main__":
    menu()
