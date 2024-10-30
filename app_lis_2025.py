import tkinter as tk
from tkinter import ttk
import sqlite3

# Ruta absoluta a la base de datos
DB_PATH = 'app_lis_2025/mi_base_de_datos.db'

# ... resto de tu código

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    conn.commit()
except sqlite3.Error as e:
    print("Error al conectar a la base de datos:", e)
finally:
    if conn:
        conn.close()


# Conexión a la base de datos
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

# Función para agregar datos
def agregar_datos():
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
    limpiar_campos()

# Función para actualizar el Treeview
def actualizar_treeview():
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

# Función para autocompletar los campos al seleccionar una fila
def seleccionar_fila(event):
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

# Función para limpiar los campos del formulario
def limpiar_campos():
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

tk.Label(frame_registro, text="ID Registro").grid(row=0, column=0, padx=5, pady=5)
id_registro_combobox = ttk.Combobox(frame_registro)
id_registro_combobox.grid(row=0, column=1, padx=5, pady=5)

# Función para llenar el combobox con los ID de registros existentes
def llenar_combobox():
    cursor.execute("SELECT id_registro FROM REGISTROS")
    registros = cursor.fetchall()
    id_registro_combobox['values'] = [registro[0] for registro in registros]

llenar_combobox()

tk.Label(frame_registro, text="Fecha Registro").grid(row=0, column=2, padx=5, pady=5)
fecha_registro_entry = tk.Entry(frame_registro)
fecha_registro_entry.grid(row=0, column=3, padx=5, pady=5)

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

# Crear y configurar el Treeview
columns = ('id_detalle_registro', 'id_registro', 'fecha_registro', 'fecha_detalle', 'articulo', 'precio', 'cantidad', 'total')
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.heading('id_detalle_registro', text='ID Detalle Registro')
tree.heading('id_registro', text='ID Registro')
tree.heading('fecha_registro', text='Fecha Registro')
tree.heading('fecha_detalle', text='Fecha Detalle')
tree.heading('articulo', text='Artículo')
tree.heading('precio', text='Precio')
tree.heading('cantidad', text='Cantidad')
tree.heading('total', text='Total')

# Ajustar el ancho de las columnas
for column in columns:
    tree.column(column, width=100)

tree.pack(fill="both", expand=True)
tree.bind('<ButtonRelease-1>', seleccionar_fila)

# Inicializar el Treeview con datos
actualizar_treeview()

# Ejecutar la aplicación
root.mainloop()
