import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import threading
import xml.etree.ElementTree as ET
import yaml
import re

class SpringBootAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Proyectos Spring Boot")
        self.root.geometry("900x700")
        self.project_path = tk.StringVar()
        self.analysis_running = False
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        ttk.Label(main_frame, text="Ruta del proyecto:").grid(row=0, column=0, sticky=tk.W, pady=5)
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        path_frame.columnconfigure(0, weight=1)
        ttk.Entry(path_frame, textvariable=self.project_path).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(path_frame, text="Examinar", command=self.browse_project).grid(row=0, column=1)

        options_frame = ttk.LabelFrame(main_frame, text="Opciones de análisis", padding="5")
        options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.analyze_config = tk.BooleanVar(value=True)
        self.analyze_dependencies = tk.BooleanVar(value=True)
        self.analyze_architecture = tk.BooleanVar(value=True)
        self.analyze_controllers = tk.BooleanVar(value=True)
        self.analyze_security = tk.BooleanVar(value=True)
        self.analyze_persistence = tk.BooleanVar(value=True)
        self.analyze_tests = tk.BooleanVar(value=True)
        self.analyze_devops = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Configuración", variable=self.analyze_config).grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Checkbutton(options_frame, text="Dependencias", variable=self.analyze_dependencies).grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Checkbutton(options_frame, text="Arquitectura", variable=self.analyze_architecture).grid(row=0, column=2, sticky=tk.W, padx=5)
        ttk.Checkbutton(options_frame, text="Controladores", variable=self.analyze_controllers).grid(row=1, column=0, sticky=tk.W, padx=5)
        ttk.Checkbutton(options_frame, text="Seguridad", variable=self.analyze_security).grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Checkbutton(options_frame, text="Persistencia", variable=self.analyze_persistence).grid(row=1, column=2, sticky=tk.W, padx=5)
        ttk.Checkbutton(options_frame, text="Pruebas", variable=self.analyze_tests).grid(row=2, column=0, sticky=tk.W, padx=5)
        ttk.Checkbutton(options_frame, text="DevOps", variable=self.analyze_devops).grid(row=2, column=1, sticky=tk.W, padx=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Analizar Proyecto", command=self.start_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generar Reporte", command=self.generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.clear_output).pack(side=tk.LEFT, padx=5)

        ttk.Label(main_frame, text="Resultados del análisis:").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        self.output_area = scrolledtext.ScrolledText(main_frame, width=100, height=30, wrap=tk.WORD)
        self.output_area.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))

        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        main_frame.rowconfigure(4, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def browse_project(self):
        path = filedialog.askdirectory(title="Seleccionar directorio del proyecto")
        if path:
            self.project_path.set(path)

    def start_analysis(self):
        if not self.project_path.get():
            messagebox.showerror("Error", "Por favor, selecciona un directorio de proyecto")
            return
        if self.analysis_running:
            return
        self.analysis_running = True
        self.progress.start()
        self.output_area.delete(1.0, tk.END)
        self.output_area.insert(tk.END, "Iniciando análisis...\n")
        thread = threading.Thread(target=self.analyze_project)
        thread.daemon = True
        thread.start()

    def analyze_project(self):
        try:
            project_path = self.project_path.get()
            analysis_results = {}
            analysis_results["contexto_general"] = self.analyze_general_context(project_path)
            if self.analyze_config.get():
                analysis_results["configuracion"] = self.analyze_configuration(project_path)
            if self.analyze_dependencies.get():
                analysis_results["dependencias"] = self.analyze_dependencies(project_path)
            if self.analyze_architecture.get():
                analysis_results["arquitectura"] = self.analyze_architecture(project_path)
            if self.analyze_controllers.get():
                analysis_results["controladores"] = self.analyze_controllers(project_path)
            if self.analyze_security.get():
                analysis_results["seguridad"] = self.analyze_security(project_path)
            if self.analyze_persistence.get():
                analysis_results["persistencia"] = self.analyze_persistence(project_path)
            if self.analyze_tests.get():
                analysis_results["pruebas"] = self.analyze_tests(project_path)
            if self.analyze_devops.get():
                analysis_results["devops"] = self.analyze_devops(project_path)
            analysis_results["comparacion"] = self.compare_with_monolith(analysis_results)
            self.display_results(analysis_results)
        except Exception as e:
            self.output_area.insert(tk.END, f"Error durante el análisis: {str(e)}\n")
        finally:
            self.analysis_running = False
            self.progress.stop()

    # --- Analysis Methods ---
    # ... (Keep all analyze_* methods as in your latest version, no need for duplicate definitions) ...

    # Utility Methods
    def find_files(self, directory, filename_pattern):
        matches = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if filename_pattern.lower() in file.lower():
                    matches.append(os.path.join(root, file))
        return matches

    def find_java_directories(self, project_path):
        java_dirs = []
        for root, dirs, files in os.walk(project_path):
            if 'src/main/java' in root:
                java_dirs.append(root)
            elif 'src' in root and 'java' in dirs:
                java_dirs.append(os.path.join(root, 'java'))
        return java_dirs

    def is_microservices(self, project_path):
        pom_files = self.find_files(project_path, "pom.xml")
        for pom_file in pom_files:
            try:
                tree = ET.parse(pom_file)
                root = tree.getroot()
                ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}
                modules = root.findall('maven:modules/maven:module', namespaces=ns) or root.findall('modules/module')
                if modules and len(modules) > 1:
                    return True
            except:
                pass
        app_files = self.find_files(project_path, "Application.java")
        if len(app_files) > 1:
            return True
        docker_files = self.find_files(project_path, "Dockerfile")
        if len(docker_files) > 1:
            return True
        k8s_files = self.find_files(project_path, "deployment.yaml")
        k8s_files.extend(self.find_files(project_path, "deployment.yml"))
        k8s_files.extend(self.find_files(project_path, "service.yaml"))
        k8s_files.extend(self.find_files(project_path, "service.yml"))
        if len(k8s_files) > 1:
            return True
        build_files = []
        build_files.extend(self.find_files(project_path, "pom.xml"))
        build_files.extend(self.find_files(project_path, "build.gradle"))
        for build_file in build_files:
            try:
                if build_file.endswith('pom.xml'):
                    tree = ET.parse(build_file)
                    root = tree.getroot()
                    ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}
                    dependencies = root.findall('.//maven:dependency', namespaces=ns) or root.findall('.//dependency')
                    for dep in dependencies:
                        dep_artifact = dep.findtext('maven:artifactId', namespaces=ns) or dep.findtext('artifactId')
                        if 'spring-cloud' in dep_artifact.lower():
                            return True
                elif build_file.endswith('build.gradle'):
                    with open(build_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if 'spring-cloud' in content.lower():
                            return True
            except:
                pass
        return False

    def display_results(self, analysis_results):
        self.output_area.delete(1.0, tk.END)
        for section, content in analysis_results.items():
            self.output_area.insert(tk.END, content)
            self.output_area.insert(tk.END, "\n")
        self.output_area.insert(tk.END, "=== RESUMEN Y RECOMENDACIONES FINALES ===\n\n")
        recommendations = self.generate_recommendations(analysis_results)
        for rec in recommendations:
            self.output_area.insert(tk.END, f"• {rec}\n")
        self.output_area.insert(tk.END, "\n=== ANÁLISIS COMPLETADO ===\n")
        self.output_area.insert(tk.END, "Revise los resultados arriba y genere un reporte si es necesario.\n")

    def generate_recommendations(self, analysis_results):
        recommendations = []
        if "Microservicios" in analysis_results.get("contexto_general", ""):
            recommendations.append("Considerar implementar un API Gateway para unificar el acceso a los microservicios.")
            recommendations.append("Evaluar el uso de service discovery (Eureka, Consul) para la localización de servicios.")
            recommendations.append("Implementar circuit breakers (Resilience4j) para mejorar la tolerancia a fallos.")
        else:
            recommendations.append("Considerar modularizar la aplicación siguiendo principios de Domain-Driven Design.")
            recommendations.append("Evaluar la separación en módulos independientes para facilitar una futura migración a microservicios.")
        seguridad_content = analysis_results.get("seguridad", "")
        if "CSRF: Deshabilitado" in seguridad_content:
            recommendations.append("Revisar la configuración de CSRF. No deshabilitar sin una justificación de seguridad adecuada.")
        if not any(keyword in seguridad_content for keyword in ["JWT", "OAuth2", "Spring Security"]):
            recommendations.append("Considerar implementar Spring Security para proteger los endpoints de la aplicación.")
        pruebas_content = analysis_results.get("pruebas", "")
        if "Cobertura baja" in pruebas_content:
            recommendations.append("Aumentar la cobertura de pruebas, especialmente para la lógica de negocio crítica.")
        if "Testcontainers" not in pruebas_content and "Microservicios" in analysis_results.get("contexto_general", ""):
            recommendations.append("Considerar usar Testcontainers para pruebas de integración con bases de datos reales.")
        devops_content = analysis_results.get("devops", "")
        if "Spring Boot Actuator" not in devops_content:
            recommendations.append("Implementar Spring Boot Actuator para monitorización y gestión de la aplicación.")
        if not any(keyword in devops_content for keyword in ["Prometheus", "Grafana"]):
            recommendations.append("Considerar implementar métricas con Prometheus y dashboards con Grafana.")
        persistencia_content = analysis_results.get("persistencia", "")
        if "Flyway" not in persistencia_content and "Liquibase" not in persistencia_content:
            recommendations.append("Considerar usar Flyway o Liquibase para gestionar migraciones de base de datos.")
        return recommendations

    def generate_report(self):
        content = self.output_area.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("Advertencia", "No hay contenido para generar el reporte. Ejecute un análisis primero.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Markdown files", "*.md"), ("All files", "*.*")],
            title="Guardar reporte de análisis"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Éxito", f"Reporte guardado en: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el reporte: {str(e)}")

    def clear_output(self):
        self.output_area.delete(1.0, tk.END)

def main():
    root = tk.Tk()
    app = SpringBootAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
