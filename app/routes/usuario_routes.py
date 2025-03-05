# Importación de módulos necesarios para la aplicación Flask
from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import (
    login_required,
    login_manager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
)
from sqlalchemy.exc import IntegrityError  # Para manejar excepciones de integridad en la base de datos
from sqlalchemy import or_  # Permite usar operadores lógicos en consultas
from werkzeug.security import check_password_hash, generate_password_hash  # Para encriptación de contraseñas
from flask import jsonify  # Para devolver respuestas en formato JSON
from app import db, login_manager  # Instancia de SQLAlchemy (db) y login_manager para gestionar sesiones de usuario
from app.models.facultad import Facultad  # Importa el modelo Facultad
from app.models.usuario import Usuario  # Importa el modelo Usuario

# Creación del Blueprint "usuario" para organizar las rutas relacionadas con usuarios
bp = Blueprint("usuario", __name__)

# Función de manejo de acceso no autorizado: se activa si el usuario no está logueado
@login_manager.unauthorized_handler
def unauthorized_callback():
    flash("Por favor inicia sesión para acceder a esta página.", "error")  # Muestra un mensaje de error
    return redirect(url_for("usuario.login"))  # Redirige a la página de login

# Ruta para mostrar los usuarios en el sistema
@bp.route("/usuario", methods=['GET', 'POST'])
def indexUsuario():
    # Si el usuario está autenticado, muestra la lista de usuarios
    if current_user.is_authenticated:
        if request.method == 'GET':
            # Realiza una consulta para obtener la información de los usuarios con sus facultades asociadas
            usuarios = (db.session.query(Usuario.identificacionUsuario, Usuario.nombreUsuario, Facultad.nombreFacultad)
                        .join(Usuario, Usuario.Facultad_idFacultad == Facultad.idFacultad).all())
            return render_template('administracion/usuarios/usuarios.html', usuarios=usuarios)  # Renderiza la vista con los usuarios

        if request.method == 'POST':
            # Obtiene el término de búsqueda proporcionado por el usuario
            usuario_a_buscar = request.form.get('usuario')
            usuarios = (
                db.session.query(Usuario.identificacionUsuario, Usuario.nombreUsuario, Facultad.nombreFacultad)
                .join(Facultad, Usuario.Facultad_idFacultad == Facultad.idFacultad)
                .filter(
                    or_(
                        Usuario.nombreUsuario.ilike(f"%{usuario_a_buscar}%"),
                        Usuario.identificacionUsuario == usuario_a_buscar,
                        Facultad.nombreFacultad.ilike(f"%{usuario_a_buscar}%")
                    )
                ).all()
            )
            return render_template('administracion/usuarios/usuarios.html', usuarios=usuarios)  # Renderiza la vista con los resultados de la búsqueda
    else:
        flash("Inicie sesión para continuar...", "error")  # Si el usuario no está autenticado, muestra un mensaje de error
        return redirect(url_for('usuario.login_administracion'))  # Redirige al login

# Ruta para registrar un nuevo usuario
@bp.route("/register_usuario", methods=["GET", "POST"])
def register_usuario():
    if request.method == "GET":
        # Obtiene todas las facultades para mostrarlas en el formulario de registro
        facultad = Facultad.query.all()
        return render_template("usuario/register_usuarios.html", facultad=facultad)  # Muestra el formulario de registro
    
    if request.method == "POST":
        # Obtiene los datos enviados desde el formulario
        documento = request.form["documento"]
        nombre = request.form["nombre"]
        facultad = request.form.get('facultad')
        
        # Verifica si el usuario ya existe en la base de datos
        identificacionUsuario = Usuario.query.filter_by(identificacionUsuario=documento).count()

        # Validaciones de los datos ingresados
        if not facultad or not nombre:
            return {"status": "error", "message": "Complete todos los campos"}, 400
        elif len(documento) < 6 or len(documento) > 12:
            return {"status": "error", "message": "Identificación inválida"}, 400
        elif identificacionUsuario > 0:
            return {"status": "warning", "message": "Identificación ya registrada"}, 400
        elif len(nombre) < 7 or len(nombre) == " ":
            return {"status": "error", "message": "Escriba su nombre completo"}, 400
        else:
            # Si todo es válido, crea un nuevo usuario
            usuario = Usuario(
                usuario=None,
                contraseña=None,
                nombreUsuario=nombre,
                identificacionUsuario=documento,
                Facultad_idFacultad=facultad,
            )
            try:
                # Agrega el usuario a la base de datos y hace commit
                db.session.add(usuario)
                db.session.commit()
                # Loguea al nuevo usuario automáticamente
                usuarioActual = Usuario.query.filter_by(identificacionUsuario=documento).first()
                login_user(usuarioActual)
                return {"status": "success", "message": "Registro exitoso"}, 200
            except IntegrityError as e:
                db.session.rollback()  # Si hay un error, revierte la operación
                return {"status": "error", "message": "Error en el registro"}, 400

