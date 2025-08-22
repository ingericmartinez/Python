import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import re
from pathlib import Path

class JavaProjectAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Proyectos Java")
        self.root.geometry("1000x700")
        
        # Variables
        self.project_path = None
        self.classes = []
        self.methods = {}
        self.current_class = None
        
        # UI Components
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Project selection
        ttk.Label(main_frame, text="Directorio del proyecto:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.project_path_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.project_path_var, width=60).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Seleccionar", command=self.select_project).grid(row=0, column=2, padx=5)
        
        # Classes frame
        classes_frame = ttk.LabelFrame(main_frame, text="Clases (no Test)", padding="5")
        classes_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        classes_frame.columnconfigure(0, weight=1)
        classes_frame.rowconfigure(0, weight=1)
        
        self.classes_listbox = tk.Listbox(classes_frame, height=10, selectmode=tk.SINGLE)
        self.classes_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.classes_listbox.bind('<<ListboxSelect>>', self.on_class_select)
        
        # Add scrollbar to classes listbox
        classes_scrollbar = ttk.Scrollbar(classes_frame, orient=tk.VERTICAL, command=self.classes_listbox.yview)
        classes_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.classes_listbox.configure(yscrollcommand=classes_scrollbar.set)
        
        # Methods frame
        methods_frame = ttk.LabelFrame(main_frame, text="Métodos", padding="5")
        methods_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        methods_frame.columnconfigure(0, weight=1)
        methods_frame.rowconfigure(0, weight=1)
        
        self.methods_listbox = tk.Listbox(methods_frame, height=8, selectmode=tk.SINGLE)
        self.methods_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.methods_listbox.bind('<<ListboxSelect>>', self.on_method_select)
        
        # Add scrollbar to methods listbox
        methods_scrollbar = ttk.Scrollbar(methods_frame, orient=tk.VERTICAL, command=self.methods_listbox.yview)
        methods_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.methods_listbox.configure(yscrollcommand=methods_scrollbar.set)
        
        # Dependencies frame
        deps_frame = ttk.LabelFrame(main_frame, text="Clases involucradas en el método", padding="5")
        deps_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        deps_frame.columnconfigure(0, weight=1)
        deps_frame.rowconfigure(0, weight=1)
        
        self.deps_tree = ttk.Treeview(deps_frame, columns=('type',), show='tree headings', height=10)
        self.deps_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.deps_tree.heading('#0', text='Clase')
        self.deps_tree.heading('type', text='Tipo')
        self.deps_tree.column('#0', width=300)
        self.deps_tree.column('type', width=100)
        
        # Add scrollbar to dependencies tree
        deps_scrollbar = ttk.Scrollbar(deps_frame, orient=tk.VERTICAL, command=self.deps_tree.yview)
        deps_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.deps_tree.configure(yscrollcommand=deps_scrollbar.set)
        
        # Back button
        ttk.Button(main_frame, text="Volver a lista de clases", command=self.back_to_classes).grid(row=4, column=0, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Seleccione un directorio de proyecto Java")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).grid(
            row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
    
    def select_project(self):
        folder = filedialog.askdirectory(title="Seleccione la carpeta del proyecto Java")
        if folder:
            self.project_path = folder
            self.project_path_var.set(folder)
            self.analyze_project()
    
    def analyze_project(self):
        if not self.project_path:
            return
        
        self.status_var.set("Analizando proyecto...")
        self.root.update()
        
        # Clear previous data
        self.classes = []
        self.methods = {}
        self.classes_listbox.delete(0, tk.END)
        self.methods_listbox.delete(0, tk.END)
        self.deps_tree.delete(*self.deps_tree.get_children())
        
        # Find all Java files
        java_files = []
        for root, dirs, files in os.walk(self.project_path):
            # Skip test directories and hidden directories
            if any(x in root for x in ['/test', '/Test', '\\test', '\\Test']) or any(x.startswith('.') for x in root.split(os.sep)):
                continue
                
            for file in files:
                if file.endswith('.java') and not file.lower().endswith('test.java'):
                    java_files.append(os.path.join(root, file))
        
        # Extract class names and methods
        for java_file in java_files:
            try:
                with open(java_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                try:
                    with open(java_file, 'r', encoding='latin-1') as f:
                        content = f.read()
                except:
                    continue
            
            # Extract class name
            class_name = self.extract_class_name(content, java_file)
            if class_name and 'test' not in class_name.lower():
                self.classes.append(class_name)
                
                # Extract methods
                class_methods = self.extract_methods(content)
                self.methods[class_name] = class_methods
        
        # Sort and display classes
        self.classes.sort()
        for class_name in self.classes:
            self.classes_listbox.insert(tk.END, class_name)
        
        self.status_var.set(f"Proyecto analizado. Encontradas {len(self.classes)} clases.")
    
    def extract_class_name(self, content, file_path):
        # Try to find class declaration
        class_patterns = [
            r'class\s+(\w+)',
            r'interface\s+(\w+)',
            r'enum\s+(\w+)',
            r'record\s+(\w+)'
        ]
        
        for pattern in class_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        # If no match, use filename
        return os.path.basename(file_path).replace('.java', '')
    
    def extract_methods(self, content):
        methods = []
        # Pattern to match method declarations
        method_pattern = r'(public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])'
        
        matches = re.finditer(method_pattern, content)
        for match in matches:
            method_name = match.group(2)
            # Skip constructors
            if not any(cls in method_name for cls in self.classes):
                methods.append(method_name)
        
        return methods
    
    def on_class_select(self, event):
        if not self.classes_listbox.curselection():
            return
        
        selected_index = self.classes_listbox.curselection()[0]
        self.current_class = self.classes[selected_index]
        
        # Display methods for selected class
        self.methods_listbox.delete(0, tk.END)
        if self.current_class in self.methods:
            for method in self.methods[self.current_class]:
                self.methods_listbox.insert(tk.END, method)
        
        self.status_var.set(f"Clase seleccionada: {self.current_class}")
    
    def on_method_select(self, event):
        if not self.methods_listbox.curselection() or not self.current_class:
            return
        
        selected_index = self.methods_listbox.curselection()[0]
        method_name = self.methods[self.current_class][selected_index]
        
        # Find the Java file for the current class
        java_file = None
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.java') and self.current_class in file:
                    java_file = os.path.join(root, file)
                    break
            if java_file:
                break
        
        if not java_file:
            self.status_var.set("No se pudo encontrar el archivo de la clase")
            return
        
        # Read the file content
        try:
            with open(java_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            try:
                with open(java_file, 'r', encoding='latin-1') as f:
                    content = f.read()
            except:
                self.status_var.set("Error al leer el archivo de la clase")
                return
        
        # Find the method and extract involved classes
        involved_classes = self.find_involved_classes(content, method_name)
        
        # Display the involved classes
        self.deps_tree.delete(*self.deps_tree.get_children())
        for cls, dep_type in involved_classes:
            self.deps_tree.insert('', 'end', text=cls, values=(dep_type,))
        
        self.status_var.set(f"Método seleccionado: {self.current_class}.{method_name} - {len(involved_classes)} clases involucradas")
    
    def find_involved_classes(self, content, method_name):
        # Find the method in the content
        method_pattern = rf'[\w\<\>\[\]]+\s+{method_name}\s*\([^\)]*\)\s*\{'
        method_match = re.search(method_pattern, content)
        
        if not method_match:
            return []
        
        # Find the method body
        start_pos = method_match.end()
        brace_count = 1
        end_pos = start_pos
        
        while brace_count > 0 and end_pos < len(content):
            if content[end_pos] == '{':
                brace_count += 1
            elif content[end_pos] == '}':
                brace_count -= 1
            end_pos += 1
        
        method_body = content[start_pos:end_pos]
        
        # Find all class references in the method body
        involved_classes = set()
        
        # Look for object creation: new ClassName()
        new_pattern = r'new\s+([\w\.]+)\s*\('
        for match in re.finditer(new_pattern, method_body):
            cls_name = match.group(1).split('.')[-1]  # Get just the class name without package
            if cls_name in self.classes:
                involved_classes.add((cls_name, 'Instanciación'))
        
        # Look for method calls: object.method()
        method_call_pattern = r'(\w+)\.\w+\s*\('
        for match in re.finditer(method_call_pattern, method_body):
            var_name = match.group(1)
            
            # Try to find the variable declaration to get its type
            var_pattern = rf'([\w\.<>\[\]]+)\s+{var_name}\s*='
            var_match = re.search(var_pattern, method_body)
            if var_match:
                cls_name = var_match.group(1).split('.')[-1].replace('[]', '')
                if cls_name in self.classes:
                    involved_classes.add((cls_name, 'Uso'))
        
        # Look for class references in parameters and return types
        param_pattern = r'\(([^)]*)\)'
        method_def_match = re.search(method_pattern[:-1] + param_pattern, content)
        if method_def_match:
            params = method_def_match.group(1).split(',')
            for param in params:
                param = param.strip()
                if param:
                    cls_name = param.split()[-1].replace('[]', '')
                    if cls_name in self.classes:
                        involved_classes.add((cls_name, 'Parámetro'))
        
        return list(involved_classes)
    
    def back_to_classes(self):
        self.methods_listbox.delete(0, tk.END)
        self.deps_tree.delete(*self.deps_tree.get_children())
        self.current_class = None
        self.status_var.set("Seleccione una clase de la lista")

if __name__ == "__main__":
    root = tk.Tk()
    app = JavaProjectAnalyzer(root)
    root.mainloop()
