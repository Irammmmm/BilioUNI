
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import cx_Oracle
from datetime import datetime
 
 # Especifica la ruta del Instant Client ANTES de cualquier conexión
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\kiwin\Downloads\instantclient_23_8")

class BiblioUNIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BiblioUNI - Gestión de Biblioteca")
        self.root.geometry("1200x700")
        
        # Configuración de la base de datos
        self.connection = None
        self.connect_to_db()
        
        # Crear interfaz
        self.create_widgets()
        self.load_books()
    

    def connect_to_db(self):
        """Establece conexión con Oracle"""
       
        try:
            self.connection = cx_Oracle.connect(
                user='System',
                password='keviN1523',
                dsn='localhost:1521/XEPDB1'
            )
        except cx_Oracle.DatabaseError as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{str(e)}")
            self.root.destroy()
    
    def execute_query(self, query, params=None, fetch=False):
        """Ejecuta consultas SQL"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or {})
            
            if fetch:
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                self.connection.commit()
                
            return True
        except cx_Oracle.DatabaseError as e:
            print(f"Error en consulta: {e}")
            self.connection.rollback()
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()

    def create_widgets(self):
        """Crea la interfaz gráfica"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de Libros
        libros_frame = ttk.Frame(self.notebook)
        self.notebook.add(libros_frame, text="Libros")
        self.create_libros_tab(libros_frame)
        
        # Pestaña de Autores
        autores_frame = ttk.Frame(self.notebook)
        self.notebook.add(autores_frame, text="Autores")
        self.create_autores_tab(autores_frame)
        
        # Pestaña de Editoriales
        editoriales_frame = ttk.Frame(self.notebook)
        self.notebook.add(editoriales_frame, text="Editoriales")
        self.create_editoriales_tab(editoriales_frame)
        
        # Pestaña de Usuarios
        usuarios_frame = ttk.Frame(self.notebook)
        self.notebook.add(usuarios_frame, text="Usuarios")
        self.create_usuarios_tab(usuarios_frame)
            
    def agregar_libro(self):
        """Abre diálogo para agregar nuevo libro"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Nuevo Libro")
    
        # Campos del formulario
        ttk.Label(dialog, text="Título:").grid(row=0, column=0, padx=5, pady=5)
        titulo_entry = ttk.Entry(dialog)
        titulo_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="ID Autor:").grid(row=1, column=0, padx=5, pady=5)
        id_autor_entry = ttk.Entry(dialog)
        id_autor_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="ID Editorial:").grid(row=2, column=0, padx=5, pady=5)
        id_editorial_entry = ttk.Entry(dialog)
        id_editorial_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="ISBN:").grid(row=3, column=0, padx=5, pady=5)
        isbn_entry = ttk.Entry(dialog)
        isbn_entry.grid(row=3, column=1, padx=5, pady=5)
    
        def guardar():
            try:
                success = self.execute_query(
                    """
                    INSERT INTO libros (id_libro, titulo, id_autor, id_editorial, isbn, disponible)
                    VALUES (libros_seq.NEXTVAL, :titulo, :id_autor, :id_editorial, :isbn, 1)
                    """,
                    {
                        'titulo': titulo_entry.get(),
                        'id_autor': int(id_autor_entry.get()),
                        'id_editorial': int(id_editorial_entry.get()),
                        'isbn': isbn_entry.get()
                    }
                )
                if success:
                    messagebox.showinfo("Éxito", "Libro agregado correctamente")
                    dialog.destroy()
                    self.load_books()
            except ValueError:
                messagebox.showerror("Error", "IDs deben ser números enteros")
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                messagebox.showerror("Error", f"Error de base de datos: {error.message}")
        
        ttk.Button(dialog, text="Guardar", command=guardar).grid(row=4, column=1, pady=10)

    def editar_libro(self):
        """Abre diálogo para editar libro existente"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un libro primero")
            return
        
        libro_data = self.tree.item(selected)['values']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Libro")
        
        # Campos del formulario
        ttk.Label(dialog, text="Título:").grid(row=0, column=0, padx=5, pady=5)
        titulo_entry = ttk.Entry(dialog)
        titulo_entry.insert(0, libro_data[1])
        titulo_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Obtener datos completos del libro
        libro_completo = self.execute_query(
            "SELECT id_autor, id_editorial, isbn FROM libros WHERE id_libro = :id",
            {'id': libro_data[0]},
            fetch=True
        )[0]
        
        ttk.Label(dialog, text="ID Autor:").grid(row=1, column=0, padx=5, pady=5)
        id_autor_entry = ttk.Entry(dialog)
        id_autor_entry.insert(0, str(libro_completo['ID_AUTOR']))
        id_autor_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="ID Editorial:").grid(row=2, column=0, padx=5, pady=5)
        id_editorial_entry = ttk.Entry(dialog)
        id_editorial_entry.insert(0, str(libro_completo['ID_EDITORIAL']))
        id_editorial_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="ISBN:").grid(row=3, column=0, padx=5, pady=5)
        isbn_entry = ttk.Entry(dialog)
        isbn_entry.insert(0, libro_completo['ISBN'])
        isbn_entry.grid(row=3, column=1, padx=5, pady=5)
        
        def actualizar():
            try:
                success = self.execute_query(
                    """
                    UPDATE libros SET
                        titulo = :titulo,
                        id_autor = :id_autor,
                        id_editorial = :id_editorial,
                        isbn = :isbn
                    WHERE id_libro = :id_libro
                    """,
                    {
                        'titulo': titulo_entry.get(),
                        'id_autor': int(id_autor_entry.get()),
                        'id_editorial': int(id_editorial_entry.get()),
                        'isbn': isbn_entry.get(),
                        'id_libro': libro_data[0]
                    }
                )
                if success:
                    messagebox.showinfo("Éxito", "Libro actualizado correctamente")
                    dialog.destroy()
                    self.load_books()
            except ValueError:
                messagebox.showerror("Error", "IDs deben ser números enteros")
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                messagebox.showerror("Error", f"Error de base de datos: {error.message}")
        
        ttk.Button(dialog, text="Actualizar", command=actualizar).grid(row=4, column=1, pady=10)

    def eliminar_libro(self):
        """Elimina el libro seleccionado"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un libro primero")
            return
        
        libro_data = self.tree.item(selected)['values']
        
        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el libro '{libro_data[1]}'?\nEsta acción no se puede deshacer."
        ):
            try:
                # Verificar si el libro tiene préstamos asociados (activos o históricos)
                prestamos = self.execute_query(
                    "SELECT COUNT(*) as total FROM prestamos WHERE id_libro = :id",
                    {'id': libro_data[0]},
                    fetch=True
                )
                
                if prestamos and prestamos[0]['TOTAL'] > 0:
                    # Preguntar si desea eliminar también los préstamos históricos
                    if messagebox.askyesno(
                        "Préstamos encontrados",
                        f"Este libro tiene {prestamos[0]['TOTAL']} préstamos registrados.\n"
                        "¿Desea eliminar todos los préstamos asociados y el libro?"
                    ):
                        # Eliminar primero los préstamos asociados
                        self.execute_query(
                            "DELETE FROM prestamos WHERE id_libro = :id",
                            {'id': libro_data[0]}
                        )
                    else:
                        messagebox.showinfo("Información", "Eliminación cancelada")
                        return
                
                # Verificar si el libro está actualmente prestado
                prestado = self.execute_query(
                    "SELECT 1 FROM prestamos WHERE id_libro = :id AND fecha_devolucion IS NULL",
                    {'id': libro_data[0]},
                    fetch=True
                )
                
                if prestado:
                    messagebox.showerror("Error", "No se puede eliminar un libro prestado")
                    return
                    
                # Ahora eliminar el libro
                success = self.execute_query(
                    "DELETE FROM libros WHERE id_libro = :id",
                    {'id': libro_data[0]}
                )
                
                if success:
                    messagebox.showinfo("Éxito", "Libro eliminado correctamente")
                    self.load_books()
                    
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                if error.code == 2292:  # ORA-02292: integrity constraint violated
                    messagebox.showerror(
                        "Error", 
                        "No se puede eliminar el libro porque tiene préstamos registrados.\n"
                        "Elimine primero los préstamos asociados."
                    )
                else:
                    messagebox.showerror("Error", f"Error de base de datos: {error.message}")    

    def create_usuarios_tab(self, parent_frame):
        """Crea la interfaz para la pestaña de usuarios"""
        # Treeview para usuarios
        self.tree_usuarios = ttk.Treeview(
            parent_frame,
            columns=("id", "nombre", "fecha_registro", "correo", "tipo_usuario"),
            show="headings"
        )
        
        self.tree_usuarios.heading("id", text="ID")
        self.tree_usuarios.heading("nombre", text="Nombre")
        self.tree_usuarios.heading("fecha_registro", text="Fecha Registro")
        self.tree_usuarios.heading("correo", text="Correo")
        self.tree_usuarios.heading("tipo_usuario", text="Tipo Usuario")
        
        # Ajustar columnas
        self.tree_usuarios.column("id", width=50)
        self.tree_usuarios.column("nombre", width=150)
        self.tree_usuarios.column("fecha_registro", width=120)
        self.tree_usuarios.column("correo", width=150)
        self.tree_usuarios.column("tipo_usuario", width=100)
        
        self.tree_usuarios.pack(fill=tk.BOTH, expand=True)
        
        # Botones de acción
        btn_frame = ttk.Frame(parent_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            btn_frame,
            text="Agregar Usuario",
            command=self.agregar_usuario
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Editar Usuario",
            command=self.editar_usuario
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Eliminar Usuario",
            command=self.eliminar_usuario
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Actualizar Lista",
            command=self.load_usuarios
        ).pack(side=tk.LEFT)
        
        # Cargar datos iniciales
        self.load_usuarios()

    def load_usuarios(self):
        """Carga los usuarios desde la base de datos"""
        usuarios = self.execute_query(
            "SELECT id_usuario, nombre, TO_CHAR(fecha_registro, 'DD/MM/YYYY') as fecha_registro, correo, tipo_usuario FROM usuarios ORDER BY nombre",
            fetch=True
        )
        
        self.tree_usuarios.delete(*self.tree_usuarios.get_children())
        
        if usuarios:
            for usuario in usuarios:
                self.tree_usuarios.insert("", tk.END, values=(
                    usuario['ID_USUARIO'],
                    usuario['NOMBRE'],
                    usuario['FECHA_REGISTRO'],
                    usuario['CORREO'] or "",
                    usuario['TIPO_USUARIO'].capitalize()
                ))
    
    def agregar_usuario(self):
        """Abre diálogo para agregar nuevo usuario"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Nuevo Usuario")
        dialog.resizable(False, False)
        
        # Campos del formulario
        ttk.Label(dialog, text="Nombre completo:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        nombre_entry = ttk.Entry(dialog, width=30)
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Correo electrónico:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        correo_entry = ttk.Entry(dialog, width=30)
        correo_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Tipo de usuario:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        tipo_entry = ttk.Combobox(dialog, 
                                values=["estudiante", "profesor", "administrador"],
                                state="readonly",
                                width=27)
        tipo_entry.grid(row=2, column=1, padx=5, pady=5)
        tipo_entry.current(0)
        
        def guardar():
            nombre = nombre_entry.get().strip()
            correo = correo_entry.get().strip()
            tipo = tipo_entry.get().strip()
            
            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
            if not tipo:
                messagebox.showerror("Error", "El tipo de usuario es obligatorio")
                return
                
            try:
                success = self.execute_query(
                    """
                    INSERT INTO usuarios (id_usuario, nombre, correo, tipo_usuario)
                    VALUES (usuarios_seq.NEXTVAL, :nombre, :correo, :tipo)
                    """,
                    {
                        'nombre': nombre,
                        'correo': correo if correo else None,
                        'tipo': tipo
                    }
                )
                
                if success:
                    messagebox.showinfo("Éxito", "Usuario agregado correctamente")
                    dialog.destroy()
                    self.load_usuarios()
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                if error.code == 1:  # Violación de constraint UNIQUE
                    messagebox.showerror("Error", "El correo electrónico ya está registrado")
                else:
                    messagebox.showerror("Error", f"Error de base de datos: {error.message}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Guardar", command=guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def editar_usuario(self):
        """Abre diálogo para editar usuario existente"""
        selected = self.tree_usuarios.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un usuario primero")
            return
        
        usuario_data = self.tree_usuarios.item(selected)['values']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Usuario")
        dialog.resizable(False, False)
        
        # Obtener datos completos del usuario
        usuario_completo = self.execute_query(
            "SELECT nombre, correo, tipo_usuario FROM usuarios WHERE id_usuario = :id",
            {'id': usuario_data[0]},
            fetch=True
        )[0]
        
        # Campos del formulario
        ttk.Label(dialog, text="Nombre completo:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        nombre_entry = ttk.Entry(dialog, width=30)
        nombre_entry.insert(0, usuario_completo['NOMBRE'])
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Correo electrónico:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        correo_entry = ttk.Entry(dialog, width=30)
        correo_entry.insert(0, usuario_completo['CORREO'] or "")
        correo_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Tipo de usuario:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        tipo_entry = ttk.Combobox(dialog, 
                                values=["estudiante", "profesor", "administrador"],
                                state="readonly",
                                width=27)
        tipo_entry.set(usuario_completo['TIPO_USUARIO'])
        tipo_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def actualizar():
            nombre = nombre_entry.get().strip()
            correo = correo_entry.get().strip()
            tipo = tipo_entry.get().strip()
            
            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
            if not tipo:
                messagebox.showerror("Error", "El tipo de usuario es obligatorio")
                return
                
            try:
                success = self.execute_query(
                    """
                    UPDATE usuarios SET
                        nombre = :nombre,
                        correo = :correo,
                        tipo_usuario = :tipo
                    WHERE id_usuario = :id
                    """,
                    {
                        'nombre': nombre,
                        'correo': correo if correo else None,
                        'tipo': tipo,
                        'id': usuario_data[0]
                    }
                )
                
                if success:
                    messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
                    dialog.destroy()
                    self.load_usuarios()
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                if error.code == 1:  # Violación de constraint UNIQUE
                    messagebox.showerror("Error", "El correo electrónico ya está registrado")
                else:
                    messagebox.showerror("Error", f"Error de base de datos: {error.message}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Actualizar", command=actualizar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def eliminar_usuario(self):
        """Elimina el usuario seleccionado"""
        selected = self.tree_usuarios.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un usuario primero")
            return
        
        usuario_data = self.tree_usuarios.item(selected)['values']
        
        # Verificar si el usuario tiene préstamos
        prestamos = self.execute_query(
            "SELECT 1 FROM prestamos WHERE id_usuario = :id",
            {'id': usuario_data[0]},
            fetch=True
        )
        
        if prestamos:
            messagebox.showerror(
                "Error", 
                "No se puede eliminar el usuario porque tiene préstamos registrados.\n"
                "Elimine primero los préstamos asociados."
            )
            return
        
        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar al usuario '{usuario_data[1]}'?\nEsta acción no se puede deshacer."
        ):
            success = self.execute_query(
                "DELETE FROM usuarios WHERE id_usuario = :id",
                {'id': usuario_data[0]}
            )
            
            if success:
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
                self.load_usuarios()

    def create_libros_tab(self, parent_frame):
        """Crea la interfaz para la pestaña de libros"""
        # Barra de búsqueda
        search_frame = ttk.Frame(parent_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            search_frame, 
            text="Buscar", 
            command=self.search_books
        ).pack(side=tk.LEFT, padx=5)
        
        # Treeview para libros
        self.tree = ttk.Treeview(
            parent_frame,
            columns=("id", "titulo", "autor", "editorial", "disponible"),
            show="headings"
        )
        
        self.tree.heading("id", text="ID")
        self.tree.heading("titulo", text="Título")
        self.tree.heading("autor", text="Autor")
        self.tree.heading("editorial", text="Editorial")
        self.tree.heading("disponible", text="Disponible")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Botones de acción
        btn_frame = ttk.Frame(parent_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            btn_frame,
            text="Agregar Libro",
            command=self.agregar_libro
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Editar Libro",
            command=self.editar_libro
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Eliminar Libro",
            command=self.eliminar_libro
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(btn_frame, orient='vertical').pack(side=tk.LEFT, padx=10, fill='y')
        
        ttk.Button(
            btn_frame, 
            text="Nuevo Préstamo",
            command=self.nuevo_prestamo
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Registrar Devolución",
            command=self.registrar_devolucion
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Actualizar Lista",
            command=self.load_books
        ).pack(side=tk.LEFT)
    
    def create_autores_tab(self, parent_frame):
        """Crea la interfaz para la pestaña de autores"""
        # Treeview para autores
        self.tree_autores = ttk.Treeview(
            parent_frame,
            columns=("id", "nombre"),
            show="headings"
        )
        
        self.tree_autores.heading("id", text="ID")
        self.tree_autores.heading("nombre", text="Nombre")
        
        self.tree_autores.pack(fill=tk.BOTH, expand=True)
        
        # Botones de acción
        btn_frame = ttk.Frame(parent_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            btn_frame,
            text="Agregar Autor",
            command=self.agregar_autor
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Editar Autor",
            command=self.editar_autor
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Eliminar Autor",
            command=self.eliminar_autor
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Actualizar Lista",
            command=self.load_autores
        ).pack(side=tk.LEFT)
        
        # Cargar datos iniciales
        self.load_autores()
    
    def create_editoriales_tab(self, parent_frame):
        """Crea la interfaz para la pestaña de editoriales"""
        # Treeview para editoriales
        self.tree_editoriales = ttk.Treeview(
            parent_frame,
            columns=("id", "nombre"),
            show="headings"
        )
        
        self.tree_editoriales.heading("id", text="ID")
        self.tree_editoriales.heading("nombre", text="Nombre")
        
        self.tree_editoriales.pack(fill=tk.BOTH, expand=True)
        
        # Botones de acción
        btn_frame = ttk.Frame(parent_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            btn_frame,
            text="Agregar Editorial",
            command=self.agregar_editorial
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Editar Editorial",
            command=self.editar_editorial
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Eliminar Editorial",
            command=self.eliminar_editorial
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Actualizar Lista",
            command=self.load_editoriales
        ).pack(side=tk.LEFT)
        
        # Cargar datos iniciales
        self.load_editoriales()

    def cargar_autores(self):
        """Carga lista de autores para combobox"""
        return self.execute_query("SELECT id_autor, nombre FROM autores ORDER BY nombre", fetch=True)

    def cargar_editoriales(self):
        """Carga lista de editoriales para combobox"""
        return self.execute_query("SELECT id_editorial, nombre FROM editoriales ORDER BY nombre", fetch=True)
    
    def load_books(self):
        """Carga los libros desde la base de datos"""
        query = """
        SELECT l.id_libro, l.titulo, l.disponible, 
               a.nombre as autor, e.nombre as editorial
        FROM libros l
        JOIN autores a ON l.id_autor = a.id_autor
        JOIN editoriales e ON l.id_editorial = e.id_editorial
        """
        
        libros = self.execute_query(query, fetch=True)
        self.tree.delete(*self.tree.get_children())
        
        if libros:
            for libro in libros:
                self.tree.insert("", tk.END, values=(
                    libro['ID_LIBRO'],
                    libro['TITULO'],
                    libro['AUTOR'],
                    libro['EDITORIAL'],
                    "Sí" if libro['DISPONIBLE'] else "No"
                ))
    
    def search_books(self):
        """Busca libros por título o autor"""
        term = self.search_entry.get().strip()
        if not term:
            self.load_books()
            return
        
        query = """
        SELECT l.id_libro, l.titulo, l.disponible, 
               a.nombre as autor, e.nombre as editorial
        FROM libros l
        JOIN autores a ON l.id_autor = a.id_autor
        JOIN editoriales e ON l.id_editorial = e.id_editorial
        WHERE UPPER(l.titulo) LIKE UPPER(:term) OR UPPER(a.nombre) LIKE UPPER(:term)
        """
        
        libros = self.execute_query(query, {'term': f'%{term}%'}, fetch=True)
        self.tree.delete(*self.tree.get_children())
        
        if libros:
            for libro in libros:
                self.tree.insert("", tk.END, values=(
                    libro['ID_LIBRO'],
                    libro['TITULO'],
                    libro['AUTOR'],
                    libro['EDITORIAL'],
                    "Sí" if libro['DISPONIBLE'] else "No"
                ))
        else:
            messagebox.showinfo("Búsqueda", "No se encontraron libros con ese criterio")
    
    def nuevo_prestamo(self):
        """Registra un nuevo préstamo"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un libro primero")
            return
        
        libro_data = self.tree.item(selected)['values']
        if libro_data[4] == "No":
            messagebox.showwarning("Advertencia", "El libro no está disponible")
            return
        
        # Pedir ID de usuario
        id_usuario = simpledialog.askinteger(
            "Nuevo Préstamo", 
            "Ingrese el ID del usuario:",
            parent=self.root
        )
        
        if not id_usuario:
            return
        
        # Verificar si el usuario existe
        usuario = self.execute_query(
            "SELECT 1 FROM usuarios WHERE id_usuario = :id",
            {'id': id_usuario},
            fetch=True
        )
        
        if not usuario:
            messagebox.showerror("Error", "Usuario no encontrado")
            return
        
        # Registrar préstamo
        prestamo_ok = self.execute_query(
            """
            INSERT INTO prestamos (id_prestamo, id_usuario, id_libro, fecha_prestamo)
            VALUES (prestamos_seq.NEXTVAL, :id_usuario, :id_libro, :fecha)
            """,
            {
                'id_usuario': id_usuario,
                'id_libro': libro_data[0],
                'fecha': datetime.now()
            }
        )
        
        if prestamo_ok:
            # Actualizar disponibilidad
            self.execute_query(
                "UPDATE libros SET disponible = 0 WHERE id_libro = :id",
                {'id': libro_data[0]}
            )
            messagebox.showinfo("Éxito", "Préstamo registrado correctamente")
            self.load_books()
        else:
            messagebox.showerror("Error", "No se pudo registrar el préstamo")
    
    def registrar_devolucion(self):
        """Registra la devolución de un libro"""
        # Obtener préstamos activos
        prestamos = self.execute_query(
            """
            SELECT p.id_prestamo, l.titulo, u.nombre as usuario
            FROM prestamos p
            JOIN libros l ON p.id_libro = l.id_libro
            JOIN usuarios u ON p.id_usuario = u.id_usuario
            WHERE p.fecha_devolucion IS NULL
            """,
            fetch=True
        )
        
        if not prestamos:
            messagebox.showinfo("Devoluciones", "No hay préstamos activos")
            return
        
        # Diálogo para seleccionar préstamo
        dialog = tk.Toplevel(self.root)
        dialog.title("Seleccionar Préstamo")
        
        tree = ttk.Treeview(dialog, columns=("id", "libro", "usuario"), show="headings")
        tree.heading("id", text="ID Préstamo")
        tree.heading("libro", text="Libro")
        tree.heading("usuario", text="Usuario")
        tree.pack(fill=tk.BOTH, expand=True)
        
        for p in prestamos:
            tree.insert("", tk.END, values=(p['ID_PRESTAMO'], p['TITULO'], p['USUARIO']))
        
        def confirmar_devolucion():
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("Advertencia", "Seleccione un préstamo")
                return
            
            prestamo_data = tree.item(selected)['values']
            
            # Actualizar préstamo
            update_ok = self.execute_query(
                """
                UPDATE prestamos 
                SET fecha_devolucion = :fecha, estado = 'COMPLETADO'
                WHERE id_prestamo = :id
                """,
                {
                    'fecha': datetime.now(),
                    'id': prestamo_data[0]
                }
            )
            
            if update_ok:
                # Obtener ID del libro para actualizar disponibilidad
                libro = self.execute_query(
                    "SELECT id_libro FROM prestamos WHERE id_prestamo = :id",
                    {'id': prestamo_data[0]},
                    fetch=True
                )
                
                if libro:
                    self.execute_query(
                        "UPDATE libros SET disponible = 1 WHERE id_libro = :id",
                        {'id': libro[0]['ID_LIBRO']}
                    )
                
                messagebox.showinfo("Éxito", "Devolución registrada correctamente")
                dialog.destroy()
                self.load_books()
            else:
                messagebox.showerror("Error", "No se pudo registrar la devolución")
        
        ttk.Button(
            dialog,
            text="Confirmar Devolución",
            command=confirmar_devolucion
        ).pack(pady=10)
    
    def __del__(self):
        """Cierra la conexión a la base de datos al salir"""
        if self.connection:
            self.connection.close()
    def load_autores(self):
        """Carga los autores desde la base de datos"""
        autores = self.execute_query(
            "SELECT id_autor, nombre FROM autores ORDER BY nombre",
            fetch=True
        )
        
        self.tree_autores.delete(*self.tree_autores.get_children())
        
        if autores:
            for autor in autores:
                self.tree_autores.insert("", tk.END, values=(
                    autor['ID_AUTOR'],
                    autor['NOMBRE'] or ""
                ))
    
    def load_editoriales(self):
        """Carga las editoriales desde la base de datos"""
        editoriales = self.execute_query(
            "SELECT id_editorial, nombre FROM editoriales ORDER BY nombre",
            fetch=True
        )
        
        self.tree_editoriales.delete(*self.tree_editoriales.get_children())
        
        if editoriales:
            for editorial in editoriales:
                self.tree_editoriales.insert("", tk.END, values=(
                    editorial['ID_EDITORIAL'],
                    editorial['NOMBRE']
                ))
    
    def agregar_autor(self):
        """Abre diálogo para agregar nuevo autor"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Nuevo Autor")
        
        # Campos del formulario
        ttk.Label(dialog, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        nombre_entry = ttk.Entry(dialog)
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        def guardar():
            nombre = nombre_entry.get().strip()
            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
                
            success = self.execute_query(
                """
                INSERT INTO autores (id_autor, nombre)
                VALUES (autores_seq.NEXTVAL, :nombre)
                """,
                {
                    'nombre': nombre
                }
            )
            
            if success:
                messagebox.showinfo("Éxito", "Autor agregado correctamente")
                dialog.destroy()
                self.load_autores()
        
        ttk.Button(dialog, text="Guardar", command=guardar).grid(row=2, column=1, pady=10)
    
    def editar_autor(self):
        """Abre diálogo para editar autor existente"""
        selected = self.tree_autores.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un autor primero")
            return
        
        autor_data = self.tree_autores.item(selected)['values']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Autor")
        
        # Campos del formulario
        ttk.Label(dialog, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        nombre_entry = ttk.Entry(dialog)
        nombre_entry.insert(0, autor_data[1])
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        def actualizar():
            nombre = nombre_entry.get().strip()
            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
                
            success = self.execute_query(
                """
                UPDATE autores SET
                    nombre = :nombre
                WHERE id_autor = :id
                """,
                {
                    'nombre': nombre or None,
                    'id': autor_data[0]
                }
            )
            
            if success:
                messagebox.showinfo("Éxito", "Autor actualizado correctamente")
                dialog.destroy()
                self.load_autores()
        
        ttk.Button(dialog, text="Actualizar", command=actualizar).grid(row=2, column=1, pady=10)
    
    def eliminar_autor(self):
        """Elimina el autor seleccionado"""
        selected = self.tree_autores.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un autor primero")
            return
        
        autor_data = self.tree_autores.item(selected)['values']
        
        # Verificar si el autor tiene libros asociados
        libros = self.execute_query(
            "SELECT 1 FROM libros WHERE id_autor = :id",
            {'id': autor_data[0]},
            fetch=True
        )
        
        if libros:
            messagebox.showerror(
                "Error", 
                "No se puede eliminar el autor porque tiene libros asociados.\n"
                "Elimine o reasigne los libros primero."
            )
            return
        
        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar al autor '{autor_data[1]}'?\nEsta acción no se puede deshacer."
        ):
            success = self.execute_query(
                "DELETE FROM autores WHERE id_autor = :id",
                {'id': autor_data[0]}
            )
            
            if success:
                messagebox.showinfo("Éxito", "Autor eliminado correctamente")
                self.load_autores()
    
    def agregar_editorial(self):
        """Abre diálogo para agregar nueva editorial"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Nueva Editorial")
        
        # Campos del formulario
        ttk.Label(dialog, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        nombre_entry = ttk.Entry(dialog)
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        def guardar():
            nombre = nombre_entry.get().strip()
            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
                
            success = self.execute_query(
                """
                INSERT INTO editoriales (id_editorial, nombre)
                VALUES (editoriales_seq.NEXTVAL, :nombre)
                """,
                {
                    'nombre': nombre
                }
            )
            
            if success:
                messagebox.showinfo("Éxito", "Editorial agregada correctamente")
                dialog.destroy()
                self.load_editoriales()
        
        ttk.Button(dialog, text="Guardar", command=guardar).grid(row=3, column=1, pady=10)
    
    def editar_editorial(self):
        """Abre diálogo para editar editorial existente"""
        selected = self.tree_editoriales.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una editorial primero")
            return
        
        editorial_data = self.tree_editoriales.item(selected)['values']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Editorial")
        
        # Campos del formulario
        ttk.Label(dialog, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        nombre_entry = ttk.Entry(dialog)
        nombre_entry.insert(0, editorial_data[1])
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        def actualizar():
            nombre = nombre_entry.get().strip()
            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
                
            success = self.execute_query(
                """
                UPDATE editoriales SET
                    nombre = :nombre
                WHERE id_editorial = :id
                """,
                {
                    'nombre': nombre,
                    'id': editorial_data[0]
                }
            )
            
            if success:
                messagebox.showinfo("Éxito", "Editorial actualizada correctamente")
                dialog.destroy()
                self.load_editoriales()
        
        ttk.Button(dialog, text="Actualizar", command=actualizar).grid(row=3, column=1, pady=10)
    
    def eliminar_editorial(self):
        """Elimina la editorial seleccionada"""
        selected = self.tree_editoriales.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una editorial primero")
            return
        
        editorial_data = self.tree_editoriales.item(selected)['values']
        
        # Verificar si la editorial tiene libros asociados
        libros = self.execute_query(
            "SELECT 1 FROM libros WHERE id_editorial = :id",
            {'id': editorial_data[0]},
            fetch=True
        )
        
        if libros:
            messagebox.showerror(
                "Error", 
                "No se puede eliminar la editorial porque tiene libros asociados.\n"
                "Elimine o reasigne los libros primero."
            )
            return
        
        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar la editorial '{editorial_data[1]}'?\nEsta acción no se puede deshacer."
        ):
            success = self.execute_query(
                "DELETE FROM editoriales WHERE id_editorial = :id",
                {'id': editorial_data[0]}
            )
            
            if success:
                messagebox.showinfo("Éxito", "Editorial eliminada correctamente")
                self.load_editoriales()

if __name__ == "__main__":
    root = tk.Tk()
    app = BiblioUNIApp(root)
    root.mainloop()