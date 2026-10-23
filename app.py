import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder=BASE_DIR)
app.secret_key = 'transmetro_cco_crud_secret_key'

from db import (
    init_tables, guardar_registro, obtener_historial,
    obtener_rutas, guardar_ruta, actualizar_ruta, eliminar_ruta,
    obtener_buses, guardar_bus, actualizar_bus, eliminar_bus,
    obtener_estaciones, guardar_estacion, actualizar_estacion, eliminar_estacion,
    obtener_pilotos, guardar_piloto, actualizar_piloto, eliminar_piloto
)

init_tables()

# ==========================================
# RUTAS DE ACCESO (LOGIN / LOGOUT)
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # Captura tanto de formulario tradicional (x-www-form-urlencoded) como de JSON
        usuario = (request.form.get('usuario') or (request.json and request.json.get('usuario')) or '').strip().upper()
        password = (request.form.get('password') or (request.json and request.json.get('password')) or '').strip()

        # Validación estricta de credenciales oficiales
        if (usuario == 'SYSTEM' and password == 'oracle') or (usuario == 'ADMIN' and password == 'admin123'):
            session['usuario'] = usuario
            if request.is_json:
                return jsonify({"status": "success", "redirect": url_for('dashboard')})
            return redirect(url_for('dashboard'))
        else:
            error = "Credenciales incorrectas. Verifique usuario y contraseña."
            if request.is_json:
                return jsonify({"status": "error", "mensaje": error}), 401
            
    return render_template('login.html', error=error)

@app.route('/logout')
@app.route('/logout.html')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ==========================================
# VISTAS PRINCIPALES (GESTIÓN, TERMINAL, REPORTES)
# ==========================================
@app.route('/')
@app.route('/index.html')
@app.route('/dashboard')
@app.route('/gestion')
@app.route('/gestion.html')
def dashboard():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/terminal')
@app.route('/terminal.html')
def terminal():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    return render_template('terminal.html')

@app.route('/reportes')
@app.route('/reportes.html')
def reportes():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    return render_template('reportes.html')

# ==========================================
# APIS REST: CRUD DE RUTAS (LÍNEAS)
# ==========================================
@app.route('/api/rutas', methods=['GET', 'POST'])
def handle_rutas():
    if request.method == 'GET':
        return jsonify(obtener_rutas())
    data = request.json or {}
    guardar_ruta(
        data.get('nombre'),
        data.get('origen'),
        data.get('destino'),
        int(data.get('tiempo_espera', 5)),
        data.get('estado', 'Activa')
    )
    return jsonify({"status": "success", "mensaje": "Línea registrada exitosamente"})

@app.route('/api/rutas/<int:id_ruta>', methods=['PUT', 'DELETE'])
def handle_ruta_id(id_ruta):
    if request.method == 'PUT':
        data = request.json or {}
        actualizar_ruta(
            id_ruta,
            data.get('nombre'),
            data.get('origen'),
            data.get('destino'),
            int(data.get('tiempo_espera', 5)),
            data.get('estado', 'Activa')
        )
        return jsonify({"status": "success", "mensaje": "Línea y minutos actualizados"})
    elif request.method == 'DELETE':
        eliminar_ruta(id_ruta)
        return jsonify({"status": "success", "mensaje": "Línea eliminada"})

# ==========================================
# APIS REST: CRUD DE BUSES (FLOTA)
# ==========================================
@app.route('/api/buses', methods=['GET', 'POST'])
def handle_buses():
    if request.method == 'GET':
        return jsonify(obtener_buses())
    data = request.json or {}
    guardar_bus(
        data.get('codigo'),
        data.get('tipo', 'Articulado'),
        int(data.get('capacidad', 160)),
        data.get('linea', 'Línea 12'),
        data.get('estado', 'En Ruta')
    )
    return jsonify({"status": "success", "mensaje": "Unidad registrada"})

