from flask import Flask, render_template, Response
import cv2
import mediapipe as mp
import numpy as np
import os

# Inicializa Flask
app = Flask(__name__)

# Inicializa MediaPipe para la detección de manos
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Carpeta que contiene los gestos almacenados
GESTURE_FOLDER = r'C:\Users\Trabajo\Documents\GitHub\DSIALESPG2\capturas_gestos'

# Función para cargar los gestos almacenados
def cargar_gestos_almacenados():
    gestos_almacenados = {}
    for archivo in os.listdir(GESTURE_FOLDER):
        if archivo.endswith('_landmarks.npy'):
            letra = archivo.split('_')[0]
            landmarks = np.load(os.path.join(GESTURE_FOLDER, archivo))
            gestos_almacenados[letra] = landmarks
    return gestos_almacenados

# Cargar los gestos al iniciar el servidor
gestos_almacenados = cargar_gestos_almacenados()

# Función para normalizar los landmarks
def normalizar_landmarks(landmarks):
    muñeca = landmarks[0]
    normalizados = []
    for lm in landmarks:
        normalizados.append([(lm[0] - muñeca[0]), (lm[1] - muñeca[1]), (lm[2] - muñeca[2])])
    return np.array(normalizados)

# Función para procesar el video de la cámara y detectar gestos
def generar_stream():
    cap = cv2.VideoCapture(0)
    with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convertir la imagen de BGR a RGB
            imagen_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultado = hands.process(imagen_rgb)

            if resultado.multi_hand_landmarks:
                for hand_landmarks in resultado.multi_hand_landmarks:
                    # Dibujar los landmarks en la imagen
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Normalizar los landmarks
                    landmarks_norm = normalizar_landmarks(np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]))

                    # Comparar con gestos almacenados
                    for letra, gesto in gestos_almacenados.items():
                        if np.allclose(gesto, landmarks_norm, atol=0.1):  # Ajusta el umbral según sea necesario
                            cv2.putText(frame, f'Gesto: {letra}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Convertir la imagen a formato JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Enviar el flujo de video
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

# Ruta para el flujo de video
@app.route('/video_feed')
def video_feed():
    return Response(generar_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Ruta para la página de practicar LS
@app.route('/practicarLS')
def practicarLS():
    return render_template('practicarLS.html')

# Iniciar la aplicación
if __name__ == "__main__":
    app.run(debug=True)
