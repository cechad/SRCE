from flask import Flask, render_template, request, redirect, url_for, Response, flash, session, send_file
import pyodbc
import cv2
import mediapipe as mp
import numpy as np
import os

# Inicializa Flask
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Cambia esto a una clave secreta

# Configura la conexión a tu base de datos
server = 'DESKTOP-REGL8D7'
database = 'IA_LENSENAS'
conexion_string = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    'Trusted_Connection=yes;'
)

# Configuración de la carpeta de archivos
UPLOAD_FOLDER = 'static/uploads'  # Cambié a una carpeta accesible
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegúrate de que la carpeta de subida existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Inicializa MediaPipe para la detección de manos
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Carpeta que contiene los gestos almacenados
GESTURE_FOLDER = r'C:\Users\Trabajo\Documents\GitHub\DSIALESPG2\capturas_gestos'

# ========================================
# Funciones auxiliares
# ========================================

# Función para cargar los gestos almacenados
def cargar_gestos_almacenados():
    gestos_almacenados = {}
    for archivo in os.listdir(GESTURE_FOLDER):
        if archivo.endswith('_landmarks.npy'):
            letra = archivo.split('_')[0]
            landmarks = np.load(os.path.join(GESTURE_FOLDER, archivo))
            gestos_almacenados[letra] = landmarks
    return gestos_almacenados

# Función para normalizar los landmarks
def normalizar_landmarks(landmarks):
    muñeca = landmarks[0]
    normalizados = []
    for lm in landmarks:
        normalizados.append([(lm[0] - muñeca[0]), (lm[1] - muñeca[1]), (lm[2] - muñeca[2])])
    return np.array(normalizados)

# Cargar los gestos al iniciar el servidor
gestos_almacenados = cargar_gestos_almacenados()

# ========================================
# Funciones para video y gestos
# ========================================

