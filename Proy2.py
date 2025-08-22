import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import re
from pathlib import Path

class JavaProjectProcessor:
    def __init__(self):
        self.project_content = ""
        self.classes = {}
        self.selected_classes = []
        self.common_package = "package"
        
    def load_project(self, file_path):
        """Carga el contenido del proyecto desde un archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.project_content = file.read()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {str(e)}")
            return False
    
    def extract_classes(self):
        """Extrae todas las clases del proyecto"""
        self.classes = {}
        class_pattern = re.compile(r'^\s*package\s+([\w\.]+)\s*;.*?^.*?class\s+(\w+)\s*(?:extends|\{|\w|implements)*\s*\{', 
                                  re.MULTILINE | re.DOTALL)
        
        matches = class_pattern.findall(self.project_content)
        for package, class_name in matches:
            # Encontrar el contenido completo de la clase
            class_start = self.project_content.find(f"class {class_name}")
            if class_start == -1:
                continue
                
            # Buscar el inicio y fin de la clase
            brace_count = 0
            class_end = class_start
            for i in range(class_start, len(self.project_content)):
                if self.project_content[i] == '{':
                    brace_count += 1
                elif self.project_content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        class_end = i + 1
                        break
            
            class_content = self.project_content[class_start:class_end]
            self.classes[class_name] = {
                'package': package,
                'content': class_content,
                'full_content': f"package {package};\n\n{class_content}"
            }
        
        return list(self.classes.keys())
    
    def change_package(self, class_name, new_package):
        """Cambia el package de una clase"""
        if class_name not in self.classes:
            return None
            
        class_info = self.classes[class_name]
        old_package = class_info['package']
        
        # Reemplazar el package antiguo por el nuevo
        new_content = class_info['full_content'].replace(
            f"package {old_package};", 
            f"package {new_package};"
        )
        
        # También actualizar las referencias a otras clases del mismo package
        for other_class in self.classes:
            if other_class != class_name:
                pattern = r'\b' + re.escape(other_class) + r'\b'
                new_content = re.sub(pattern, f"{self.common_package}.{other_class}", new_content)
        
        return new_content
    
    def generate_modified_classes(self, output_dir):
        """Genera las clases modificadas en el directorio de salida"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        generated_files = []
        for class_name in self.selected_classes:
            modified_content = self.change_package(class_name, self.common_package)
            if modified_content:
                file_path = os.path.join(output_dir, f"{class_name}.java")
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(modified_content)
                generated_files.append(file_path)
        
        return generated_files
    
    def create_test_harness(self, output_dir, main_class, main_method):
        """Crea una clase de prueba para ejecutar el método principal"""
        test_class_content = f"""package {self.common_package};

public class TestHarness {{
    public static void main(String[] args) {{
        try {{
            System.out.println("Iniciando prueba del flujo de negocio...");
            
            // Crear instancia de la clase principal
            {main_class} instance = new {main_class}();
            
            // Ejecutar el método principal
            System.out.println("Resultado: " + instance.{main_method}());
            
            System.out.println("Prueba completada exitosamente!");
        }} catch (Exception e) {{
            System.err.println("Error durante la prueba: " + e.getMessage());
            e.printStackTrace();
        }}
    }}
}}
"""
        
        file_path = os.path.join(output_dir, "TestHarness.java")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(test_class_content)
        
        return file_path


class JavaProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Procesador de Proyectos Java")
        self.root.geometry("900x700")
        
        self.processor = JavaProjectProcessor()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid para expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Procesador de Proyectos Java", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Botón para cargar archivo
        ttk.Label(main_frame, text="Archivo del proyecto Java:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.file_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.file_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        ttk.Button(main_frame, text="Examinar", command=self.browse_file).grid(row=1, column=2, padx=(5, 0))
        
        # Package común
        ttk.Label(main_frame, text="Package común:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.common_package = tk.StringVar(value="package")
        ttk.Entry(main_frame, textvariable=self.common_package, width=30).grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        
        # Lista de clases
        ttk.Label(main_frame, text="Clases disponibles:").grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        ttk.Label(main_frame, text="Clases seleccionadas:").grid(row=3, column=1, sticky=tk.W, pady=(10, 5))
        
        # Listboxes para clases disponibles y seleccionadas
        self.available_listbox = tk.Listbox(main_frame, selectmode=tk.MULTIPLE, height=10)
        self.available_listbox.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.selected_listbox = tk.Listbox(main_frame, height=10)
        self.selected_listbox.grid(row=4, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Botones para mover clases
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=2, padx=(10, 0))
        
        ttk.Button(button_frame, text=">", command=self.add_class).pack(pady=5)
        ttk.Button(button_frame, text="<", command=self.remove_class).pack(pady=5)
        ttk.Button(button_frame, text=">>", command=self.add_all_classes).pack(pady=5)
        ttk.Button(button_frame, text="<<", command=self.remove_all_classes).pack(pady=5)
        
        # Clase y método principal para prueba
        ttk.Label(main_frame, text="Clase principal para prueba:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.main_class = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.main_class, width=30).grid(row=5, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(main_frame, text="Método principal para prueba:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.main_method = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.main_method, width=30).grid(row=6, column=1, sticky=tk.W, padx=(5, 0))
        
        # Botón para procesar
        ttk.Button(main_frame, text="Procesar y Generar Clases", command=self.process_classes).grid(row=7, column=0, columnspan=3, pady=10)
        
        # Área de texto para mostrar resultados
        ttk.Label(main_frame, text="Resultados y detalles:").grid(row=8, column=0, sticky=tk.W, pady=(10, 5))
        self.result_text = scrolledtext.ScrolledText(main_frame, width=80, height=15)
        self.result_text.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar expansión
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        main_frame.rowconfigure(9, weight=1)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de proyecto Java",
            filetypes=[("Text files", "*.txt"), ("Java files", "*.java"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            if self.processor.load_project(filename):
                classes = self.processor.extract_classes()
                self.update_available_classes(classes)
    
    def update_available_classes(self, classes):
        """Actualiza la lista de clases disponibles"""
        self.available_listbox.delete(0, tk.END)
        for class_name in classes:
            self.available_listbox.insert(tk.END, class_name)
    
    def add_class(self):
        """Añade clases seleccionadas a la lista de seleccionadas"""
        selected_indices = self.available_listbox.curselection()
        for i in selected_indices:
            class_name = self.available_listbox.get(i)
            if class_name not in self.selected_listbox.get(0, tk.END):
                self.selected_listbox.insert(tk.END, class_name)
    
    def remove_class(self):
        """Elimina clases seleccionadas de la lista de seleccionadas"""
        selected_indices = self.selected_listbox.curselection()
        for i in selected_indices:
            self.selected_listbox.delete(i)
    
    def add_all_classes(self):
        """Añade todas las clases a la lista de seleccionadas"""
        self.selected_listbox.delete(0, tk.END)
        for i in range(self.available_listbox.size()):
            class_name = self.available_listbox.get(i)
            self.selected_listbox.insert(tk.END, class_name)
    
    def remove_all_classes(self):
        """Elimina todas las clases de la lista de seleccionadas"""
        self.selected_listbox.delete(0, tk.END)
    
    def process_classes(self):
        """Procesa las clases seleccionadas y genera las versiones modificadas"""
        if not self.file_path.get():
            messagebox.showerror("Error", "Por favor, seleccione un archivo de proyecto primero")
            return
            
        selected_classes = list(self.selected_listbox.get(0, tk.END))
        if not selected_classes:
            messagebox.showerror("Error", "Por favor, seleccione al menos una clase")
            return
            
        # Actualizar el package común
        self.processor.common_package = self.common_package.get()
        self.processor.selected_classes = selected_classes
        
        # Seleccionar directorio de salida
        output_dir = filedialog.askdirectory(title="Seleccionar directorio de salida")
        if not output_dir:
            return
            
        # Generar clases modificadas
        try:
            generated_files = self.processor.generate_modified_classes(output_dir)
            
            # Crear clase de prueba si se especificó clase y método principal
            main_class = self.main_class.get()
            main_method = self.main_method.get()
            if main_class and main_method:
                test_file = self.processor.create_test_harness(output_dir, main_class, main_method)
                generated_files.append(test_file)
            
            # Mostrar resultados
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Procesamiento completado!\n\n")
            self.result_text.insert(tk.END, f"Package común: {self.processor.common_package}\n")
            self.result_text.insert(tk.END, f"Clases procesadas: {len(generated_files)}\n\n")
            self.result_text.insert(tk.END, "Archivos generados:\n")
            for file_path in generated_files:
                self.result_text.insert(tk.END, f"- {os.path.basename(file_path)}\n")
            
            self.result_text.insert(tk.END, f"\nDirectorio de salida: {output_dir}\n")
            
            messagebox.showinfo("Éxito", f"Se generaron {len(generated_files)} archivos en el directorio de salida")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar las clases: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = JavaProcessorApp(root)
    root.mainloop()
