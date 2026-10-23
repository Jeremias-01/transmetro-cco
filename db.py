import oracledb
from datetime import datetime

# Credenciales exactas Oracle 21c
DB_USER = "SYSTEM"
DB_PASSWORD = "oracle"
DB_HOST = "localhost"
DB_PORT = 1521
DB_SERVICE = "xe"

# Memoria de respaldo local inicial
MEMORIA_RUTAS = [
    {"id": 1, "nombre": "Línea 12 (Eje Sur)", "origen": "Centra Sur", "destino": "Plaza Barrios", "tiempo_espera": 5, "estado": "Activa"},
    {"id": 2, "nombre": "Línea 1 (Centro)", "origen": "San Sebastián", "destino": "Correos", "tiempo_espera": 4, "estado": "Activa"},
    {"id": 3, "nombre": "Línea 7 (Periférico)", "origen": "Roosevelt", "destino": "Universidad", "tiempo_espera": 5, "estado": "Activa"},
    {"id": 4, "nombre": "Línea 13 (Oriente)", "origen": "Hangares", "destino": "Centro Cívico", "tiempo_espera": 5, "estado": "Activa"}
]

MEMORIA_ESTACIONES = [
    {"id": 1, "nombre": "Centra Sur", "capacidad": 160, "linea": "Línea 12", "estado": "Operativa"},
    {"id": 2, "nombre": "El Trébol", "capacidad": 200, "linea": "Línea 12", "estado": "Operativa"},
    {"id": 3, "nombre": "Plaza Barrios", "capacidad": 180, "linea": "Línea 12", "estado": "Operativa"},
    {"id": 4, "nombre": "San Sebastián", "capacidad": 120, "linea": "Línea 1", "estado": "Operativa"},
    {"id": 5, "nombre": "Roosevelt", "capacidad": 170, "linea": "Línea 7", "estado": "Operativa"}
]

MEMORIA_BUSES = [
    {"id": 1, "codigo": "TM-042", "tipo": "Articulado", "capacidad": 160, "linea": "Línea 12", "estado": "En Ruta"},
    {"id": 2, "codigo": "TM-015", "tipo": "Bi-Articulado", "capacidad": 240, "linea": "Línea 12", "estado": "En Ruta"},
    {"id": 3, "codigo": "TM-088", "tipo": "Padrón", "capacidad": 90, "linea": "Línea 1", "estado": "En Bahía"},
    {"id": 4, "codigo": "TM-104", "tipo": "Articulado", "capacidad": 160, "linea": "Línea 7", "estado": "Taller"}
]

MEMORIA_PILOTOS = [
    {"id": 1, "codigo": "PIL-042", "nombre": "Carlos Gómez", "dpi": "2450123450101", "unidad": "TM-042", "estado": "Activo"},
    {"id": 2, "codigo": "PIL-015", "nombre": "Marta Hernández", "dpi": "1890456120101", "unidad": "TM-015", "estado": "Activo"},
    {"id": 3, "codigo": "PIL-088", "nombre": "Luis Morales", "dpi": "1987542310101", "unidad": "TM-088", "estado": "Activo"}
]

MEMORIA_AFORO = []

def get_connection():
    try:
        return oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            service_name=DB_SERVICE
        )
    except Exception:
        return None

