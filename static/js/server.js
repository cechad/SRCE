require('dotenv').config();
const express = require('express');
const session = require('express-session');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const mysql = require('mysql2');

// Crear una app de Express
const app = express();

// Configurar sesión
app.use(session({
    secret: 'mi_secreto',  // Cambia esto por una clave más segura
    resave: false,
    saveUninitialized: true
}));

// Inicializar Passport
app.use(passport.initialize());
app.use(passport.session());

// Conectar a MySQL
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',  // Cambia esto a tu usuario de MySQL
    password: 'password',  // Cambia esto a tu contraseña de MySQL
    database: 'DSIALESPG2'  // Nombre de tu base de datos
});

// Estrategia de autenticación con Google
passport.use(new GoogleStrategy({
    clientID: process.env.GOOGLE_CLIENT_ID,   // Define estas variables en el archivo .env
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: "/auth/google/callback"
  },
  function(accessToken, refreshToken, profile, done) {
    // Verificar si el usuario ya existe en la base de datos
    const email = profile.emails[0].value;
    db.query('SELECT * FROM USUARIOS WHERE EMAIL = ?', [email], (err, results) => {
        if (err) return done(err);
        if (results.length > 0) {
            // Usuario encontrado
            return done(null, results[0]);
        } else {
            // Nuevo usuario, insertar en la tabla USUARIOS
            const newUser = {
                NOMBRE_USUARIO: profile.displayName,
                EMAIL: email,
                CONTRASEÑA: '',  // Vacío porque es autenticación de Google
                FECHA_REGISTRO: new Date()
            };
            db.query('INSERT INTO USUARIOS SET ?', newUser, (err, res) => {
                if (err) return done(err);
                newUser.ID_USUARIO = res.insertId;
                return done(null, newUser);
            });
        }
    });
  }
));

// Serializar y deserializar el usuario en la sesión
passport.serializeUser((user, done) => {
    done(null, user.ID_USUARIO);
});

passport.deserializeUser((id, done) => {
    db.query('SELECT * FROM USUARIOS WHERE ID_USUARIO = ?', [id], (err, results) => {
        if (err) return done(err);
        done(null, results[0]);
    });
});

// Ruta para iniciar sesión con Google
app.get('/auth/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

// Ruta de callback de Google
app.get('/auth/google/callback', 
  passport.authenticate('google', { failureRedirect: '/' }),
  function(req, res) {
    // Usuario autenticado, redirigir al home
    res.redirect('/home');
  }
);

// Ruta protegida (solo accesible si el usuario está autenticado)
app.get('/home', (req, res) => {
    if (!req.isAuthenticated()) {
        return res.redirect('/');
    }
    res.send(`Hola, ${req.user.NOMBRE_USUARIO}. Bienvenido a la aplicación.`);
});

// Iniciar el servidor
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Servidor corriendo en el puerto ${PORT}`);
});