# Función para procesar el video de la cámara y detectar gestos
def generar_stream():
    cap = cv2.VideoCapture(0)  # Índice de la cámara
    with mp_hands.Hands(static_image_mode=False, max_num_hands=1, 
                        min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultado = hands.process(frame_rgb)

            if resultado.multi_hand_landmarks:
                for hand_landmarks in resultado.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    landmark_coords_actual = [[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]
                    landmark_coords_actual_normalizados = normalizar_landmarks(landmark_coords_actual)

                    letra_detectada = None
                    menor_diferencia = float('inf')

                    # Comparar los landmarks actuales con los gestos almacenados
                    for letra, landmarks_guardados in gestos_almacenados.items():
                        diferencias = [np.mean(np.abs(landmarks_guardados[i] - landmark_coords_actual_normalizados)) 
                                       for i in range(len(landmarks_guardados))]
                        diferencia_promedio = np.mean(diferencias)

                        if diferencia_promedio < menor_diferencia:
                            menor_diferencia = diferencia_promedio
                            letra_detectada = letra

                    muñeca = hand_landmarks.landmark[0]
                    h, w, _ = frame.shape
                    x_text = int(muñeca.x * w)
                    y_text = int(muñeca.y * h) - 20

                    if letra_detectada and menor_diferencia < 0.02:  # Umbral de diferencia
                        texto = f'Letra: {letra_detectada}'
                        color = (0, 255, 0)  # Verde si la letra fue detectada correctamente
                    else:
                        texto = 'Letra no reconocida'
                        color = (0, 0, 255)  # Rojo si no coincide

                    cv2.putText(frame, texto, (x_text, y_text), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

# ========================================
# Rutas de la aplicación
# ========================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    contraseña = request.form.get('password')

    try:
        conexion = pyodbc.connect(conexion_string)
        cursor = conexion.cursor()

        cursor.execute(""" 
            SELECT us.UsuarioID, us.RolID 
            FROM InicioDeSesion sesion 
            JOIN Usuarios us ON sesion.UsuarioID = us.UsuarioID 
            WHERE sesion.Email = ? AND sesion.Contraseña = ? 
        """, (email, contraseña))

        usuario = cursor.fetchone()

        if usuario:
            session['usuario_id'] = usuario[0]
            session['rol_id'] = usuario[1]

            # Depuración de roles y redirección
            print(f"Usuario ID: {session['usuario_id']}, Rol ID: {session['rol_id']}")

            if usuario[1] == 1:  # Admin
                return redirect(url_for('admin'))
            elif usuario[1] == 2:  # Maestro
                return redirect(url_for('teacher'))
            elif usuario[1] == 3:  # Estudiante
                return redirect(url_for('practicarLS'))
        else:
            flash("Credenciales incorrectas.")
            return redirect(url_for('index'))

    except pyodbc.Error as e:
        print("Error al conectar a la base de datos:", e)
        flash("Error en la conexión.")
        return redirect(url_for('index'))

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

# Función para verificar la extensión del archivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf']

@app.route('/subir_archivo', methods=['POST'])
def subir_archivo():
    if 'archivo' not in request.files:
        flash('No se ha seleccionado ningún archivo.')
        return redirect(url_for('salon'))

    archivo = request.files['archivo']

    if archivo.filename == '':
        flash('No se ha seleccionado ningún archivo.')
        return redirect(url_for('salon'))

    # Determinar visibilidad (por ejemplo, desde un formulario)
    tipo_visibilidad = request.form.get('tipo_visibilidad')  # 'maestro', 'estudiante', 'ambos'

    if archivo and allowed_file(archivo.filename):
        # Guardar el archivo en la carpeta de uploads
        ruta_archivo = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
        archivo.save(ruta_archivo)

        # Guardar información en la base de datos
        try:
            conexion = pyodbc.connect(conexion_string)
            cursor = conexion.cursor()
            # Inserta el archivo en la tabla
            cursor.execute("""
                INSERT INTO Archivos (UsuarioID, NombreArchivo, TipoVisibilidad) 
                VALUES (?, ?, ?)
            """, (session['usuario_id'], archivo.filename, tipo_visibilidad))

            conexion.commit()  # Confirma la transacción
            flash('Archivo subido y registrado correctamente.')
        except pyodbc.Error as e:
            print("Error al insertar en la base de datos:", e)
            flash('Error al guardar el archivo en la base de datos.')
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

        return redirect(url_for('mostrar_pdf'))  # Redirigir a la página que muestra los archivos

    flash('Formato de archivo no permitido. Solo se aceptan archivos PDF.')
    return redirect(url_for('salon'))

# Ruta para mostrar archivos PDF
@app.route('/mostrar_pdf')
def mostrar_pdf():
    # Obtiene la lista de archivos PDF en la carpeta de subida
    archivos = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.pdf')]
    return render_template('mostrar_pdf.html', archivos=archivos)

@app.route('/ver_pdf/<archivo>')
def ver_pdf(archivo):
    ruta_archivo = os.path.join(app.config['UPLOAD_FOLDER'], archivo)
    return send_file(ruta_archivo, as_attachment=False)

# Rutas de roles y páginas específicas
@app.route('/admin')
def admin():
    if 'rol_id' in session and session['rol_id'] in [1,2, 3]: 
        return render_template('admin.html')
    else:
        return redirect(url_for('admin'))

@app.route('/teacher')
def teacher():
    if 'rol_id' in session and session['rol_id'] == 2:
        return render_template('teacher.html')
    else:
        return redirect(url_for('teacher'))

@app.route('/student')
def student():
    if 'rol_id' in session and session['rol_id'] == 3:
        return render_template('student.html')
    else:
        return redirect(url_for('student'))

@app.route('/practicarLS')
def practicarLS():
    if 'rol_id' in session and session['rol_id'] in [2, 3]:  # Maestro o Estudiante
        return render_template('practicarLS.html')
    else:
        return redirect(url_for('practicarLS'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/salon')
def salon():
    if 'rol_id' in session and session['rol_id'] == 2:  # Solo para Maestros
        return render_template('salon.html')
    else:
        return redirect(url_for('salon'))

@app.route('/video_feed')
def video_feed():
    return Response(generar_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ========================================
# Ejecuta la aplicación
# ========================================
if __name__ == '__main__':
    app.run(debug=True)