def init_tables():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # 1. Tabla Aforo
            cursor.execute("""
                BEGIN
                    EXECUTE IMMEDIATE '
                        CREATE TABLE DEMO_REGISTRO_AFORO (
                            ID_REGISTRO NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            ESTACION VARCHAR2(50),
                            CAPACIDAD_MAXIMA NUMBER,
                            PASAJEROS_ESPERA NUMBER,
                            ESTADO_ALERTA VARCHAR2(30),
                            FECHA_HORA TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )';
                EXCEPTION WHEN OTHERS THEN IF SQLCODE != -955 THEN RAISE; END IF; END;
            """)

            # 2. Tabla Rutas
            cursor.execute("""
                BEGIN
                    EXECUTE IMMEDIATE '
                        CREATE TABLE DEMO_RUTAS (
                            ID_RUTA NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            NOMBRE_RUTA VARCHAR2(100),
                            ORIGEN VARCHAR2(100),
                            DESTINO VARCHAR2(100),
                            TIEMPO_ESPERA NUMBER,
                            ESTADO VARCHAR2(30) DEFAULT ''Activa''
                        )';
                EXCEPTION WHEN OTHERS THEN IF SQLCODE != -955 THEN RAISE; END IF; END;
            """)

            # 3. Tabla Estaciones
            cursor.execute("""
                BEGIN
                    EXECUTE IMMEDIATE '
                        CREATE TABLE DEMO_ESTACIONES (
                            ID_ESTACION NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            NOMBRE VARCHAR2(100),
                            CAPACIDAD NUMBER,
                            LINEA VARCHAR2(100) DEFAULT ''Línea 12'',
                            ESTADO VARCHAR2(30) DEFAULT ''Operativa''
                        )';
                EXCEPTION WHEN OTHERS THEN IF SQLCODE != -955 THEN RAISE; END IF; END;
            """)

            # 4. Tabla Buses
            cursor.execute("""
                BEGIN
                    EXECUTE IMMEDIATE '
                        CREATE TABLE DEMO_BUSES (
                            ID_BUS NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            CODIGO VARCHAR2(20),
                            TIPO VARCHAR2(50),
                            CAPACIDAD NUMBER,
                            LINEA VARCHAR2(100),
                            ESTADO VARCHAR2(30)
                        )';
                EXCEPTION WHEN OTHERS THEN IF SQLCODE != -955 THEN RAISE; END IF; END;
            """)

            # 5. Tabla Pilotos
            cursor.execute("""
                BEGIN
                    EXECUTE IMMEDIATE '
                        CREATE TABLE DEMO_PILOTOS (
                            ID_PILOTO NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            CODIGO VARCHAR2(20),
                            NOMBRE VARCHAR2(100),
                            DPI VARCHAR2(20),
                            UNIDAD VARCHAR2(20),
                            ESTADO VARCHAR2(30) DEFAULT ''Activo''
                        )';
                EXCEPTION WHEN OTHERS THEN IF SQLCODE != -955 THEN RAISE; END IF; END;
            """)

            conn.commit()
            cursor.close()
            print("[DB] Tablas CRUD sincronizadas correctamente en Oracle 21c.")
        except Exception as e:
            print(f"[DB] Error al inicializar tablas: {e}")
        finally:
            conn.close()
    else:
        print("[AVISO] Servidor operando con estructura en memoria lista para sincronizar.")

# ==========================================
# CRUD: RUTAS
# ==========================================
def obtener_rutas():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ID_RUTA, NOMBRE_RUTA, ORIGEN, DESTINO, TIEMPO_ESPERA, NVL(ESTADO, 'Activa') FROM DEMO_RUTAS ORDER BY ID_RUTA DESC")
            filas = cursor.fetchall()
            cursor.close()
            conn.close()
            if filas:
                return [{"id": r[0], "nombre": r[1], "origen": r[2], "destino": r[3], "tiempo_espera": r[4], "estado": r[5]} for r in filas]
        except Exception:
            if conn: conn.close()
    return MEMORIA_RUTAS

def guardar_ruta(nombre, origen, destino, tiempo_espera, estado="Activa"):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO DEMO_RUTAS (NOMBRE_RUTA, ORIGEN, DESTINO, TIEMPO_ESPERA, ESTADO) VALUES (:1, :2, :3, :4, :5)",
                           (nombre, origen, destino, tiempo_espera, estado))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            if conn: conn.close()
    nuevo_id = max([r["id"] for r in MEMORIA_RUTAS], default=0) + 1
    MEMORIA_RUTAS.insert(0, {"id": nuevo_id, "nombre": nombre, "origen": origen, "destino": destino, "tiempo_espera": tiempo_espera, "estado": estado})
    return True