@app.route('/api/buses/<int:id_bus>', methods=['PUT', 'DELETE'])
def handle_bus_id(id_bus):
    if request.method == 'PUT':
        data = request.json or {}
        actualizar_bus(
            id_bus,
            data.get('codigo'),
            data.get('tipo'),
            int(data.get('capacidad', 160)),
            data.get('linea'),
            data.get('estado')
        )
        return jsonify({"status": "success", "mensaje": "Bus y estado actualizados"})
    elif request.method == 'DELETE':
        eliminar_bus(id_bus)
        return jsonify({"status": "success", "mensaje": "Unidad retirada"})

# ==========================================
# APIS REST: CRUD DE ESTACIONES
# ==========================================
@app.route('/api/estaciones', methods=['GET', 'POST'])
def handle_estaciones():
    if request.method == 'GET':
        return jsonify(obtener_estaciones())
    data = request.json or {}
    guardar_estacion(
        data.get('nombre'),
        int(data.get('capacidad', 160)),
        data.get('linea', 'Línea 12'),
        data.get('estado', 'Operativa')
    )
    return jsonify({"status": "success", "mensaje": "Estación registrada"})

@app.route('/api/estaciones/<int:id_estacion>', methods=['PUT', 'DELETE'])
def handle_estacion_id(id_estacion):
    if request.method == 'PUT':
        data = request.json or {}
        actualizar_estacion(
            id_estacion,
            data.get('nombre'),
            int(data.get('capacidad', 160)),
            data.get('linea'),
            data.get('estado')
        )
        return jsonify({"status": "success", "mensaje": "Estación y aforo nominal actualizados"})
    elif request.method == 'DELETE':
        eliminar_estacion(id_estacion)
        return jsonify({"status": "success", "mensaje": "Estación eliminada"})

# ==========================================
# APIS REST: CRUD DE PILOTOS
# ==========================================
@app.route('/api/pilotos', methods=['GET', 'POST'])
def handle_pilotos():
    if request.method == 'GET':
        return jsonify(obtener_pilotos())
    data = request.json or {}
    guardar_piloto(
        data.get('codigo'),
        data.get('nombre'),
        data.get('dpi'),
        data.get('unidad', 'Sin asignar'),
        data.get('estado', 'Activo')
    )
    return jsonify({"status": "success", "mensaje": "Piloto registrado"})

@app.route('/api/pilotos/<int:id_piloto>', methods=['PUT', 'DELETE'])
def handle_piloto_id(id_piloto):
    if request.method == 'PUT':
        data = request.json or {}
        actualizar_piloto(
            id_piloto,
            data.get('codigo'),
            data.get('nombre'),
            data.get('dpi'),
            data.get('unidad'),
            data.get('estado')
        )
        return jsonify({"status": "success", "mensaje": "Piloto actualizado"})
    elif request.method == 'DELETE':
        eliminar_piloto(id_piloto)
        return jsonify({"status": "success", "mensaje": "Piloto dado de baja"})

# ==========================================
# REGLAS DE NEGOCIO: AFORO
# ==========================================
@app.route('/api/aforo', methods=['POST'])
def registrar_aforo():
    data = request.json or {}
    pasajeros = int(data.get('pasajeros') or 0)
    capacidad = int(data.get('capacidad') or 160)
    estacion = data.get('estacion') or "Centra Sur"

    umbral_alerta = capacidad * 1.50
    es_sobredemanda = pasajeros >= umbral_alerta
    porcentaje = round((pasajeros / capacidad) * 100, 1)
    estado = "SOBREDEMANDA (+50%)" if es_sobredemanda else "NORMAL"

    guardar_registro(estacion, capacidad, pasajeros, estado)

    return jsonify({
        "status": "success",
        "conteo": pasajeros,
        "capacidad": capacidad,
        "porcentaje": porcentaje,
        "alerta": es_sobredemanda,
        "mensaje": "¡Alerta Crítica! Enviar refuerzo" if es_sobredemanda else "Aforo normal"
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)