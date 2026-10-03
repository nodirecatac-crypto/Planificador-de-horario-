# ==============================================================
# EXPERIMENTOS DEL INFORME (Tablas 2, 3 y 4)
# Compara Fuerza Bruta, Backtracking con poda y Programación Dinámica,
# y mide el efecto del orden voraz. Usa el módulo horario_academico.py
# (deben estar en la misma carpeta). Ejecutar:  python experimentos.py
# ==============================================================
import itertools
import random
import statistics
import time

import horario_academico as h


# --------------------------------------------------------------
# Configuración de las instancias
# --------------------------------------------------------------
def configurar(dias, franjas, aulas):
    """Fija la configuración global que usa horario_academico."""
    h.dias[:] = dias
    h.turnos.clear()
    h.turnos["T"] = franjas
    h.aulas[:] = [{"nombre": n, "capacidad": c} for n, c in aulas]


def curso(nombre, docente, estudiantes, turno="T"):
    return {"nombre": nombre, "docente": docente,
            "estudiantes": estudiantes, "turno": turno}


# --------------------------------------------------------------
# Variante 1: Backtracking con poda (el del sistema)
# --------------------------------------------------------------
def correr_backtracking(lista_ordenada):
    h.estadisticas["nodos"] = 0
    h.estadisticas["podas"] = 0
    asignacion = []
    ok = h.backtracking(lista_ordenada, 0, asignacion)
    return ok, h.estadisticas["nodos"], h.estadisticas["podas"]


# --------------------------------------------------------------
# Variante 2: Fuerza Bruta (genera todas las combinaciones y valida)
# --------------------------------------------------------------
def correr_fuerza_bruta(lista_ordenada):
    listas = [h.generar_opciones(c) for c in lista_ordenada]
    evaluadas = 0
    for combinacion in itertools.product(*listas):
        evaluadas += 1
        valida = True
        for i, opcion in enumerate(combinacion):
            if h.hay_conflicto(opcion, combinacion[:i]):
                valida = False
                break
        if valida:
            return True, evaluadas
    return False, evaluadas


# --------------------------------------------------------------
# Variante 3: Programación Dinámica descendente (memorización)
# Estado: (curso actual, aulas ocupadas, docentes ocupados)
# --------------------------------------------------------------
def correr_prog_dinamica(lista_ordenada):
    listas = [h.generar_opciones(c) for c in lista_ordenada]
    memo = set()                    # estados ya explorados sin solución
    contadores = {"estados": 0, "reutilizados": 0}

    def resolver(i, ocup_aula, ocup_doc):
        if i == len(lista_ordenada):
            return True
        estado = (i, ocup_aula, ocup_doc)
        if estado in memo:
            contadores["reutilizados"] += 1
            return False
        contadores["estados"] += 1
        for op in listas[i]:
            clave_aula = (op["dia"], op["hora"], op["aula"])
            clave_doc = (op["dia"], op["hora"], op["docente"])
            if clave_aula in ocup_aula or clave_doc in ocup_doc:
                continue
            if resolver(i + 1, ocup_aula | {clave_aula},
                        ocup_doc | {clave_doc}):
                return True
        memo.add(estado)
        return False

    ok = resolver(0, frozenset(), frozenset())
    return ok, contadores["estados"], contadores["reutilizados"]


def mediana_ms(funcion, repeticiones):
    tiempos = []
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        funcion()
        tiempos.append((time.perf_counter() - t0) * 1000)
    return statistics.median(tiempos)


# --------------------------------------------------------------
# Tabla 3: comparación de los tres algoritmos
# --------------------------------------------------------------
def tabla3():
    print("\nTABLA 3. Fuerza Bruta vs Backtracking con poda vs Prog. Dinámica")
    print("Config.: 2 días, 1 turno de 2 franjas, 2 aulas (40 y 60); "
          "un solo docente (4 bloques)")
    configurar(["Lunes", "Martes"], ["08:00-09:30", "09:40-11:10"],
               [("A", 40), ("B", 60)])
    print(f"{'n':<3}{'Resultado':<13}{'FB comb.':>11}{'FB ms':>10}"
          f"{'BT nodos':>10}{'BT ms':>8}{'PD estados':>12}{'PD reutil.':>12}")
    for n in (4, 5, 6, 7):
        cursos = [curso(f"C{i}", "Docente", 30) for i in range(n)]
        orden = h.ordenar_cursos(cursos)
        reps = 3 if n == 7 else 5
        ok_fb, comb = correr_fuerza_bruta(orden)
        t_fb = mediana_ms(lambda: correr_fuerza_bruta(orden), reps)
        ok_bt, nodos, _ = correr_backtracking(orden)
        t_bt = mediana_ms(lambda: correr_backtracking(orden), reps)
        ok_pd, estados, reutil = correr_prog_dinamica(orden)
        resultado = "Con solución" if ok_bt else "Sin solución"
        assert ok_fb == ok_bt == ok_pd
        print(f"{n:<3}{resultado:<13}{comb:>11,}{t_fb:>10.1f}"
              f"{nodos:>10}{t_bt:>8.1f}{estados:>12}{reutil:>12}"
              .replace(",", " "))