def actualizar_ruta(id_ruta, nombre, origen, destino, tiempo_espera, estado):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE DEMO_RUTAS 
                SET NOMBRE_RUTA = :1, ORIGEN = :2, DESTINO = :3, TIEMPO_ESPERA = :4, ESTADO = :5
                WHERE ID_RUTA = :6
            """, (nombre, origen, destino, tiempo_espera, estado, id_ruta))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            if conn: conn.close()
    for r in MEMORIA_RUTAS:
        if r["id"] == int(id_ruta):
            r.update({"nombre": nombre, "origen": origen, "destino": destino, "tiempo_espera": int(tiempo_espera), "estado": estado})
            break
    return True

def eliminar_ruta(id_ruta):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM DEMO_RUTAS WHERE ID_RUTA = :1", (id_ruta,))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            if conn: conn.close()
    global MEMORIA_RUTAS
    MEMORIA_RUTAS = [r for r in MEMORIA_RUTAS if r["id"] != int(id_ruta)]
    return True

# ==========================================
# CRUD: FLOTA DE BUSES
# ==========================================
def obtener_buses():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ID_BUS, CODIGO, TIPO, CAPACIDAD, LINEA, ESTADO FROM DEMO_BUSES ORDER BY ID_BUS DESC")
            filas = cursor.fetchall()
            cursor.close()
            conn.close()
            if filas:
                return [{"id": r[0], "codigo": r[1], "tipo": r[2], "capacidad": r[3], "linea": r[4], "estado": r[5]} for r in filas]
        except Exception:
            if conn: conn.close()
    return MEMORIA_BUSES

def guardar_bus(codigo, tipo, capacidad, linea, estado):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO DEMO_BUSES (CODIGO, TIPO, CAPACIDAD, LINEA, ESTADO) VALUES (:1, :2, :3, :4, :5)",
                           (codigo, tipo, capacidad, linea, estado))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            if conn: conn.close()
    nuevo_id = max([b["id"] for b in MEMORIA_BUSES], default=0) + 1
    MEMORIA_BUSES.insert(0, {"id": nuevo_id, "codigo": codigo, "tipo": tipo, "capacidad": capacidad, "linea": linea, "estado": estado})
    return True

def actualizar_bus(id_bus, codigo, tipo, capacidad, linea, estado):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE DEMO_BUSES 
                SET CODIGO = :1, TIPO = :2, CAPACIDAD = :3, LINEA = :4, ESTADO = :5
                WHERE ID_BUS = :6
            """, (codigo, tipo, capacidad, linea, estado, id_bus))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            if conn: conn.close()
    for b in MEMORIA_BUSES:
        if b["id"] == int(id_bus):
            b.update({"codigo": codigo, "tipo": tipo, "capacidad": int(capacidad), "linea": linea, "estado": estado})
            break
    return True

def eliminar_bus(id_bus):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM DEMO_BUSES WHERE ID_BUS = :1", (id_bus,))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            if conn: conn.close()
    global MEMORIA_BUSES
    MEMORIA_BUSES = [b for b in MEMORIA_BUSES if b["id"] != int(id_bus)]
    return True

# ==========================================
# CRUD: ESTACIONES
# ==========================================
def obtener_estaciones():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ID_ESTACION, NOMBRE, CAPACIDAD, NVL(LINEA, 'Línea 12'), NVL(ESTADO, 'Operativa') FROM DEMO_ESTACIONES ORDER BY ID_ESTACION DESC")
            filas = cursor.fetchall()
            cursor.close()
            conn.close()
            if filas:
                return [{"id": r[0], "nombre": r[1], "capacidad": r[2], "linea": r[3], "estado": r[4]} for r in filas]
        except Exception:
            if conn: conn.close()
    return MEMORIA_ESTACIONES

def guardar_estacion(nombre, capacidad, linea="Línea 12", estado="Operativa"):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO DEMO_ESTACIONES (NOMBRE, CAPACIDAD, LINEA, ESTADO) VALUES (:1, :2, :3, :4)",
                           (nombre, capacidad, linea, estado))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            if conn: conn.close()
    nuevo_id = max([e["id"] for e in MEMORIA_ESTACIONES], default=0) + 1
    MEMORIA_ESTACIONES.insert(0, {"id": nuevo_id, "nombre": nombre, "capacidad": capacidad, "linea": linea, "estado": estado})
    return True

