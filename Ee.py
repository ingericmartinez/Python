import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import shutil

class JavaClassExporter:
    def __init__(self, root):
        self.root = root
        self.root.title("Java Class Exporter")
        self.root.geometry("900x650")
        
        # Variables
        self.project_path = tk.StringVar()
        self.java_files = []  # Almacenará tuplas (path, name, type, package)
        self.all_java_files_cache = {}  # Cache para búsqueda rápida de archivos por nombre
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Project selection frame
        frame_top = ttk.Frame(self.root, padding="10")
        frame_top.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(frame_top, text="Project Directory:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(frame_top, textvariable=self.project_path, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(frame_top, text="Browse", command=self.browse_directory).grid(row=0, column=2)
        ttk.Button(frame_top, text="Scan", command=self.scan_java_files).grid(row=0, column=3, padx=5)
        
        # Table frame
        frame_middle = ttk.Frame(self.root, padding="10")
        frame_middle.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        columns = ("select", "name", "type", "package", "path")
        self.tree = ttk.Treeview(frame_middle, columns=columns, show="headings", selectmode="extended")
        
        # Define headings
        self.tree.heading("select", text="Select")
        self.tree.heading("name", text="Class/Interface Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("package", text="Package")
        self.tree.heading("path", text="Path")
        
        # Define columns
        self.tree.column("select", width=60, anchor="center")
        self.tree.column("name", width=150)
        self.tree.column("type", width=80)
        self.tree.column("package", width=200)
        self.tree.column("path", width=350)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame_middle, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind click on checkbox column
        self.tree.bind('<Button-1>', self.on_tree_click)
        
        # Button frame
        frame_bottom = ttk.Frame(self.root, padding="10")
        frame_bottom.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(frame_bottom, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_bottom, text="Deselect All", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_bottom, text="Export Selected", command=self.export_selected).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        frame_middle.columnconfigure(0, weight=1)
        frame_middle.rowconfigure(0, weight=1)
        
    def on_tree_click(self, event):
        """Handle click on checkbox column"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1":  # Checkbox column
                item = self.tree.identify_row(event.y)
                current_value = self.tree.set(item, "select")
                new_value = "☑" if current_value == "◻" else "◻"
                self.tree.set(item, "select", new_value)
    
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.project_path.set(directory)
            
    def scan_java_files(self):
        project_dir = self.project_path.get()
        if not project_dir:
            messagebox.showwarning("Warning", "Please select a project directory first.")
            return
            
        self.java_files = []
        self.all_java_files_cache = {}
        self.tree.delete(*self.tree.get_children())
        
        try:
            for root_dir, _, files in os.walk(project_dir):
                for file in files:
                    if file.endswith('.java'):
                        full_path = os.path.join(root_dir, file)
                        
                        # Read file to determine type, name and package
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # Extract package
                        package_match = re.search(r'^package\s+([^;]+);', content, re.MULTILINE)
                        package_name = package_match.group(1) if package_match else "default"
                        
                        # Check if it's a class or interface
                        is_interface = 'interface ' in content.split('{')[0]
                        class_match = re.search(r'(class|interface|enum)\s+(\w+)', content)
                        if class_match:
                            name = class_match.group(2)
                            file_type = "Interface" if is_interface else "Class"
                            
                            # Store file info with package
                            self.java_files.append((full_path, name, file_type, package_name))
                            self.all_java_files_cache[name] = (full_path, package_name)
            
            # ORDENAR LAS CLASES ALFABÉTICAMENTE por nombre
            self.java_files.sort(key=lambda x: x[1].lower())
            
            # Insert into treeview ordenado
            for full_path, name, file_type, package_name in self.java_files:
                self.tree.insert("", "end", values=("◻", name, file_type, package_name, full_path))
            
            self.status_var.set(f"Found {len(self.java_files)} Java files")
            messagebox.showinfo("Info", f"Found {len(self.java_files)} Java files.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error scanning directory: {str(e)}")
            
    def select_all(self):
        for item in self.tree.get_children():
            self.tree.set(item, "select", "☑")
            
    def deselect_all(self):
        for item in self.tree.get_children():
            self.tree.set(item, "select", "◻")
            
    def export_selected(self):
        selected_items = []
        for item in self.tree.get_children():
            if self.tree.set(item, "select") == "☑":
                selected_items.append(item)
                
        if not selected_items:
            messagebox.showwarning("Warning", "Please select at least one class/interface to export.")
            return
            
        # Ask for output directory
        output_dir = filedialog.askdirectory()
        if not output_dir:
            return
            
        exported_files = set()
        try:
            # Primero recolectar todos los archivos seleccionados
            files_to_export = []
            for item in selected_items:
                values = self.tree.item(item)['values']
                file_path = values[4]  # Full path is in column 5
                files_to_export.append(file_path)
            
            # Exportar archivos manteniendo estructura de paquetes
            for file_path in files_to_export:
                self.export_java_file_with_package(file_path, output_dir, exported_files)
                
            messagebox.showinfo("Success", f"Exported {len(exported_files)} files to {output_dir}")
            self.status_var.set(f"Exported {len(exported_files)} files")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during export: {str(e)}")
        
    def export_java_file_with_package(self, file_path, output_dir, exported_files, depth=0):
        """Export Java file maintaining its original package structure"""
        if depth > 10:  # Prevent infinite recursion
            return
            
        try:
            filename = os.path.basename(file_path)
            if filename in exported_files:
                return  # Already exported
                
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Extraer el package del archivo
            package_match = re.search(r'^package\s+([^;]+);', content, re.MULTILINE)
            if package_match:
                package_name = package_match.group(1)
                # Crear estructura de directorios según el package
                package_path = package_name.replace('.', os.sep)
                full_output_dir = os.path.join(output_dir, package_path)
                os.makedirs(full_output_dir, exist_ok=True)
                
                # Escribir el archivo con el contenido original (sin modificar el package)
                output_path = os.path.join(full_output_dir, filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                # Si no tiene package, exportar en el directorio raíz
                output_path = os.path.join(output_dir, filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
            exported_files.add(filename)
            
            # Encontrar clases importadas para exportar también
            import_pattern = r'^import\s+([^;]+);'
            imports = re.findall(import_pattern, content, re.MULTILINE)
            
            for import_stmt in imports:
                if import_stmt.endswith('.*'):
                    continue  # Skip wildcard imports
                    
                import_parts = import_stmt.split('.')
                class_name = import_parts[-1]
                
                # Buscar la clase importada en nuestro cache
                if class_name in self.all_java_files_cache:
                    imported_file_path, _ = self.all_java_files_cache[class_name]
                    self.export_java_file_with_package(imported_file_path, output_dir, exported_files, depth + 1)
                        
        except Exception as e:
            raise Exception(f"Error processing file {file_path}: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = JavaClassExporter(root)
    root.mainloop()