# --------------------------------------------------------------
# Instancias con solución (4 docentes distintos) y configuración completa
# --------------------------------------------------------------
def instancias_con_solucion():
    print("\nInstancias con solución (cursos de 4 docentes distintos)")
    configurar(["Lunes", "Martes"], ["08:00-09:30", "09:40-11:10"],
               [("A", 40), ("B", 60)])
    for n in range(4, 8):
        cursos = [curso(f"C{i}", f"Docente {i % 4}", 30) for i in range(n)]
        orden = h.ordenar_cursos(cursos)
        ok, nodos, _ = correr_backtracking(orden)
        _, comb = correr_fuerza_bruta(orden)
        print(f"  n={n}: solución={ok}  BT nodos={nodos}  FB combinaciones={comb}")

    print("\nConfiguración completa del sistema (5 días, 3 turnos, 3 aulas)")
    h.dias[:] = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    h.turnos.clear()
    h.turnos.update({
        "Mañana": ["08:00-09:30", "09:40-11:10", "11:20-12:50"],
        "Tarde": ["14:00-15:30", "15:40-17:10", "17:20-18:50"],
        "Noche": ["19:00-20:30", "20:40-22:10"],
    })
    h.aulas[:] = [{"nombre": "A-101", "capacidad": 30},
                  {"nombre": "A-102", "capacidad": 40},
                  {"nombre": "B-201", "capacidad": 60}]
    nombres_turno = list(h.turnos)
    for n in (10, 20, 30, 40):
        cursos = [curso(f"C{i}", f"Docente {i}", 25 + i % 30,
                        nombres_turno[i % 3]) for i in range(n)]
        orden = h.ordenar_cursos(cursos)
        t0 = time.perf_counter()
        ok, nodos, _ = correr_backtracking(orden)
        ms = (time.perf_counter() - t0) * 1000
        print(f"  n={n}: solución={ok}  nodos={nodos}  tiempo={ms:.2f} ms")


# --------------------------------------------------------------
# Tabla 4: efecto del orden de los cursos (200 instancias factibles)
# --------------------------------------------------------------
def instancia_aleatoria(rnd):
    n = rnd.randint(9, 12)
    return [curso(f"C{i}", f"Docente {rnd.randint(1, 6)}",
                  rnd.randint(15, 58)) for i in range(n)]


def tabla4(cantidad=200, semilla=11):
    print(f"\nTABLA 4. Efecto del orden ({cantidad} instancias factibles, "
          f"semilla {semilla})")
    configurar(["Lunes", "Martes"], ["08:00-09:30", "09:40-11:10"],
               [("A-101", 30), ("A-102", 40), ("B-201", 60)])
    rnd = random.Random(semilla)
    resultados = {"Voraz": [], "Orden de ingreso": [], "Ascendente": []}
    while len(resultados["Voraz"]) < cantidad:
        cursos = instancia_aleatoria(rnd)
        voraz = h.ordenar_cursos(cursos)
        ok, nodos_voraz, _ = correr_backtracking(voraz)
        if not ok:                       # solo instancias factibles
            continue
        resultados["Voraz"].append(nodos_voraz)
        _, nodos, _ = correr_backtracking(cursos)
        resultados["Orden de ingreso"].append(nodos)
        asc = sorted(cursos, key=lambda c: c["estudiantes"])
        _, nodos, _ = correr_backtracking(asc)
        resultados["Ascendente"].append(nodos)
    base = statistics.mean(resultados["Voraz"])
    print(f"{'Orden':<20}{'Nodos prom.':>13}{'Nodos máx.':>12}{'Veces':>8}")
    for nombre, lista in resultados.items():
        prom = statistics.mean(lista)
        print(f"{nombre:<20}{prom:>13.1f}{max(lista):>12,}{prom / base:>8.0f}"
              .replace(",", " "))


if __name__ == "__main__":
    tabla3()
    instancias_con_solucion()
    tabla4()