def actualizar_estacion(id_estacion, nombre, capacidad, linea, estado):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE DEMO_ESTACIONES 
                SET NOMBRE = :1, CAPACIDAD = :2, LINEA = :3, ESTADO = :4
                WHERE ID_ESTACION = :5
            """, (nombre, capacidad, linea, estado, id_estacion))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            if conn: conn.close()
    for e in MEMORIA_ESTACIONES:
        if e["id"] == int(id_estacion):
            e.update({"nombre": nombre, "capacidad": int(capacidad), "linea": linea, "estado": estado})
            break
    return True

def eliminar_estacion(id_estacion):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM DEMO_ESTACIONES WHERE ID_ESTACION = :1", (id_estacion,))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            if conn: conn.close()
    global MEMORIA_ESTACIONES
    MEMORIA_ESTACIONES = [e for e in MEMORIA_ESTACIONES if e["id"] != int(id_estacion)]
    return True

# ==========================================
# CRUD: PILOTOS
# ==========================================
def obtener_pilotos():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ID_PILOTO, CODIGO, NOMBRE, DPI, NVL(UNIDAD, 'Sin asignar'), NVL(ESTADO, 'Activo') FROM DEMO_PILOTOS ORDER BY ID_PILOTO DESC")
            filas = cursor.fetchall()
            cursor.close()
            conn.close()
            if filas:
                return [{"id": r[0], "codigo": r[1], "nombre": r[2], "dpi": r[3], "unidad": r[4], "estado": r[5]} for r in filas]
        except Exception:
            if conn: conn.close()
    return MEMORIA_PILOTOS

def guardar_piloto(codigo, nombre, dpi, unidad="Sin asignar", estado="Activo"):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO DEMO_PILOTOS (CODIGO, NOMBRE, DPI, UNIDAD, ESTADO) VALUES (:1, :2, :3, :4, :5)",
                           (codigo, nombre, dpi, unidad, estado))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            if conn: conn.close()
    nuevo_id = max([p["id"] for p in MEMORIA_PILOTOS], default=0) + 1
    MEMORIA_PILOTOS.insert(0, {"id": nuevo_id, "codigo": codigo, "nombre": nombre, "dpi": dpi, "unidad": unidad, "estado": estado})
    return True

def actualizar_piloto(id_piloto, codigo, nombre, dpi, unidad, estado):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE DEMO_PILOTOS 
                SET CODIGO = :1, NOMBRE = :2, DPI = :3, UNIDAD = :4, ESTADO = :5
                WHERE ID_PILOTO = :6
            """, (codigo, nombre, dpi, unidad, estado, id_piloto))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            if conn: conn.close()
    for p in MEMORIA_PILOTOS:
        if p["id"] == int(id_piloto):
            p.update({"codigo": codigo, "nombre": nombre, "dpi": dpi, "unidad": unidad, "estado": estado})
            break
    return True

def eliminar_piloto(id_piloto):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM DEMO_PILOTOS WHERE ID_PILOTO = :1", (id_piloto,))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            if conn: conn.close()
    global MEMORIA_PILOTOS
    MEMORIA_PILOTOS = [p for p in MEMORIA_PILOTOS if p["id"] != int(id_piloto)]
    return True

# ==========================================
# BITÁCORA Y AFORO
# ==========================================
def guardar_registro(estacion, capacidad, pasajeros, estado):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO DEMO_REGISTRO_AFORO (ESTACION, CAPACIDAD_MAXIMA, PASAJEROS_ESPERA, ESTADO_ALERTA)
                VALUES (:1, :2, :3, :4)
            """, (estacion, capacidad, pasajeros, estado))
            conn.commit()
            cursor.close()
            conn.close()
            return
        except Exception:
            if conn: conn.close()
    MEMORIA_AFORO.insert(0, {
        "estacion": estacion,
        "pasajeros": pasajeros,
        "alerta": estado,
        "hora": datetime.now().strftime("%H:%M:%S")
    })

def obtener_historial():
    conn = get_connection()
    historial = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ESTACION, PASAJEROS_ESPERA, ESTADO_ALERTA, TO_CHAR(FECHA_HORA, 'HH24:MI:SS') 
                FROM DEMO_REGISTRO_AFORO 
                ORDER BY ID_REGISTRO DESC FETCH FIRST 10 ROWS ONLY
            """)
            for r in cursor.fetchall():
                historial.append({"estacion": r[0], "pasajeros": r[1], "alerta": r[2], "hora": r[3]})
            cursor.close()
            conn.close()
            return historial
        except Exception:
            if conn: conn.close()
    return MEMORIA_AFORO[:10]