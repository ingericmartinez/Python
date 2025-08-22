import os
import shutil
import tkinter as tk
from tkinter import filedialog, ttk

# --- Lógica principal del script ---

def populate_tree(tree, node, parent=""):
    """
    Función recursiva para llenar el Treeview con la estructura de directorios y archivos.
    """
    if os.path.isdir(node):
        # Es un directorio, lo insertamos en el árbol
        # El 'iid' es un identificador único, usamos la ruta completa
        item_id = tree.insert(parent, 'end', text=os.path.basename(node), values=[node], open=True)
        # Recorremos su contenido para agregarlo al árbol
        for item in os.listdir(node):
            populate_tree(tree, os.path.join(node, item), parent=item_id)
    else:
        # Es un archivo, lo insertamos
        tree.insert(parent, 'end', text=os.path.basename(node), values=[node])

def get_all_children(tree, item=""):
    """
    Obtiene todos los descendientes de un elemento en el Treeview.
    """
    children = tree.get_children(item)
    for child in children:
        children.extend(get_all_children(tree, child))
    return children

def toggle_check(event):
    """
    Maneja el evento de hacer clic en una casilla para seleccionar/deseleccionar
    los elementos hijos también.
    """
    row_id = tree.identify_row(event.y)
    if not row_id:
        return

    # Cambiamos el estado de la casilla (marcado/desmarcado)
    tags = tree.item(row_id, 'tags')
    if 'checked' in tags:
        tree.item(row_id, tags=('unchecked',))
    else:
        tree.item(row_id, tags=('checked',))

    # Propagamos el cambio a todos los hijos
    for child_id in get_all_children(tree, row_id):
        tree.item(child_id, tags=tree.item(row_id, 'tags'))


def clone_structure():
    """
    Función principal que realiza la clonación de los elementos seleccionados.
    """
    # Obtenemos la ruta de destino
    dest_dir = dest_dir_var.get()
    if not dest_dir:
        print("Error: Por favor, selecciona un directorio de destino.")
        return

    # Obtenemos todos los elementos marcados
    checked_items = tree.tag_has('checked')

    if not checked_items:
        print("Advertencia: No se ha seleccionado ningún elemento para clonar.")
        return

    # Creamos un conjunto para evitar procesar rutas duplicadas (padres e hijos)
    paths_to_copy = set()
    source_dir = source_dir_var.get()

    for item_id in checked_items:
        # Obtenemos la ruta completa del elemento
        path = tree.item(item_id, 'values')[0]
        paths_to_copy.add(path)

    print("Iniciando la clonación...")

    for path in sorted(list(paths_to_copy)): # Ordenamos para asegurar que los directorios padres se creen primero
        # Calculamos la ruta relativa al origen para construir el destino correctamente
        relative_path = os.path.relpath(path, source_dir)
        destination_path = os.path.join(dest_dir, relative_path)

        # Si es un directorio, creamos el directorio de destino
        if os.path.isdir(path):
            os.makedirs(destination_path, exist_ok=True)
            print(f"Directorio creado: {destination_path}")
        # Si es un archivo, lo copiamos
        elif os.path.isfile(path):
            # Nos aseguramos de que el directorio del archivo exista en el destino
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            shutil.copy2(path, destination_path)
            print(f"Archivo copiado: {destination_path}")

    print("¡Clonación completada con éxito!")


def select_source_directory():
    """
    Abre un diálogo para que el usuario seleccione el directorio de origen.
    """
    directory = filedialog.askdirectory()
    if directory:
        source_dir_var.set(directory)
        # Limpiamos el árbol anterior
        for i in tree.get_children():
            tree.delete(i)
        # Llenamos el árbol con la nueva estructura
        populate_tree(tree, directory)

def select_dest_directory():
    """
    Abre un diálogo para que el usuario seleccione el directorio de destino.
    """
    directory = filedialog.askdirectory()
    if directory:
        dest_dir_var.set(directory)


# --- Creación de la Interfaz Gráfica (GUI) ---

# Ventana principal
root = tk.Tk()
root.title("Asistente para Clonar Directorios")
root.geometry("600x700")

# Frame principal
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

# --- Sección de Selección de Directorios ---

dir_frame = ttk.LabelFrame(main_frame, text="1. Selección de Directorios", padding="10")
dir_frame.pack(fill=tk.X, expand=True)

# Variables para guardar las rutas
source_dir_var = tk.StringVar()
dest_dir_var = tk.StringVar()

# Origen
ttk.Button(dir_frame, text="Seleccionar Origen", command=select_source_directory).pack(side=tk.LEFT, padx=5)
ttk.Entry(dir_frame, textvariable=source_dir_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)

# Destino
ttk.Button(dir_frame, text="Seleccionar Destino", command=select_dest_directory).pack(side=tk.LEFT, padx=(15, 5))
ttk.Entry(dir_frame, textvariable=dest_dir_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)

# --- Sección de Estructura de Directorio ---

tree_frame = ttk.LabelFrame(main_frame, text="2. Estructura del Directorio (marca lo que quieres clonar)", padding="10")
tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

# Creación del Treeview para mostrar la estructura
tree = ttk.Treeview(tree_frame, columns=("fullpath",), displaycolumns=())
tree.pack(fill=tk.BOTH, expand=True)

# Configuración de los 'tags' para las casillas de verificación
# Usamos imágenes simples para simular las casillas
# Tkinter no tiene checkboxes nativos en el Treeview
im_checked = tk.PhotoImage(data=b'R0lGODlhEAAQAMQAAORHHOVSKudfLulrSOp3WOyGaO2Ja+2Vb+2XcO6dffGoivGsk/Owo/SzqfTDrPTDr/bGs/bGs/fJt/fJt/fLuPfLuPjNv/jNwPnNwPnRxPrVxfnWxfvbyPzdygAAAP///yH5BAEKAA8ALAAAAAAQABAAAAVQ4CeOZGme52rTcrgWEiJAgBYEBAgQ4gBSYIg+D4QB8KgIgoExDICCF6GhmBgiwQHyAwGPB4LhEPrgJwgMGocv1sPpsiA/OhdPS172eBUECBAA7')
im_unchecked = tk.PhotoImage(data=b'R0lGODlhEAAQAMQAAORHHOVSKudfLulrSOp3WOyGaO2Ja+2Vb+2XcO6dffGoivGsk/Owo/SzqfTDrPTDr/bGs/bGs/fJt/fJt/fLuPfLuPjNv/jNwPnNwPnRxPrVxfnWxfvbyPzdygAAAP///yH5BAEKAA8ALAAAAAAQABAAAAU54CeOZGme52rTcrgWEiJAgBYEBAgQ4gBSYIg+D4QB8KgIgoExDICCF6GhmBgiwQHyAwGPB4LhEPrgJwgMGocv1sPpsiA/OhdPS172eBUECBAA7')

tree.tag_configure('checked', image=im_checked)
tree.tag_configure('unchecked', image=im_unchecked)

# Asociar el evento de clic a nuestra función de marcado/desmarcado
tree.bind('<Button-1>', toggle_check)

# --- Sección de Acción ---

action_frame = ttk.Frame(main_frame, padding="10")
action_frame.pack(fill=tk.X, expand=True)

ttk.Button(action_frame, text="¡Clonar Estructura Seleccionada!", command=clone_structure).pack(expand=True)

# Iniciar el bucle principal de la aplicación
root.mainloop()
