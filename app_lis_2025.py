import tkinter as tk
from tkinter import ttk
import sqlite3

# Ruta absoluta a la base de datos
DB_PATH = 'app_lis_2025/mi_base_de_datos.db'

# Conexión a la base de datos
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear las tablas si no existen
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS REGISTROS (
        id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_registro TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DETALLES_REGISTROS (
        id_detalle_registro INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_detalle TEXT NOT NULL,
        articulo TEXT NOT NULL,
        precio REAL,
        cantidad REAL,
        total REAL,
        id_registro INTEGER,
        FOREIGN KEY (id_registro) REFERENCES REGISTROS(id_registro)
    )''')

    conn.commit()
except sqlite3.Error as e:
    print("Error al conectar a la base de datos:", e)

# Función para agregar datos
def agregar_datos():
    """
    Agrega un nuevo registro a la base de datos.
    """
    id_registro = id_registro_combobox.get()
    fecha_registro = fecha_registro_entry.get()
    fecha_detalle = fecha_detalle_entry.get()
    articulo = articulo_entry.get()
    precio = float(precio_entry.get())
    cantidad = float(cantidad_entry.get())
    total = precio * cantidad

    # Si no hay un id_registro seleccionado, crear un nuevo registro en la tabla REGISTROS
    if not id_registro:
        cursor.execute("INSERT INTO REGISTROS (fecha_registro) VALUES (?)", (fecha_registro,))
        id_registro = cursor.lastrowid
        llenar_combobox()  # Actualizar el combobox después de agregar un nuevo registro
    else:
        id_registro = int(id_registro)

    # Insertar en la tabla DETALLES_REGISTROS
    cursor.execute("INSERT INTO DETALLES_REGISTROS (fecha_detalle, articulo, precio, cantidad, total, id_registro) VALUES (?, ?, ?, ?, ?, ?)",
                   (fecha_detalle, articulo, precio, cantidad, total, id_registro))
    conn.commit()
    actualizar_treeview()
    actualizar_treeview_detalles()
    limpiar_campos()

# Función para actualizar el Treeview principal
def actualizar_treeview():
    """
    Actualiza el Treeview principal con todos los registros de la base de datos.
    """
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute('''
    SELECT d.id_detalle_registro, r.id_registro, r.fecha_registro, d.fecha_detalle, d.articulo, d.precio, d.cantidad, d.total
    FROM DETALLES_REGISTROS d
    JOIN REGISTROS r ON d.id_registro = r.id_registro
    ''')
    rows = cursor.fetchall()
    for row in rows:
        tree.insert('', tk.END, values=row)

# Función para actualizar el Treeview de detalles
def actualizar_treeview_detalles():
    """
    Actualiza el Treeview de detalles con los registros correspondientes al id_registro seleccionado.
    """
    for row in tree_detalles.get_children():
        tree_detalles.delete(row)
    id_registro = id_registro_combobox.get()
    if id_registro:
        cursor.execute('''
        SELECT id_detalle_registro, fecha_detalle, articulo, precio, cantidad, total
        FROM DETALLES_REGISTROS
        WHERE id_registro = ?
        ''', (id_registro,))
        rows = cursor.fetchall()
        for row in rows:
            tree_detalles.insert('', tk.END, values=row)

# Función para autocompletar los campos al seleccionar una fila
def seleccionar_fila(event):
    """
    Autocompleta los campos del formulario al seleccionar una fila en el Treeview principal.
    """
    item = tree.selection()[0]
    valores = tree.item(item, 'values')
    id_registro_combobox.set(valores[1])
    fecha_registro_entry.delete(0, tk.END)
    fecha_registro_entry.insert(0, valores[2])
    fecha_detalle_entry.delete(0, tk.END)
    fecha_detalle_entry.insert(0, valores[3])
    articulo_entry.delete(0, tk.END)
    articulo_entry.insert(0, valores[4])
    precio_entry.delete(0, tk.END)
    precio_entry.insert(0, valores[5])
    cantidad_entry.delete(0, tk.END)
    cantidad_entry.insert(0, valores[6])
    actualizar_treeview_detalles()

# Función para limpiar los campos del formulario
def limpiar_campos():
    """
    Limpia todos los campos del formulario.
    """
    fecha_registro_entry.delete(0, tk.END)
    id_registro_combobox.set('')
    fecha_detalle_entry.delete(0, tk.END)
    articulo_entry.delete(0, tk.END)
    precio_entry.delete(0, tk.END)
    cantidad_entry.delete(0, tk.END)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Formulario de Artículos")

# Frame para REGISTROS
frame_registro = tk.Frame(root, padx=10, pady=10)
frame_registro.pack(fill="x")

# Función para ir al registro anterior
def registro_anterior():
    """
    Carga el registro anterior al actualmente seleccionado.
    """
    current_id = id_registro_combobox.get()
    if current_id:
        cursor.execute("SELECT MAX(id_registro) FROM REGISTROS WHERE id_registro < ?", (current_id,))
        prev_id = cursor.fetchone()[0]
        if prev_id:
            id_registro_combobox.set(prev_id)
            cargar_registro(prev_id)

# Función para ir al registro siguiente
def registro_siguiente():
    """
    Carga el registro siguiente al actualmente seleccionado.
    """
    current_id = id_registro_combobox.get()
    if current_id:
        cursor.execute("SELECT MIN(id_registro) FROM REGISTROS WHERE id_registro > ?", (current_id,))
        next_id = cursor.fetchone()[0]
        if next_id:
            id_registro_combobox.set(next_id)
            cargar_registro(next_id)

# Función para cargar los datos de un registro
def cargar_registro(id_registro):
    """
    Carga los datos de un registro específico en el formulario.
    """
    cursor.execute("SELECT fecha_registro FROM REGISTROS WHERE id_registro = ?", (id_registro,))
    fecha_registro = cursor.fetchone()[0]
    fecha_registro_entry.delete(0, tk.END)
    fecha_registro_entry.insert(0, fecha_registro)
    actualizar_treeview_detalles()

# Función para ir al primer registro
def primer_registro():
    """
    Carga el primer registro de la tabla REGISTROS.
    """
    cursor.execute("SELECT MIN(id_registro) FROM REGISTROS")
    primer_id = cursor.fetchone()[0]
    if primer_id:
        id_registro_combobox.set(primer_id)
        cargar_registro(primer_id)

# Función para ir al último registro
def ultimo_registro():
    """
    Carga el último registro de la tabla REGISTROS.
    """
    cursor.execute("SELECT MAX(id_registro) FROM REGISTROS")
    ultimo_id = cursor.fetchone()[0]
    if ultimo_id:
        id_registro_combobox.set(ultimo_id)
        cargar_registro(ultimo_id)

# Función para crear un nuevo registro
def nuevo_registro():
    """
    Crea un nuevo registro en la tabla REGISTROS y lo carga en el formulario.
    """
    cursor.execute("INSERT INTO REGISTROS (fecha_registro) VALUES (?)", (fecha_registro_entry.get(),))
    conn.commit()
    nuevo_id = cursor.lastrowid
    id_registro_combobox.set(nuevo_id)
    llenar_combobox()
    limpiar_campos()
    fecha_registro_entry.insert(0, fecha_registro_entry.get())  # Mantener la fecha del registro
    actualizar_treeview_detalles()

# Botones de navegación
btn_primer = tk.Button(frame_registro, text="<<", command=primer_registro)
btn_primer.grid(row=0, column=0, padx=5, pady=5)

btn_anterior = tk.Button(frame_registro, text="<", command=registro_anterior)
btn_anterior.grid(row=0, column=1, padx=5, pady=5)

btn_siguiente = tk.Button(frame_registro, text=">", command=registro_siguiente)
btn_siguiente.grid(row=0, column=2, padx=5, pady=5)

btn_ultimo = tk.Button(frame_registro, text=">>", command=ultimo_registro)
btn_ultimo.grid(row=0, column=3, padx=5, pady=5)

btn_nuevo = tk.Button(frame_registro, text="+", command=nuevo_registro)
btn_nuevo.grid(row=0, column=4, padx=5, pady=5)

tk.Label(frame_registro, text="ID Registro").grid(row=0, column=5, padx=5, pady=5)
id_registro_combobox = ttk.Combobox(frame_registro)
id_registro_combobox.grid(row=0, column=6, padx=5, pady=5)

# Función para llenar el combobox con los ID de registros existentes
def llenar_combobox():
    """
    Llena el combobox con los ID de registros existentes en la tabla REGISTROS.
    """
    cursor.execute("SELECT id_registro FROM REGISTROS")
    registros = cursor.fetchall()
    id_registro_combobox['values'] = [registro[0] for registro in registros]

llenar_combobox()

# Función para actualizar el Treeview de detalles cuando cambia el combobox
def on_combobox_select(event):
    """
    Actualiza el Treeview de detalles cuando se selecciona un nuevo registro en el combobox.
    """
    id_registro = id_registro_combobox.get()
    if id_registro:
        cargar_registro(id_registro)

id_registro_combobox.bind("<<ComboboxSelected>>", on_combobox_select)

tk.Label(frame_registro, text="Fecha Registro").grid(row=0, column=7, padx=5, pady=5)
fecha_registro_entry = tk.Entry(frame_registro)
fecha_registro_entry.grid(row=0, column=8, padx=5, pady=5)

# Frame para DETALLES_REGISTROS
frame_detalle = tk.Frame(root, padx=10, pady=10)
frame_detalle.pack(fill="x")

tk.Label(frame_detalle, text="Fecha Detalle").grid(row=0, column=0, padx=5, pady=5)
fecha_detalle_entry = tk.Entry(frame_detalle)
fecha_detalle_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_detalle, text="Artículo").grid(row=0, column=2, padx=5, pady=5)
articulo_entry = tk.Entry(frame_detalle)
articulo_entry.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_detalle, text="Precio").grid(row=0, column=4, padx=5, pady=5)
precio_entry = tk.Entry(frame_detalle)
precio_entry.grid(row=0, column=5, padx=5, pady=5)

tk.Label(frame_detalle, text="Cantidad").grid(row=0, column=6, padx=5, pady=5)
cantidad_entry = tk.Entry(frame_detalle)
cantidad_entry.grid(row=0, column=7, padx=5, pady=5)

# Botón para agregar datos
agregar_btn = tk.Button(root, text="Agregar", command=agregar_datos)
agregar_btn.pack(pady=10)

# Crear y configurar el Treeview para DETALLES_REGISTROS
detalles_frame = tk.Frame(root)
detalles_frame.pack(fill="both", expand=True, padx=10, pady=10)

columns_detalles = ('id_detalle_registro', 'fecha_detalle', 'articulo', 'precio', 'cantidad', 'total')
tree_detalles = ttk.Treeview(detalles_frame, columns=columns_detalles, show='headings')

for col in columns_detalles:
    tree_detalles.heading(col, text=col.replace('_', ' ').title())
    tree_detalles.column(col, width=100)

vsb_detalles = ttk.Scrollbar(detalles_frame, orient="vertical", command=tree_detalles.yview)
vsb_detalles.pack(side='right', fill='y')

hsb_detalles = ttk.Scrollbar(detalles_frame, orient="horizontal", command=tree_detalles.xview)
hsb_detalles.pack(side='bottom', fill='x')

tree_detalles.configure(yscrollcommand=vsb_detalles.set, xscrollcommand=hsb_detalles.set)
tree_detalles.pack(side="left", fill="both", expand=True)

# Crear y configurar el Treeview principal
tree_frame = tk.Frame(root)
tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

columns = ('id_detalle_registro', 'id_registro', 'fecha_registro', 'fecha_detalle', 'articulo', 'precio', 'cantidad', 'total')
tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

for col in columns:
    tree.heading(col, text=col.replace('_', ' ').title())
    tree.column(col, width=100)

vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
vsb.pack(side='right', fill='y')

hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
hsb.pack(side='bottom', fill='x')

tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
tree.pack(side="left", fill="both", expand=True)

tree.bind('<ButtonRelease-1>', seleccionar_fila)



# Inicializar los Treeviews con datos
actualizar_treeview()
actualizar_treeview_detalles()

# Ejecutar la aplicación
root.mainloop()