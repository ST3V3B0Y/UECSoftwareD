from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import (
    login_required,
    login_manager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
)
from sqlalchemy.exc import IntegrityError  # Para manejar errores de integridad de BD
from sqlalchemy import or_  # Para condiciones OR en consultas
from werkzeug.security import check_password_hash, generate_password_hash  # Para manejo seguro de contraseñas
from flask import jsonify  # Para respuestas JSON
from app import db, login_manager  # Instancias de la aplicación
from app.models.facultad import Facultad  # Modelo de facultades
from app.models.usuario import Usuario  # Modelo de usuarios

# Creación del Blueprint para rutas de usuario
bp = Blueprint("usuario", __name__)

# Manejador para usuarios no autorizados
@login_manager.unauthorized_handler
def unauthorized_callback():
    """Redirige a los usuarios no autenticados a la página de login con mensaje"""
    flash("Por favor inicia sesión para acceder a esta página.", "error")
    return redirect(url_for("usuario.login"))


@bp.route("/usuario", methods=['GET','POST'])
def indexUsuario():
    """
    Vista principal de gestión de usuarios
    
    GET: Muestra listado completo de usuarios con sus facultades
    POST: Filtra usuarios según término de búsqueda (nombre, identificación o facultad)
    """
    if current_user.is_authenticated:
        if request.method == 'GET':
            # Consulta todos los usuarios con su facultad
            usuarios = (db.session.query(
                Usuario.identificacionUsuario, 
                Usuario.nombreUsuario, 
                Facultad.nombreFacultad)
                .join(Usuario, Usuario.Facultad_idFacultad==Facultad.idFacultad)
                .all())
            return render_template('administracion/usuarios/usuarios.html', usuarios=usuarios)
        
        if request.method == 'POST':
            # Búsqueda filtrada de usuarios
            usuario_a_buscar = request.form.get('usuario')
            usuarios = (
                db.session.query(
                    Usuario.identificacionUsuario, 
                    Usuario.nombreUsuario, 
                    Facultad.nombreFacultad)
                .join(Facultad, Usuario.Facultad_idFacultad==Facultad.idFacultad)
                .filter(
                    or_(
                        Usuario.nombreUsuario.ilike(f"%{usuario_a_buscar}%"),  # Búsqueda parcial por nombre
                        Usuario.identificacionUsuario == usuario_a_buscar,  # Búsqueda exacta por documento
                        Facultad.nombreFacultad.ilike(f"%{usuario_a_buscar}%")  # Búsqueda parcial por facultad
                    )).all()
                )
            return render_template('administracion/usuarios/usuarios.html', usuarios=usuarios)
    else:
        flash("Inicie sesión para continuar...", "error")
        return redirect(url_for('usuario.login_administracion'))


@bp.route("/register_usuario", methods=["GET", "POST"])
def register_usuario():
    """
    Registro de nuevos usuarios
    
    GET: Muestra formulario de registro con listado de facultades
    POST: Procesa el registro de nuevos usuarios
    """
    if request.method == "GET":
        facultad = Facultad.query.all()
        return render_template("usuario/register_usuarios.html", facultad=facultad)
    
    if request.method == "POST":
        # Obtención de datos del formulario
        documento = request.form["documento"]
        nombre = request.form["nombre"]
        facultad = request.form.get('facultad')
        
        # Validación de usuario existente
        identificacionUsuario = Usuario.query.filter_by(identificacionUsuario=documento).count()

        if not facultad or not nombre:
            return {"status": "error", "message": "Complete todos los campos"}, 400
        elif identificacionUsuario > 0:
            return {"status": "warning", "message": "Identificación ya registrada"}, 400
        else:
            # Creación del nuevo usuario
            usuario = Usuario(
                usuario=None,
                contraseña=None,
                nombreUsuario=nombre,
                identificacionUsuario=documento,
                Facultad_idFacultad=facultad,
            )
            try:
                db.session.add(usuario)
                db.session.commit()
                usuarioActual = Usuario.query.filter_by(identificacionUsuario=documento).first()
                login_user(usuarioActual)  # Autologin después del registro
                return {"status": "success", "message": "Registro exitoso"}, 200
            except IntegrityError as e:
                db.session.rollback()
                return {"status": "error", "message": "Error en el registro"}, 400


@bp.route("/login_usuario", methods=["GET", "POST"])
def login_usuario():
    """
    Login para usuarios regulares (no administradores)
    
    GET: Redirige al formulario de login
    POST: Autentica al usuario mediante identificación
    """
    if request.method == "GET":
        return redirect(url_for('usuario.login'))
    
    if request.method == "POST":
        identificacion = request.form.get("documento")
        if identificacion:
            usuarioActual = Usuario.query.filter_by(
                identificacionUsuario=identificacion
            ).first()
            if usuarioActual:
                login_user(usuarioActual)
                return jsonify({
                    "success": True, 
                    "redirect": url_for("equipo.equipo")
                })
            else:
                return jsonify({
                    "success": False, 
                    "message": "Usted no está registrado en el sistema..."
                })
    return jsonify({"success": False, "message": "Error en la solicitud."})


@bp.route("/login")
def login():
    """Muestra el formulario de login para usuarios regulares"""
    if request.method == "GET":
        return render_template("usuario/login_usuarios.html")
    

@bp.route("/login_administracion", methods=["GET","POST"])
def login_administracion():
    """
    Login para administradores
    
    GET: Muestra formulario de login
    POST: Valida credenciales de administrador
    """
    if request.method == "GET":
        return render_template("administracion/login_administracion.html")
    
    if request.method == "POST":
        usuario = request.form.get("usuario")
        contraseña = request.form.get("contraseña")
        user = Usuario.query.filter_by(usuario=usuario).first()
        
        if user:
            # NOTA: Se recomienda usar check_password_hash en lugar de comparación directa
            if user.contraseña == contraseña:
                login_user(user)
                return redirect(url_for('usuario.administracion'))
            else:
                flash("Usuario o contraseña incorrectos.", "error")
                return redirect(url_for('usuario.login_administracion')) 
        else:
            flash("Usuario o contraseña incorrectos.", "error")
            return redirect(url_for('usuario.login_administracion')) 


@bp.route("/administracion", methods=["GET","POST"])
def administracion():
    """Panel de administración (acceso restringido)"""
    if current_user.is_authenticated:
        if request.method == "GET":
            return render_template("administracion/administracion.html")
    else:
        flash("Inicie sesión para continuar...", "error")
        return redirect(url_for('usuario.login_administracion'))


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Cierra la sesión del usuario actual"""
    logout_user()
    return redirect(url_for('index'))


@bp.route("/perfil", methods=["GET","POST"])
@login_required
def perfil():
    """Vista del perfil de usuario (requiere autenticación)"""
    if request.method == "GET":
        return render_template("usuario/usuarios.html")