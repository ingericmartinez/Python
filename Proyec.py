import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
from collections import deque

class CodeAnalyzer:
    def __init__(self):
        self.classes = {}
        self.current_file = ""
        
    def parse_project(self, file_content):
        """Analiza el contenido del proyecto y extrae todas las clases con sus métodos"""
        self.classes = {}
        lines = file_content.split('\n')
        current_class = None
        current_method = None
        class_content = []
        
        for line in lines:
            # Buscar declaración de clase
            class_match = re.match(r'^\s*class\s+(\w+)\s*[:{]\s*$', line)
            if class_match:
                if current_class:
                    self.classes[current_class] = {
                        'methods': self._extract_methods(class_content),
                        'content': class_content
                    }
                current_class = class_match.group(1)
                class_content = [line]
                continue
                
            if current_class:
                class_content.append(line)
                
        # Añadir la última clase
        if current_class:
            self.classes[current_class] = {
                'methods': self._extract_methods(class_content),
                'content': class_content
            }
            
        return self.classes
        
    def _extract_methods(self, class_content):
        """Extrae los métodos de una clase"""
        methods = {}
        method_name = None
        method_content = []
        in_method = False
        brace_count = 0
        
        for line in class_content:
            # Buscar declaración de método
            method_match = re.match(r'^\s*(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*(?::[^{]*)?\s*{', line)
            if method_match and not in_method:
                method_name = method_match.group(1)
                in_method = True
                brace_count = 1
                method_content = [line]
                continue
                
            if in_method:
                method_content.append(line)
                # Contar llaves para determinar el final del método
                brace_count += line.count('{')
                brace_count -= line.count('}')
                
                if brace_count <= 0:
                    methods[method_name] = method_content
                    in_method = False
                    method_name = None
                    
        return methods
        
    def find_method_calls(self, method_content):
        """Encuentra todas las llamadas a métodos en el contenido de un método"""
        calls = []
        for line in method_content:
            # Buscar patrones de llamadas a métodos
            matches = re.findall(r'(\w+)\.(\w+)\s*\(|(\w+)\s*\(', line)
            for match in matches:
                if match[0] and match[1]:  # patron objeto.metodo()
                    calls.append((match[0], match[1]))
                elif match[2]:  # patron metodo()
                    calls.append(('self', match[2]))
        return calls
        
    def trace_dependencies(self, start_class, start_method):
        """Rastrea todas las dependencias a partir de una clase y método inicial"""
        if start_class not in self.classes:
            return None
            
        if start_method not in self.classes[start_class]['methods']:
            return None
            
        # Usamos BFS para rastrear las dependencias
        visited = set()
        queue = deque([(start_class, start_method)])
        dependencies = []
        
        while queue:
            current_class, current_method = queue.popleft()
            if (current_class, current_method) in visited:
                continue
                
            visited.add((current_class, current_method))
            
            # Obtener el contenido del método actual
            method_content = self.classes[current_class]['methods'][current_method]
            calls = self.find_method_calls(method_content)
            
            for obj, method in calls:
                if obj == 'self':  # Llamada a método de la misma clase
                    if method in self.classes[current_class]['methods']:
                        dependencies.append((current_class, current_method, current_class, method))
                        if (current_class, method) not in visited:
                            queue.append((current_class, method))
                else:  # Llamada a método de otra clase
                    if obj in self.classes and method in self.classes[obj]['methods']:
                        dependencies.append((current_class, current_method, obj, method))
                        if (obj, method) not in visited:
                            queue.append((obj, method))
            
        return dependencies


class CodeAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Dependencias de Métodos")
        self.root.geometry("900x700")
        
        self.analyzer = CodeAnalyzer()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid para expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Analizador de Dependencias de Métodos", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Botón para cargar archivo
        ttk.Label(main_frame, text="Archivo del proyecto:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.file_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.file_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        ttk.Button(main_frame, text="Examinar", command=self.browse_file).grid(row=1, column=2, padx=(5, 0))
        
        # Entrada para clase inicial
        ttk.Label(main_frame, text="Clase inicial:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.start_class = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.start_class, width=30).grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        
        # Entrada para método inicial
        ttk.Label(main_frame, text="Método inicial:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.start_method = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.start_method, width=30).grid(row=3, column=1, sticky=tk.W, padx=(5, 0))
        
        # Botón para analizar
        ttk.Button(main_frame, text="Analizar Dependencias", command=self.analyze_dependencies).grid(row=4, column=0, columnspan=3, pady=10)
        
        # Treeview para mostrar resultados
        ttk.Label(main_frame, text="Dependencias encontradas:").grid(row=5, column=0, sticky=tk.W, pady=(10, 5))
        
        columns = ('clase_origen', 'metodo_origen', 'clase_destino', 'metodo_destino')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        self.tree.heading('clase_origen', text='Clase Origen')
        self.tree.heading('metodo_origen', text='Método Origen')
        self.tree.heading('clase_destino', text='Clase Destino')
        self.tree.heading('metodo_destino', text='Método Destino')
        
        self.tree.column('clase_origen', width=150)
        self.tree.column('metodo_origen', width=150)
        self.tree.column('clase_destino', width=150)
        self.tree.column('metodo_destino', width=150)
        
        self.tree.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Scrollbar para el treeview
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=6, column=3, sticky=(tk.N, tk.S))
        
        # Área de texto para mostrar detalles
        ttk.Label(main_frame, text="Detalles del método seleccionado:").grid(row=7, column=0, sticky=tk.W, pady=(10, 5))
        self.details_text = scrolledtext.ScrolledText(main_frame, width=80, height=10)
        self.details_text.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar expansión
        main_frame.rowconfigure(6, weight=1)
        main_frame.rowconfigure(8, weight=1)
        
        # Enlazar evento de selección en el treeview
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de proyecto",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.analyzer.parse_project(content)
                    messagebox.showinfo("Éxito", "Proyecto cargado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo: {str(e)}")
    
    def analyze_dependencies(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Por favor, seleccione un archivo de proyecto primero")
            return
            
        if not self.start_class.get() or not self.start_method.get():
            messagebox.showerror("Error", "Por favor, especifique la clase y método inicial")
            return
            
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Analizar dependencias
        try:
            dependencies = self.analyzer.trace_dependencies(
                self.start_class.get(), 
                self.start_method.get()
            )
            
            if not dependencies:
                messagebox.showinfo("Resultado", "No se encontraron dependencias")
                return
                
            # Llenar treeview con los resultados
            for dep in dependencies:
                self.tree.insert('', 'end', values=dep)
                
            messagebox.showinfo("Éxito", f"Se encontraron {len(dependencies)} dependencias")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al analizar dependencias: {str(e)}")
    
    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        item = self.tree.item(selected_item[0])
        clase_origen, metodo_origen, clase_destino, metodo_destino = item['values']
        
        # Mostrar detalles del método seleccionado
        try:
            if clase_destino in self.analyzer.classes and metodo_destino in self.analyzer.classes[clase_destino]['methods']:
                method_content = self.analyzer.classes[clase_destino]['methods'][metodo_destino]
                details = f"Método: {clase_destino}.{metodo_destino}()\n\n"
                details += "Contenido:\n" + "\n".join(method_content)
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(tk.END, details)
            else:
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(tk.END, "No se encontraron detalles para este método")
        except Exception as e:
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, f"Error al cargar detalles: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CodeAnalyzerApp(root)
    root.mainloop()
