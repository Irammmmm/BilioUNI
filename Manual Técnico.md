
1. Descripción General
BiblioUNI es un sistema de gestión de biblioteca desarrollado en Python con interfaz gráfica (Tkinter) que se conecta a una base de datos Oracle. Permite gestionar libros, autores, editoriales y usuarios, así como registrar préstamos y devoluciones.

2. Requisitos del Sistema
Python 3.8+
Oracle Instant Client
Base de datos Oracle (XEPDB1)
Bibliotecas: cx_Oracle, tkinter

3. Configuraci´0n de la Base de Datos
cx_Oracle.init_oracle_client(lib_dir=r"C:\ruta\instantclient")
connection = cx_Oracle.connect(
    user='System',
    password='keviN1523',
    dsn='localhost:1521/XEPDB1'
)

4. Diagrama de Clases
BiblioUNIApp: Clase principal que gestiona la interfaz y conexión a BD
Métodos principales:
execute_query(): Ejecuta consultas SQL
create_widgets(): Construye la interfaz
CRUD para cada entidad (libros, usuarios, etc.)
