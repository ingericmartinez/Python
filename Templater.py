import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import re

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Templates de Proyecto")
        self.root.geometry("800x600")

        # Variables
        self.source_dir = tk.StringVar()
        self.new_project_name = tk.StringVar()
        self.methods = {}

        # --- Interfaz Gráfica ---

        # Frame para la selección del proyecto
        project_frame = ttk.LabelFrame(root, text="Configuración del Proyecto")
        project_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(project_frame, text="Directorio del Proyecto Original:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(project_frame, textvariable=self.source_dir, width=60).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(project_frame, text="Explorar...", command=self.browse_source_dir).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(project_frame, text="Nuevo Nombre del Proyecto:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(project_frame, textvariable=self.new_project_name, width=60).grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(project_frame, text="Crear Template y Listar Métodos", command=self.create_template_and_list_methods).grid(row=2, column=0, columnspan=3, pady=10)

        # Frame para la lista de métodos
        methods_frame = ttk.LabelFrame(root, text="Métodos de la Aplicación")
        methods_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(methods_frame, columns=("Archivo", "Metodo"), show="headings")
        self.tree.heading("Archivo", text="Archivo")
        self.tree.heading("Metodo", text="Método")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(methods_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Frame para la generación final
        generate_frame = ttk.Frame(root)
        generate_frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Button(generate_frame, text="Generar Template (Eliminar Métodos Seleccionados)", command=self.generate_template).pack(pady=10)

    def browse_source_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.source_dir.set(directory)

    def create_template_and_list_methods(self):
        source = self.source_dir.get()
        new_name = self.new_project_name.get()

        if not source or not new_name:
            messagebox.showerror("Error", "Por favor, selecciona un directorio de origen y proporciona un nuevo nombre de proyecto.")
            return

        destination_parent = filedialog.askdirectory(title="Selecciona dónde guardar el nuevo proyecto")
        if not destination_parent:
            return
            
        self.destination_dir = os.path.join(destination_parent, new_name)

        try:
            # Copiar la estructura del proyecto
            shutil.copytree(source, self.destination_dir)
            
            # Limpiar la tabla anterior
            for i in self.tree.get_children():
                self.tree.delete(i)
            self.methods.clear()

            # Listar métodos de los archivos copiados
            self.list_methods_from_project(self.destination_dir)
            messagebox.showinfo("Éxito", f"La estructura del proyecto se ha copiado a:\n{self.destination_dir}\n\nAhora puedes seleccionar los métodos a eliminar.")
            
        except FileExistsError:
            messagebox.showerror("Error", f"El directorio '{self.destination_dir}' ya existe. Por favor, elige un nombre de proyecto diferente o una ubicación distinta.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al copiar el proyecto: {e}")

    def list_methods_from_project(self, directory):
        # Expresión regular para encontrar métodos de Java.
        # Puede necesitar ajustes para otros lenguajes o estilos de código.
        method_regex = re.compile(r'(public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+)\s*\([^)]*\)\s*(\{?|[^;])')

        for root_dir, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".java"): # Se puede extender a otros tipos de archivo, ej: .py, .kt
                    file_path = os.path.join(root_dir, file)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        found_methods = method_regex.finditer(content)
                        for match in found_methods:
                            method_name = match.group(2)
                            # Añadir a la tabla con una casilla de verificación
                            item_id = self.tree.insert("", "end", values=(os.path.relpath(file_path, directory), method_name))
                            self.methods[item_id] = {'file_path': file_path, 'method_name': method_name, 'checked': tk.BooleanVar(value=False)}
                            
                            # Simular una casilla de verificación (visual)
                            self.tree.item(item_id, tags=('unchecked',))
        
        self.tree.tag_configure('unchecked', image=self.get_checkbox_image(False))
        self.tree.tag_configure('checked', image=self.get_checkbox_image(True))
        self.tree.bind('<Button-1>', self.toggle_checkbox)

    def get_checkbox_image(self, checked):
        # Crea imágenes de checkbox sobre la marcha
        if checked:
            return tk.PhotoImage(data=b'R0lGODdhEAAQAIABAAAAAP//ACwAAAAAEAAQAAAIjAABCBxIsKDBgwgTDlzIsKFDgxceNnS4kGFDiA4hSpzIsGLFixgXMmzYkGHDjxw9fgQZUOFBkyhRlgwJgGZNmzZz6tzJk2dPn0CDCh1KtKjRo0iTKl3KtKnTp1CjSp1KtarVq1izat3KtavXr2DDih1LtqzZs2jTql3Ltq3bt3Djyp1Lt67du3jz6t3Lt6/fv4ADCx5MuLDhw4gTK17MuLHjx5AjS55MubLly5gza97MubPnz6BDix5NurTp06hTq17NurXr17Bjy55Nu7bt27hz697Nu7fv38CDCx9OvLjx48iTK1/OvLnz59CjS59Ovbr169iza9/Ovbv37+DDix9Pvrz58+jTq1/Pvr379/Djy59Pv779+/jz69/Pv7////8ABijggAQWaOCBCCao4IIMNujggxBGKOGEFFZo4YUYZqjhhhx26OGHIIYo4ogklmjiiSimqOKKLLbo4ouLFwA7')
        else:
            return tk.PhotoImage(data=b'R0lGODdhEAAQAIABAAAAAP//ACwAAAAAEAAQAAAIhAABCBxIsKDBgwgTDlzIsKFDgxceNnS4kGHDhA4hSpzIsGHDhxgrYsSIkWNHjx5BhhQ5kmRJkyhTplwZgGZNmzZz6tzJk2dPn0CDCh1KVOlQo0iTKl3KtKnTp1CjSp1KtarVq1izat3KtavXr2DDih1LtqzZs2jTql3Ltq3bt3Djyp1Lt67du3jz6t3Lt6/fv4ADCx5MOCCAAA7')

    def toggle_checkbox(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id and row_id in self.methods:
            current_tags = self.tree.item(row_id, "tags")
            if 'unchecked' in current_tags:
                self.tree.item(row_id, tags=('checked',))
                self.methods[row_id]['checked'].set(True)
            else:
                self.tree.item(row_id, tags=('unchecked',))
                self.methods[row_id]['checked'].set(False)

    def generate_template(self):
        methods_to_delete = []
        for item_id, data in self.methods.items():
            if data['checked'].get():
                methods_to_delete.append(data)

        if not methods_to_delete:
            messagebox.showinfo("Información", "No se ha seleccionado ningún método para eliminar.")
            return

        if not messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de que quieres eliminar {len(methods_to_delete)} métodos? Esta acción no se puede deshacer."):
            return

        for method_data in methods_to_delete:
            file_path = method_data['file_path']
            method_name = method_data['method_name']
            
            # Expresión regular para encontrar el método completo
            # ATENCIÓN: Esta es una simplificación y podría fallar con sobrecargas de métodos o código complejo.
            method_body_regex = re.compile(
                r'(public|protected|private|static|\s).*?\s+' + re.escape(method_name) + r'\s*\([^)]*\)\s*\{[^{}]*(((?<=\{)[^{}]*)|[^{}]*)*\}', 
                re.DOTALL
            )
            
            with open(file_path, 'r+', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                new_content = method_body_regex.sub('', content)
                f.seek(0)
                f.write(new_content)
                f.truncate()
        
        messagebox.showinfo("Éxito", f"Se han eliminado {len(methods_to_delete)} métodos del proyecto en:\n{self.destination_dir}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
