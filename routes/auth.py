from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, bcrypt
from models.user import User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    
    # Si ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('orders.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        # Validar campos
        if not username or not password:
            flash('Por favor completa todos los campos.', 'warning')
            return render_template('login.html')
        
        # Buscar usuario
        user = User.query.filter_by(username=username).first()
        
        # Verificar credenciales
        if user and bcrypt.check_password_hash(user.password_hash, password):
            if not user.activo:
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'danger')
                return render_template('login.html')
            
            # Iniciar sesión
            login_user(user, remember=remember)
            user.ultima_conexion = datetime.utcnow()
            db.session.commit()
            
            flash(f'¡Bienvenido, {user.nombre_completo or user.username}!', 'success')
            
            # Redirigir a la página solicitada o al dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('orders.dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Registro de nuevos usuarios (solo admins)"""
    
    # Solo los administradores pueden registrar usuarios
    if not current_user.es_admin():
        flash('No tienes permisos para acceder a esta página.', 'danger')
        return redirect(url_for('orders.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        nombre_completo = request.form.get('nombre_completo')
        rol = request.form.get('rol', 'empleado')
        
        # Validaciones
        if not all([username, email, password, confirm_password]):
            flash('Por favor completa todos los campos obligatorios.', 'warning')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'warning')
            return render_template('register.html')
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('El correo electrónico ya está registrado.', 'danger')
            return render_template('register.html')
        
        # Crear nuevo usuario
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            nombre_completo=nombre_completo,
            rol=rol
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'Usuario {username} registrado exitosamente.', 'success')
        return redirect(url_for('auth.register'))
    
    return render_template('register.html')


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Perfil del usuario"""
    
    if request.method == 'POST':
        nombre_completo = request.form.get('nombre_completo')
        email = request.form.get('email')
        
        # Actualizar datos
        if nombre_completo:
            current_user.nombre_completo = nombre_completo
        
        if email and email != current_user.email:
            # Verificar que el email no esté en uso
            if User.query.filter_by(email=email).first():
                flash('El correo electrónico ya está en uso.', 'danger')
                return render_template('profile.html')
            current_user.email = email
        
        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('profile.html')


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Cambiar contraseña"""
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validaciones
        if not all([current_password, new_password, confirm_password]):
            flash('Por favor completa todos los campos.', 'warning')
            return render_template('change_password.html')
        
        if not bcrypt.check_password_hash(current_user.password_hash, current_password):
            flash('La contraseña actual es incorrecta.', 'danger')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('Las nuevas contraseñas no coinciden.', 'danger')
            return render_template('change_password.html')
        
        if len(new_password) < 6:
            flash('La nueva contraseña debe tener al menos 6 caracteres.', 'warning')
            return render_template('change_password.html')
        
        # Actualizar contraseña
        current_user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        
        flash('Contraseña actualizada correctamente.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('change_password.html')