# Ruta para el login del usuario
@bp.route("/login_usuario", methods=["GET", "POST"])
def login_usuario():
    if request.method == "GET":
        return redirect(url_for('usuario.login'))  # Redirige a la página de login
    if request.method == "POST":
        # Obtiene los datos del formulario de login
        identificacion = request.form.get("documento")
        if identificacion:
            # Busca al usuario en la base de datos
            usuarioActual = Usuario.query.filter_by(identificacionUsuario=identificacion).first()
            if usuarioActual:
                # Si el usuario existe, lo loguea
                login_user(usuarioActual)
                return jsonify({"success": True, "redirect": url_for("equipo.equipo")})  # Redirige al dashboard
            else:
                return jsonify({"success": False, "message": "Usted no está registrado en el sistema..."})  # Si no está registrado
    return jsonify({"success": False, "message": "Error en la solicitud."})  # Si ocurre un error en el proceso

# Ruta para la vista de login
@bp.route("/login")
def login():
    if request.method == "GET":
        return render_template("usuario/login_usuarios.html")  # Muestra la vista de login
    
# Ruta para el login de administración
@bp.route("/login_administracion", methods=["GET", "POST"])
def login_administracion():
    if request.method == "GET":
        return render_template("administracion/login_administracion.html")  # Muestra el formulario de login de administración
    
    if request.method == "POST":
        usuario = request.form.get("usuario")
        contraseña = request.form.get("contraseña")
        # Verifica si el usuario existe en la base de datos
        user = Usuario.query.filter_by(usuario=usuario).first()
        if user:
            if user.contraseña == contraseña:
                login_user(user)  # Si la contraseña es correcta, inicia sesión
                return redirect(url_for('usuario.administracion'))  # Redirige al panel de administración
            else:
                flash("Usuario o contraseña incorrectos.", "error")  # Si la contraseña es incorrecta
                return redirect(url_for('usuario.login_administracion'))  # Redirige al login de administración
        else:
            flash("Usuario o contraseña incorrectos.", "error")  # Si el usuario no existe
            return redirect(url_for('usuario.login_administracion'))  # Redirige al login de administración

# Ruta para la administración del sistema (panel de administración)
@bp.route("/administracion", methods=["GET", "POST"])
def administracion():
    if current_user.is_authenticated:
        if request.method == "GET":
            return render_template("administracion/administracion.html")  # Muestra el panel de administración
    else:
        flash("Inicie sesión para continuar...", "error")
        return redirect(url_for('usuario.login_administracion'))  # Redirige al login si no está autenticado

# Ruta para cerrar sesión
@bp.route("/logout", methods=["POST"])
@login_required  # Solo usuarios autenticados pueden cerrar sesión
def logout():
    logout_user()  # Cierra la sesión del usuario actual
    return redirect(url_for('index'))  # Redirige a la página principal

# Ruta para ver y editar el perfil del usuario
@bp.route("/perfil", methods=["GET", "POST"])
@login_required  # Solo usuarios autenticados pueden acceder a esta ruta
def perfil():
    if request.method == "GET":
        return render_template("usuario/usuarios.html")  # Muestra la vista del perfil

