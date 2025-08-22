import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import re

class JavaPrintlnAdder:
    def __init__(self, root):
        self.root = root
        self.root.title("Java System.out.println Adder")
        self.root.geometry("800x600")
        
        # Variables
        self.project_path = tk.StringVar()
        
        # UI Components
        self.create_widgets()
    
    def create_widgets(self):
        # Frame for project selection
        frame = tk.Frame(self.root)
        frame.pack(pady=10, padx=10, fill="x")
        
        tk.Label(frame, text="Proyecto Java:").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.project_path, width=50).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="Seleccionar", command=self.select_project).grid(row=0, column=2)
        
        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Agregar System.out.println", command=self.add_println, 
                 bg="green", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Salir", command=self.root.quit,
                 bg="red", fg="white").pack(side="left", padx=5)
        
        # Log area
        tk.Label(self.root, text="Log de Procesamiento:").pack(anchor="w", padx=10)
        self.log_area = scrolledtext.ScrolledText(self.root, width=90, height=25)
        self.log_area.pack(pady=10, padx=10, fill="both", expand=True)
        
    def select_project(self):
        folder = filedialog.askdirectory(title="Seleccione la carpeta del proyecto Java")
        if folder:
            self.project_path.set(folder)
            self.log("Carpeta seleccionada: " + folder)
    
    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.root.update_idletasks()
    
    def add_println(self):
        project_path = self.project_path.get()
        if not project_path:
            messagebox.showerror("Error", "Por favor seleccione una carpeta de proyecto")
            return
        
        try:
            java_files = self.find_java_files(project_path)
            self.log(f"Encontrados {len(java_files)} archivos Java")
            
            processed_count = 0
            for java_file in java_files:
                if self.process_java_file(java_file):
                    processed_count += 1
                
            messagebox.showinfo("Éxito", f"System.out.println agregados a {processed_count} archivos Java")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
    
    def find_java_files(self, folder):
        java_files = []
        for root, dirs, files in os.walk(folder):
            # Skip hidden directories (like .git)
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.java'):
                    java_files.append(os.path.join(root, file))
        return java_files
    
    def process_java_file(self, file_path):
        self.log(f"Procesando: {os.path.basename(file_path)}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
        
        # Extract class name
        class_name = self.extract_class_name(content)
        if not class_name:
            self.log(f"  No se pudo encontrar el nombre de la clase, omitiendo")
            return False
        
        # Process methods
        new_content = self.add_println_to_methods(content, class_name)
        
        # Only write if changes were made
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            self.log(f"  System.out.println agregados a métodos en {class_name}")
            return True
        else:
            self.log(f"  No se encontraron métodos para modificar en {class_name}")
            return False
    
    def extract_class_name(self, content):
        # Look for class declaration (skip inner classes and interfaces)
        class_pattern = r'^[^{}]*?\b(class|interface|enum|record)\s+(\w+)'
        matches = re.finditer(class_pattern, content, re.MULTILINE)
        
        for match in matches:
            # Skip interfaces, enums and records if we want only classes
            if match.group(1) == 'class':
                return match.group(2)
        
        # If no class found, return the first match regardless of type
        first_match = re.search(r'^(?:public|private|protected|abstract|final|static)?\s*(?:class|interface|enum|record)\s+(\w+)', content, re.MULTILINE)
        return first_match.group(1) if first_match else None
    
    def add_println_to_methods(self, content, class_name):
        # Pattern to match method declarations (excluding constructors)
        method_pattern = r'(\n\s*(?:public|protected|private|static|final|synchronized|abstract|native|\s)+[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)\s*(?:throws\s+[\w\s,]+)?\s*\{)'
        
        methods = list(re.finditer(method_pattern, content))
        methods.reverse()  # Process from end to beginning to avoid offset issues
        
        for match in methods:
            method_name = match.group(2)
            
            # Skip constructors (methods with same name as class)
            if method_name == class_name:
                continue
            
            # Skip main method
            if method_name == 'main' and 'static' in match.group(1) and 'void' in match.group(1):
                continue
            
            # Find the opening brace of the method (it's in our match)
            method_start = match.end()
            
            # Add entry log at the beginning of the method
            entry_log = f'\n        System.out.println("ENTRADA: {class_name}.{method_name}");\n'
            content = content[:method_start] + entry_log + content[method_start:]
            
            # Add exit logs before return statements
            content = self.add_exit_println(content, class_name, method_name)
        
        return content
    
    def add_exit_println(self, content, class_name, method_name):
        # Find all return statements in the method
        return_pattern = r'return[^;]*;'
        returns = list(re.finditer(return_pattern, content))
        returns.reverse()  # Process from end to beginning
        
        for return_match in returns:
            exit_log = f'        System.out.println("SALIDA: {class_name}.{method_name}");\n'
            content = content[:return_match.start()] + exit_log + content[return_match.start():]
        
        return content

if __name__ == "__main__":
    root = tk.Tk()
    app = JavaPrintlnAdder(root)
    root.mainloop()
