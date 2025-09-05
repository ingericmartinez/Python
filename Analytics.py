import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import subprocess
import threading
import json
import xml.etree.ElementTree as ET
import yaml
import re

class SpringBootAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Proyectos Spring Boot")
        self.root.geometry("900x700")
        
        # Variables
        self.project_path = tk.StringVar()
        self.analysis_running = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Selección de proyecto
        ttk.Label(main_frame, text="Ruta del proyecto:").grid(row=0, column=0, sticky=tk.W, pady=5)
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        path_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(path_frame, textvariable=self.project_path).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(path_frame, text="Examinar", command=self.browse_project).grid(row=0, column=1)
        
        # Opciones de análisis
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
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Analizar Proyecto", command=self.start_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generar Reporte", command=self.generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.clear_output).pack(side=tk.LEFT, padx=5)
        
        # Área de salida
        ttk.Label(main_frame, text="Resultados del análisis:").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        
        self.output_area = scrolledtext.ScrolledText(main_frame, width=100, height=30, wrap=tk.WORD)
        self.output_area.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Configurar pesos para el redimensionamiento
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
        
        # Ejecutar el análisis en un hilo separado
        thread = threading.Thread(target=self.analyze_project)
        thread.daemon = True
        thread.start()
    
    def analyze_project(self):
        try:
            project_path = self.project_path.get()
            analysis_results = {}
            
            # 1. Contexto General del Proyecto
            analysis_results["contexto_general"] = self.analyze_general_context(project_path)
            
            # 2. Configuración Base
            if self.analyze_config.get():
                analysis_results["configuracion"] = self.analyze_configuration(project_path)
            
            # 3. Gestión de Dependencias
            if self.analyze_dependencies.get():
                analysis_results["dependencias"] = self.analyze_dependencies(project_path)
            
            # 4. Arquitectura del Código
            if self.analyze_architecture.get():
                analysis_results["arquitectura"] = self.analyze_architecture(project_path)
            
            # 5. Controladores REST
            if self.analyze_controllers.get():
                analysis_results["controladores"] = self.analyze_controllers(project_path)
            
            # 6. Seguridad y Autenticación
            if self.analyze_security.get():
                analysis_results["seguridad"] = self.analyze_security(project_path)
            
            # 7. Persistencia y Base de Datos
            if self.analyze_persistence.get():
                analysis_results["persistencia"] = self.analyze_persistence(project_path)
            
            # 8. Pruebas y Calidad
            if self.analyze_tests.get():
                analysis_results["pruebas"] = self.analyze_tests(project_path)
            
            # 9. Observabilidad y DevOps
            if self.analyze_devops.get():
                analysis_results["devops"] = self.analyze_devops(project_path)
            
            # 10. Comparación con Arquitectura Monolítica
            analysis_results["comparacion"] = self.compare_with_monolith(analysis_results)
            
            # Mostrar resultados
            self.display_results(analysis_results)
            
        except Exception as e:
            self.output_area.insert(tk.END, f"Error durante el análisis: {str(e)}\n")
        finally:
            self.analysis_running = False
            self.progress.stop()
    
    def analyze_general_context(self, project_path):
        result = "=== CONTEXTO GENERAL DEL PROYECTO ===\n\n"
        
        # Detectar tipo de arquitectura
        if self.is_microservices(project_path):
            result += "Tipo de arquitectura: Microservicios\n"
        else:
            result += "Tipo de arquitectura: Monolito\n"
        
        # Detectar archivos de despliegue
        deployment_methods = []
        if self.find_files(project_path, "Dockerfile"):
            deployment_methods.append("Docker")
        if self.find_files(project_path, "docker-compose.yml") or self.find_files(project_path, "docker-compose.yaml"):
            deployment_methods.append("Docker Compose")
        if self.find_files(project_path, "kubernetes.yml") or self.find_files(project_path, "kubernetes.yaml") or self.find_files(project_path, "deployment.yml"):
            deployment_methods.append("Kubernetes")
        
        if deployment_methods:
            result += f"Métodos de despliegue detectados: {', '.join(deployment_methods)}\n"
        else:
            result += "No se detectaron métodos de despliegue específicos (Docker/Kubernetes)\n"
        
        # Detectar dominio funcional (basado en nombres de paquetes)
        java_dirs = self.find_java_directories(project_path)
        if java_dirs:
            package_names = [os.path.basename(dir) for dir in java_dirs]
            result += f"Dominios detectados: {', '.join(package_names)}\n"
        
        result += "\n"
        return result
    
    def analyze_configuration(self, project_path):
        result = "=== CONFIGURACIÓN BASE ===\n\n"
        
        # Buscar archivos de configuración
        config_files = []
        config_files.extend(self.find_files(project_path, "application.properties"))
        config_files.extend(self.find_files(project_path, "application.yml"))
        config_files.extend(self.find_files(project_path, "application.yaml"))
        
        if not config_files:
            result += "No se encontraron archivos de configuración principales.\n"
            return result
        
        for config_file in config_files:
            result += f"Archivo de configuración: {config_file}\n"
            
            try:
                if config_file.endswith('.properties'):
                    with open(config_file, 'r') as f:
                        content = f.read()
                        # Detectar perfiles activos
                        active_profiles = re.findall(r'spring\.profiles\.active=(.+)', content)
                        if active_profiles:
                            result += f"Perfiles activos: {active_profiles[0]}\n"
                        
                        # Detectar puerto
                        server_port = re.findall(r'server\.port=(\d+)', content)
                        if server_port:
                            result += f"Puerto del servidor: {server_port[0]}\n"
                        
                        # Detectar base de datos
                        db_url = re.findall(r'spring\.datasource\.url=(.+)', content)
                        if db_url:
                            result += f"URL de base de datos: {db_url[0]}\n"
                
                elif config_file.endswith('.yml') or config_file.endswith('.yaml'):
                    with open(config_file, 'r') as f:
                        config_data = yaml.safe_load(f)
                        if config_data:
                            # Detectar perfiles activos
                            if 'spring' in config_data and 'profiles' in config_data['spring'] and 'active' in config_data['spring']['profiles']:
                                result += f"Perfiles activos: {config_data['spring']['profiles']['active']}\n"
                            
                            # Detectar puerto
                            if 'server' in config_data and 'port' in config_data['server']:
                                result += f"Puerto del servidor: {config_data['server']['port']}\n"
                            
                            # Detectar base de datos
                            if 'spring' in config_data and 'datasource' in config_data['spring'] and 'url' in config_data['spring']['datasource']:
                                result += f"URL de base de datos: {config_data['spring']['datasource']['url']}\n"
            
            except Exception as e:
                result += f"Error al leer el archivo de configuración: {str(e)}\n"
            
            result += "\n"
        
        return result
    
    def analyze_dependencies(self, project_path):
        result = "=== GESTIÓN DE DEPENDENCIAS ===\n\n"
        
        # Buscar archivos de dependencias
        build_files = []
        build_files.extend(self.find_files(project_path, "pom.xml"))
        build_files.extend(self.find_files(project_path, "build.gradle"))
        
        if not build_files:
            result += "No se encontraron archivos de gestión de dependencias.\n"
            return result
        
        for build_file in build_files:
            result += f"Archivo de dependencias: {build_file}\n"
            
            try:
                if build_file.endswith('pom.xml'):
                    tree = ET.parse(build_file)
                    root = tree.getroot()
                    
                    # Namespace para XML
                    ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}
                    
                    # Obtener groupId, artifactId y version
                    group_id = root.findtext('maven:groupId', namespaces=ns) or root.findtext('groupId')
                    artifact_id = root.findtext('maven:artifactId', namespaces=ns) or root.findtext('artifactId')
                    version = root.findtext('maven:version', namespaces=ns) or root.findtext('version')
                    
                    result += f"Proyecto: {group_id}:{artifact_id}:{version}\n\n"
                    
                    # Obtener dependencias
                    dependencies = root.findall('.//maven:dependency', namespaces=ns) or root.findall('.//dependency')
                    if dependencies:
                        result += "Dependencias principales:\n"
                        for dep in dependencies[:10]:  # Mostrar solo las primeras 10
                            dep_group = dep.findtext('maven:groupId', namespaces=ns) or dep.findtext('groupId')
                            dep_artifact = dep.findtext('maven:artifactId', namespaces=ns) or dep.findtext('artifactId')
                            dep_version = dep.findtext('maven:version', namespaces=ns) or dep.findtext('version')
                            result += f"  - {dep_group}:{dep_artifact}:{dep_version}\n"
                    
                    # Detectar plugins
                    plugins = root.findall('.//maven:plugin', namespaces=ns) or root.findall('.//plugin')
                    if plugins:
                        result += "\nPlugins detectados:\n"
                        for plugin in plugins[:5]:  # Mostrar solo los primeros 5
                            plugin_group = plugin.findtext('maven:groupId', namespaces=ns) or plugin.findtext('groupId')
                            plugin_artifact = plugin.findtext('maven:artifactId', namespaces=ns) or plugin.findtext('artifactId')
                            result += f"  - {plugin_group}:{plugin_artifact}\n"
                
                elif build_file.endswith('build.gradle'):
                    with open(build_file, 'r') as f:
                        content = f.read()
                        
                        # Detectar dependencias
                        dependencies = re.findall(r"implementation\s+['\"]([^'\"]+)['\"]", content)
                        dependencies.extend(re.findall(r"compile\s+['\"]([^'\"]+)['\"]", content))
                        
                        if dependencies:
                            result += "Dependencias principales:\n"
                            for dep in dependencies[:10]:  # Mostrar solo las primeras 10
                                result += f"  - {dep}\n"
                        
                        # Detectar plugins
                        plugins = re.findall(r"id\s+['\"]([^'\"]+)['\"]", content)
                        if plugins:
                            result += "\nPlugins detectados:\n"
                            for plugin in plugins[:5]:  # Mostrar solo los primeros 5
                                result += f"  - {plugin}\n"
            
            except Exception as e:
                result += f"Error al analizar el archivo de dependencias: {str(e)}\n"
            
            result += "\n"
        
        return result
    
    def analyze_architecture(self, project_path):
        result = "=== ARQUITECTURA DEL CÓDIGO ===\n\n"
        
        java_dirs = self.find_java_directories(project_path)
        if not java_dirs:
            result += "No se encontraron directorios Java en el proyecto.\n"
            return result
        
        # Analizar estructura de paquetes
        result += "Estructura de paquetes detectada:\n"
        for java_dir in java_dirs:
            for root, dirs, files in os.walk(java_dir):
                # Calcular nivel de anidamiento
                level = root.replace(java_dir, '').count(os.sep)
                indent = '  ' * level
                result += f"{indent}{os.path.basename(root)}/\n"
        
        # Detectar capas comunes
        layers = {"controller": 0, "service": 0, "repository": 0, "model": 0, "entity": 0, "dto": 0, "config": 0}
        
        for java_dir in java_dirs:
            for root, dirs, files in os.walk(java_dir):
                for file in files:
                    if file.endswith('.java'):
                        file_path = os.path.join(root, file)
                        for layer in layers:
                            if layer in file_path.lower():
                                layers[layer] += 1
        
        result += "\nPatrones detectados:\n"
        for layer, count in layers.items():
            if count > 0:
                result += f"  - {layer.capitalize()}: {count} archivos\n"
        
        # Detectar bounded contexts
        package_counts = {}
        for java_dir in java_dirs:
            for root, dirs, files in os.walk(java_dir):
                if files and any(f.endswith('.java') for f in files):
                    package_name = root.replace(java_dir, '').replace(os.sep, '.')
                    if package_name.startswith('.'):
                        package_name = package_name[1:]
                    if package_name:
                        package_counts[package_name] = len([f for f in files if f.endswith('.java')])
        
        if package_counts:
            result += "\nBounded contexts/dominios detectados:\n"
            for package, count in sorted(package_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                result += f"  - {package}: {count} clases\n"
        
        result += "\n"
        return result
    
    def analyze_controllers(self, project_path):
        result = "=== CONTROLADORES REST ===\n\n"
        
        java_dirs = self.find_java_directories(project_path)
        if not java_dirs:
            result += "No se encontraron directorios Java en el proyecto.\n"
            return result
        
        # Buscar controladores
        controllers = []
        for java_dir in java_dirs:
            for root, dirs, files in os.walk(java_dir):
                for file in files:
                    if file.endswith('.java') and ('controller' in root.lower() or 'Controller.java' in file):
                        controllers.append(os.path.join(root, file))
        
        if not controllers:
            result += "No se encontraron controladores REST.\n"
            return result
        
        result += f"Se encontraron {len(controllers)} controladores:\n\n"
        
        for controller in controllers[:5]:  # Analizar solo los primeros 5 controladores
            result += f"Controlador: {os.path.basename(controller)}\n"
            
            try:
                with open(controller, 'r') as f:
                    content = f.read()
                    
                    # Detectar anotaciones @RequestMapping, @GetMapping, etc.
                    mappings = re.findall(r'@(RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\([^)]*\)', content)
                    if mappings:
                        result += "  Endpoints detectados:\n"
                        for mapping in mappings:
                            result += f"    - {mapping}\n"
                    
                    # Detectar Swagger/OpenAPI
                    if '@Api' in content or '@Operation' in content or '@Tag' in content:
                        result += "  Documentación: Swagger/OpenAPI detectado\n"
                    
                    # Detectar validaciones
                    if '@Valid' in content or '@NotNull' in content or '@Size' in content:
                        result += "  Validaciones: Se detectan validaciones de entrada\n"
            
            except Exception as e:
                result += f"  Error al analizar el controlador: {str(e)}\n"
            
            result += "\n"
        
        return result
    
    def analyze_security(self, project_path):
        result = "=== SEGURIDAD Y AUTENTICACIÓN ===\n\n"
        
        java_dirs = self.find_java_directories(project_path)
        if not java_dirs:
            result += "No se encontraron directorios Java en el proyecto.\n"
            return result
        
        # Buscar configuraciones de seguridad
        security_configs = []
        for java_dir in java_dirs:
            for root, dirs, files in os.walk(java_dir):
                for file in files:
                    if file.endswith('.java') and ('security' in root.lower() or 'config' in root.lower()):
                        security_configs.append(os.path.join(root, file))
        
        # Buscar dependencias de seguridad en archivos de build
        build_files = []
        build_files.extend(self.find_files(project_path, "pom.xml"))
        build_files.extend(self.find_files(project_path, "build.gradle"))
        
        security_dependencies = []
        for build_file in build_files:
            try:
                if build_file.endswith('pom.xml'):
                    tree = ET.parse(build_file)
                    root = tree.getroot()
                    
                    # Namespace para XML
                    ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}
                    
                    # Buscar dependencias de seguridad
                    dependencies = root.findall('.//maven:dependency', namespaces=ns) or root.findall('.//dependency')
                    for dep in dependencies:
                        dep_group = dep.findtext('maven:groupId', namespaces=ns) or dep.findtext('groupId')
                        dep_artifact = dep.findtext('maven:artifactId', namespaces=ns) or dep.findtext('artifactId')
                        
                        if 'security' in dep_artifact.lower() or 'jwt' in dep_artifact.lower() or 'oauth' in dep_artifact.lower():
                            security_dependencies.append(f"{dep_group}:{dep_artifact}")
                
                elif build_file.endswith('build.gradle'):
                    with open(build_file, 'r') as f:
                        content = f.read()
                        
                        # Buscar dependencias de seguridad
                        deps = re.findall(r"(implementation|compile)\s+['\"]([^:'\"]+:[^:'\"]+)['\"]", content)
                        for dep_type, dep in deps:
                            if 'security' in dep.lower() or 'jwt' in dep.lower() or 'oauth' in dep.lower():
                                security_dependencies.append(dep)
            
            except Exception as e:
                result += f"Error al analizar dependencias de seguridad: {str(e)}\n"
        
        if security_dependencies:
            result += "Dependencias de seguridad detectadas:\n"
            for dep in security_dependencies:
                result += f"  - {dep}\n"
            result += "\n"
        
        if security_configs:
            result += f"Se encontraron {len(security_configs)} configuraciones de seguridad:\n"
            for config in security_configs[:3]:  # Analizar solo las primeras 3 configuraciones
                result += f"  - {os.path.basename(config)}\n"
            
            # Intentar detectar tipo de seguridad
            try:
                with open(security_configs[0], 'r') as f:
                    content = f.read()
                    
                    if 'extends WebSecurityConfigurerAdapter' in content:
                        result += "  Tipo: Spring Security tradicional\n"
                    elif '@EnableWebSecurity' in content:
                        result += "  Tipo: Spring Security (nueva configuración)\n"
                    
                    if 'JWT' in content or 'jwt' in content:
                        result += "  Autenticación: JWT detectado\n"
                    if 'OAuth2' in content or 'oauth' in content.lower():
                        result += "  Autenticación: OAuth2 detectado\n"
                    
                    if '@EnableGlobalMethodSecurity' in content:
                        result += "  Seguridad a nivel de método: Habilitada\n"
            
            except Exception as e:
                result += f"  Error al analizar configuración de seguridad: {str(e)}\n"
        else:
            result += "No se detectaron configuraciones de seguridad específicas.\n"
        
        result += "\n"
        return result
    
    def analyze_persistence(self, project_path):
        result = "=== PERSISTENCIA Y BASE DE DATOS ===\n\n"
        
        java_dirs = self.find_java_directories(project_path)
        if not java_dirs:
            result += "No se encontraron directorios Java en el proyecto.\n"
            return result
        
        # Buscar entidades y repositorios
        entities = []
        repositories = []
        for java_dir in java_dirs:
            for root, dirs, files in os.walk(java_dir):
                for file in files:
                    if file.endswith('.java'):
                        file_path = os.path.join(root, file)
                        if 'entity' in root.lower() or 'model' in root.lower():
                            entities.append(file_path)
                        elif 'repository' in root.lower() or 'dao' in root.lower():
                            repositories.append(file_path)
        
        result += f"Se encontraron {len(entities)} entidades y {len(repositories)} repositorios.\n\n"
        
        # Analizar algunas entidades
        if entities:
            result += "Ejemplo de entidades detectadas:\n"
            for entity in entities[:3]:  # Mostrar solo las primeras 3 entidades
                result += f"  - {os.path.basename(entity)}\n"
            
            # Intentar detectar anotaciones JPA
            try:
                with open(entities[0], 'r') as f:
                    content = f.read()
                    
                    if '@Entity' in content:
                        result += "  Framework: JPA detectado\n"
                    
                    if '@Table' in content:
                        result += "  Mapeo: Configuración de tablas detectada\n"
                    
                    relationships = []
                    if '@OneToMany' in content:
                        relationships.append("OneToMany")
                    if '@ManyToOne' in content:
                        relationships.append("ManyToOne")
                    if '@ManyToMany' in content:
                        relationships.append("ManyToMany")
                    if '@OneToOne' in content:
                        relationships.append("OneToOne")
                    
                    if relationships:
                        result += f"  Relaciones: {', '.join(relationships)} detectadas\n"
            
            except Exception as e:
                result += f"  Error al analizar entidad: {str(e)}\n"
            
            result += "\n"
        
        # Buscar herramientas de migración
        migration_tools = []
        if self.find_files(project_path, "flyway"):
            migration_tools.append("Flyway")
        if self.find_files(project_path, "liquibase"):
            migration_tools.append("Liquibase")
        
        if migration_tools:
            result += f"Herramientas de migración detectadas: {', '.join(migration_tools)}\n"
        
        result += "\n"
        return result
    
    def analyze_tests(self, project_path):
        result = "=== PRUEBAS Y CALIDAD ===\n\n"
        
        # Buscar directorios de pruebas
        test_dirs = []
        for root, dirs, files in os.walk(project_path):
            if 'test' in root.lower() and 'java' in root.lower():
                test_dirs.append(root)
        
        if not test_dirs:
            result += "No se encontraron directorios de pruebas.\n"
            return result
        
        # Contar archivos de prueba
        test_files = []
        for test_dir in test_dirs:
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    if file.endswith('.java'):
                        test_files.append(os.path.join(root, file))
        
        result += f"Se encontraron {len(test_files)} archivos de prueba.\n\n"
        
        # Analizar tipos de pruebas
        test_types = {"Unit": 0, "Integration": 0, "Other": 0}
        for test_file in test_files:
            if 'Test' in os.path.basename(test_file):
                test_types["Unit"] += 1
            elif 'IT' in os.path.basename(test_file) or 'IntegrationTest' in os.path.basename(test_file):
                test_types["Integration"] += 1
            else:
                test_types["Other"] += 1
        
        result += "Distribución de pruebas:\n"
        for test_type, count in test_types.items():
            if count > 0:
                result += f"  - {test_type}: {count} archivos\n"
        
        # Buscar herramientas de testing
        build_files = []
        build_files.extend(self.find_files(project_path, "pom.xml"))
        build_files.extend(self.find_files(project_path, "build.gradle"))
        
        testing_tools = []
        for build_file in build_files:
            try:
                if build_file.endswith('pom.xml'):
                    tree = ET.parse(build_file)
                    root = tree.getroot()
                    
                    # Namespace para XML
                    ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}
                    
                    # Buscar dependencias de testing
                    dependencies = root.findall('.//maven:dependency', namespaces=ns) or root.findall('.//dependency')
                    for dep in dependencies:
                        dep_group = dep.findtext('maven:groupId', namespaces=ns) or dep.findtext('groupId')
                        dep_artifact = dep.findtext('maven:artifactId', namespaces=ns) or dep.findtext('artifactId')
                        
                        if 'junit' in dep_artifact.lower():
                            testing_tools.append("JUnit")
                        elif 'mockito' in dep_artifact.lower():
                            testing_tools.append("Mockito")
                        elif 'testcontainers' in dep_artifact.lower():
                            testing_tools.append("Testcontainers")
                
                elif build_file.endswith('build.gradle'):
                    with open(build_file, 'r') as f:
                        content = f.read()
                        
                        # Buscar dependencias de testing
                        if 'junit' in content.lower():
                            testing_tools.append("JUnit")
                        if 'mockito' in content.lower():
                            testing_tools.append("Mockito")
                        if 'testcontainers' in content.lower():
                            testing_tools.append("Testcontainers")
            
            except Exception as e:
                result += f"Error al analizar herramientas de testing: {str(e)}\n"
        
        if testing_tools:
            result += f"\nHerramientas de testing detectadas: {', '.join(set(testing_tools))}\n"
        
        # Buscar configuraciones de calidad de código
        quality_tools = []
        if self.find_files(project_path, "sonar"):
            quality_tools.append("SonarQube")
        if self.find_files(project_path, "checkstyle"):
            quality_tools.append("Checkstyle")
        if self.find_files(project_path, "pmd"):
            quality_tools.append("PMD")
        if self.find_files(project_path, "spotbugs"):
            quality_tools.append("SpotBugs")
        
        if quality_tools:
            result += f"Herramientas de calidad de código detectadas: {', '.join(quality_tools)}\n"
        
        result += "\n"
        return result
    
    def analyze_devops(self, project_path):
        result = "=== OBSERVABILIDAD Y DEVOPS ===\n\n"
        
        # Buscar configuraciones de logging
        logging_configs = []
        logging_configs.extend(self.find_files(project_path, "logback.xml"))
        logging_configs.extend(self.find_files(project_path, "log4j"))
        logging_configs.extend(self.find_files(project_path, "logging"))
        
        if logging_configs:
            result += "Configuraciones de logging detectadas:\n"
            for config in logging_configs:
                result += f"  - {os.path.basename(config)}\n"
            result += "\n"
        
        # Buscar configuraciones de métricas y trazabilidad
        monitoring_tools = []
        if self.find_files(project_path, "prometheus"):
            monitoring_tools.append("Prometheus")
        if self.find_files(project_path, "grafana"):
            monitoring_tools.append("Grafana")
        if self.find_files(project_path, "elk"):
            monitoring_tools.append("ELK")
        if self.find_files(project_path, "zipkin"):
            monitoring_tools.append("Zipkin")
        if self.find_files(project_path, "sleuth"):
            monitoring_tools.append("Sleuth")
        
        if monitoring_tools:
            result += f"Herramientas de monitoreo detectadas: {', '.join(monitoring_tools)}\n"
        
        # Buscar configuraciones CI/CD
        ci_cd_files = []
        ci_cd_files.extend(self.find_files(project_path, "jenkins"))
        ci_cd_files.extend(self.find_files(project_path, "github"))
        ci_cd_files.extend(self.find_files(project_path, "gitlab"))
        ci_cd_files.extend(self.find_files(project_path, "azure-pipelines"))
        ci_cd_files.extend(self.find_files(project_path, ".github"))
        ci_cd_files.extend(self.find_files(project_path, ".gitlab"))
        
        if ci_cd_files:
            result += "\nConfiguraciones CI/CD detectadas:\n"
            for file in ci_cd_files:
                result += f"  - {os.path.basename(file)}\n"
        
        result += "\n"
        return result
    
    def compare_with_monolith(self, analysis_results):
        result = "=== COMPARACIÓN CON ARQUITECTURA MONOLÍTICA ===\n\n"
        
        # Determinar si es microservicio o monolito
        is_microservices = "Microservicios" in analysis_results.get("contexto_general", "")
        
        if is_microservices:
            result += "El proyecto sigue una arquitectura de microservicios.\n\n"
            result += "Ventajas respecto a un monolito:\n"
            result += "  - Mejor escalabilidad horizontal por servicio\n"
            result += "  - Mayor independencia en el desarrollo y despliegue\n"
            result += "  - Tecnologías específicas por dominio\n"
            result += "  - Mayor tolerancia a fallos\n\n"
            result += "Desafíos:\n"
            result += "  - Mayor complejidad en la operación\n"
            result += "  - Necesidad de orquestación (Kubernetes, Docker Compose)\n"
            result += "  - Comunicación entre servicios más compleja\n"
            result += "  - Mayor overhead en transacciones distribuidas\n"
        else:
            result += "El proyecto sigue una arquitectura monolítica.\n\n"
            result += "Ventajas respecto a microservicios:\n"
            result += "  - Menor complejidad operativa\n"
            result += "  - Desarrollo y testing más sencillos\n"
            result += "  - Transacciones ACID más fáciles de implementar\n"
            result += "  - Menor overhead de comunicación\n\n"
            result += "Desafíos:\n"
            result += "  - Escalabilidad limitada\n"
            result += "  - Acoplamiento más fuerte entre componentes\n"
            result += "  - Dificultad para adoptar tecnologías heterogéneas\n"
            result += "  - Despliegues más riesgosos\n"
        
        result += "\n"
        return result
    
    def display_results(self, analysis_results):
        self.output_area.delete(1.0, tk.END)
        
        for section, content in analysis_results.items():
            self.output_area.insert(tk.END, content)
            self.output_area.insert(tk.END, "\n")
        
        self.output_area.insert(tk.END, "=== ANÁLISIS COMPLETADO ===\n")
        self.output_area.insert(tk.END, "Revise los resultados arriba y genere un reporte si es necesario.\n")
    
    def generate_report(self):
        content = self.output_area.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("Advertencia", "No hay contenido para generar el reporte. Ejecute un análisis primero.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Guardar reporte de análisis"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(content)
                messagebox.showinfo("Éxito", f"Reporte guardado en: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el reporte: {str(e)}")
    
    def clear_output(self):
        self.output_area.delete(1.0, tk.END)
    
    # Métodos utilitarios
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
        # Heurística simple para detectar microservicios
        # 1. Buscar múltiples módulos en Maven/Gradle
        # 2. Buscar múltiples aplicaciones Spring Boot
        # 3. Buscar configuraciones de Docker/Kubernetes para múltiples servicios
        
        # Verificar si es un proyecto multi-módulo de Maven
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
        
        # Verificar si hay múltiples archivos de aplicación
        app_files = self.find_files(project_path, "Application.java")
        if len(app_files) > 1:
            return True
        
        # Verificar configuraciones de Docker/Kubernetes para múltiples servicios
        docker_files = self.find_files(project_path, "Dockerfile")
        if len(docker_files) > 1:
            return True
        
        k8s_files = self.find_files(project_path, "deployment.yaml")
        k8s_files.extend(self.find_files(project_path, "deployment.yml"))
        k8s_files.extend(self.find_files(project_path, "service.yaml"))
        k8s_files.extend(self.find_files(project_path, "service.yml"))
        
        if len(k8s_files) > 1:
            return True
        
        return False

def main():
    root = tk.Tk()
    app = SpringBootAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
      # ... (continuación desde el código anterior)

    def analyze_controllers(self, project_path):
        result = "=== CONTROLADORES REST ===\n\n"
        
        java_dirs = self.find_java_directories(project_path)
        if not java_dirs:
            result += "No se encontraron directorios Java en el proyecto.\n"
            return result
        
        # Buscar controladores
        controllers = []
        for java_dir in java_dirs:
            for root, dirs, files in os.walk(java_dir):
                for file in files:
                    if file.endswith('.java'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if '@RestController' in content or '@Controller' in content:
                                controllers.append((file_path, content))
        
        if not controllers:
            result += "No se encontraron controladores REST.\n"
            return result
        
        result += f"Se encontraron {len(controllers)} controladores:\n\n"
        
        for controller_path, content in controllers[:5]:  # Analizar solo los primeros 5 controladores
            result += f"Controlador: {os.path.basename(controller_path)}\n"
            
            try:
                # Detectar anotaciones de mapeo
                mappings = re.findall(r'@(RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\([^)]*\)', content)
                if mappings:
                    result += "  Endpoints detectados:\n"
                    for mapping in mappings[:10]:  # Mostrar solo los primeros 10 endpoints
                        # Extraer la ruta si está disponible
                        path_match = re.search(r'@[A-Za-z]*Mapping\([^)]*value\s*=\s*["\']([^"\']+)["\']', mapping)
                        if path_match:
                            result += f"    - {mapping.split('(')[0]}: {path_match.group(1)}\n"
                        else:
                            # Buscar la ruta directamente en la anotación
                            path_direct = re.search(r'@[A-Za-z]*Mapping\(["\']([^"\']+)["\']', mapping)
                            if path_direct:
                                result += f"    - {mapping.split('(')[0]}: {path_direct.group(1)}\n"
                            else:
                                result += f"    - {mapping}\n"
                
                # Detectar Swagger/OpenAPI
                swagger_annotations = re.findall(r'@(Api|Operation|Tag|ApiResponse|ApiParam)\([^)]*\)', content)
                if swagger_annotations:
                    result += f"  Documentación: Swagger/OpenAPI detectado ({len(swagger_annotations)} anotaciones)\n"
                
                # Detectar validaciones
                validation_annotations = re.findall(r'@(Valid|NotNull|NotBlank|NotEmpty|Size|Min|Max|Email|Pattern)\([^)]*\)', content)
                if validation_annotations:
                    result += f"  Validaciones: {len(validation_annotations)} anotaciones de validación detectadas\n"
                
                # Detectar manejo de excepciones
                exception_handlers = re.findall(r'@(ExceptionHandler|ControllerAdvice|RestControllerAdvice)\([^)]*\)', content)
                if exception_handlers:
                    result += f"  Manejo de excepciones: {len(exception_handlers)} manejadores detectados\n"
            
            except Exception as e:
                result += f"  Error al analizar el controlador: {str(e)}\n"
            
            result += "\n"
        
        return result

    def analyze_security(self, project_path):
        result = "=== SEGURIDAD Y AUTENTICACIÓN ===\n\n"
        
        java_dirs = self.find_java_directories(project_path)
        if not java_dirs:
            result += "No se encontraron directorios Java en el proyecto.\n"
            return result
        
        # Buscar configuraciones de seguridad
        security_configs = []
        security_files = []
        for java_dir in java_dirs:
            for root, dirs, files in os.walk(java_dir):
                for file in files:
                    if file.endswith('.java'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if any(keyword in content for keyword in ['SpringSecurity', 'WebSecurityConfigurerAdapter', 
                                                                     '@EnableWebSecurity', 'SecurityConfig', 
                                                                     'JWT', 'OAuth2', 'Authentication', 'Authorization']):
                                security_files.append((file_path, content))
                                if any(keyword in content for keyword in ['@Configuration', '@EnableWebSecurity', 
                                                                         'WebSecurityConfigurerAdapter', 'SecurityConfig']):
                                    security_configs.append((file_path, content))
        
        # Buscar dependencias de seguridad en archivos de build
        build_files = []
        build_files.extend(self.find_files(project_path, "pom.xml"))
        build_files.extend(self.find_files(project_path, "build.gradle"))
        
        security_dependencies = set()
        for build_file in build_files:
            try:
                if build_file.endswith('pom.xml'):
                    tree = ET.parse(build_file)
                    root = tree.getroot()
                    
                    # Namespace para XML
                    ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}
                    
                    # Buscar dependencias de seguridad
                    dependencies = root.findall('.//maven:dependency', namespaces=ns) or root.findall('.//dependency')
                    for dep in dependencies:
                        dep_group = dep.findtext('maven:groupId', namespaces=ns) or dep.findtext('groupId')
                        dep_artifact = dep.findtext('maven:artifactId', namespaces=ns) or dep.findtext('artifactId')
                        
                        if any(keyword in dep_artifact.lower() for keyword in ['security', 'jwt', 'oauth', 'auth', 'keycloak']):
                            security_dependencies.add(f"{dep_group}:{dep_artifact}")
                
                elif build_file.endswith('build.gradle'):
                    with open(build_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Buscar dependencias de seguridad
                        deps = re.findall(r"(implementation|compile|api)\s+['\"]([^:'\"]+:[^:'\"]+)['\"]", content)
                        for dep_type, dep in deps:
                            if any(keyword in dep.lower() for keyword in ['security', 'jwt', 'oauth', 'auth', 'keycloak']):
                                security_dependencies.add(dep)
            
            except Exception as e:
                result += f"Error al analizar dependencias de seguridad: {str(e)}\n"
        
        if security_dependencies:
            result += "Dependencias de seguridad detectadas:\n"
            for dep in sorted(security_dependencies):
                result += f"  - {dep}\n"
            result += "\n"
        
        if security_configs:
            result += f"Se encontraron {len(security_configs)} configuraciones de seguridad:\n"
            for config_path, content in security_configs[:3]:  # Analizar solo las primeras 3 configuraciones
                result += f"  - {os.path.basename(config_path)}\n"
                
                # Detectar tipo de seguridad
                if 'extends WebSecurityConfigurerAdapter' in content:
                    result += "    Tipo: Spring Security tradicional (WebSecurityConfigurerAdapter)\n"
                elif '@EnableWebSecurity' in content:
                    result += "    Tipo: Spring Security (nueva configuración DSL)\n"
                
                # Detectar mecanismos de autenticación
                auth_mechanisms = []
                if 'JWT' in content or 'jwt' in content.lower():
                    auth_mechanisms.append("JWT")
                if 'OAuth2' in content or 'oauth' in content.lower():
                    auth_mechanisms.append("OAuth2")
                if 'LDAP' in content or 'ldap' in content.lower():
                    auth_mechanisms.append("LDAP")
                if 'BasicAuthentication' in content or 'basic' in content.lower():
                    auth_mechanisms.append("HTTP Basic")
                
                if auth_mechanisms:
                    result += f"    Mecanismos de autenticación: {', '.join(auth_mechanisms)}\n"
                
                # Detectar autorización
                if '@EnableGlobalMethodSecurity' in content:
                    result += "    Seguridad a nivel de método: Habilitada\n"
                
                # Detectar CSRF
                if 'csrf().disable()' in content:
                    result += "    ⚠️  CSRF: Deshabilitado (posible vulnerabilidad)\n"
                elif 'csrf().enable()' in content or 'csrf()' in content:
                    result += "    CSRF: Habilitado\n"
            
            result += "\n"
        
        # Analizar archivos de propiedades para configuraciones de seguridad
        config_files = []
        config_files.extend(self.find_files(project_path, "application.properties"))
        config_files.extend(self.find_files(project_path, "application.yml"))
        config_files.extend(self.find_files(project_path, "application.yaml"))
        
        security_properties = []
        for config_file in config_files:
            try:
                if config_file.endswith('.properties'):
                    with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        security_lines = [line for line in content.split('\n') if any(keyword in line for keyword in 
                                 ['security', 'auth', 'jwt', 'oauth', 'token', 'keycloak'])]
                        security_properties.extend(security_lines)
                
                elif config_file.endswith('.yml') or config_file.endswith('.yaml'):
                    with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        security_lines = [line for line in content.split('\n') if any(keyword in line for keyword in 
                                 ['security', 'auth', 'jwt', 'oauth', 'token', 'keycloak'])]
                        security_properties.extend(security_lines)
            
            except Exception as e:
                result += f"Error al analizar configuraciones de seguridad: {str(e)}\n"
        
        if security_properties:
            result += "Configuraciones de seguridad en archivos de propiedades:\n"
            for prop in security_properties[:10]:  # Mostrar solo las primeras 10
                result += f"  - {prop}\n"
        
        if not security_configs and not security_dependencies and not security_properties:
            result += "No se detectaron configuraciones de seguridad específicas.\n"
        
        result += "\n"
        return result

    def analyze_persistence(self, project_path):
        result = "=== PERSISTENCIA Y BASE DE DATOS ===\n\n"
        
        java_dirs = self.find_java_directories(project_path)
        if not java_dirs:
            result += "No se encontraron directorios Java en el proyecto.\n"
            return result
        
        # Buscar entidades y repositorios
        entities = []
        repositories = []
        for java_dir in java_dirs:
            for root, dirs, files in os.walk(java_dir):
                for file in files:
                    if file.endswith('.java'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if '@Entity' in content or '@Table' in content:
                                entities.append((file_path, content))
                            elif any(annotation in content for annotation in 
                                    ['@Repository', 'JpaRepository', 'CrudRepository', 'PagingAndSortingRepository']):
                                repositories.append((file_path, content))
        
        result += f"Se encontraron {len(entities)} entidades y {len(repositories)} repositorios.\n\n"
        
        # Analizar algunas entidades
        if entities:
            result += "Ejemplo de entidades detectadas:\n"
            for entity_path, content in entities[:3]:  # Mostrar solo las primeras 3 entidades
                result += f"  - {os.path.basename(entity_path)}\n"
                
                # Detectar anotaciones JPA
                jpa_annotations = re.findall(r'@(Entity|Table|Id|GeneratedValue|Column|OneToMany|ManyToOne|ManyToMany|OneToOne)\([^)]*\)', content)
                if jpa_annotations:
                    result += f"    Anotaciones JPA: {len(jpa_annotations)} detectadas\n"
                
                # Detectar relaciones
                relationships = []
                if '@OneToMany' in content:
                    relationships.append("OneToMany")
                if '@ManyToOne' in content:
                    relationships.append("ManyToOne")
                if '@ManyToMany' in content:
                    relationships.append("ManyToMany")
                if '@OneToOne' in content:
                    relationships.append("OneToOne")
                
                if relationships:
                    result += f"    Relaciones: {', '.join(relationships)} detectadas\n"
            
            result += "\n"
        
        # Analizar repositorios
        if repositories:
            result += "Ejemplo de repositorios detectados:\n"
            for repo_path, content in repositories[:3]:  # Mostrar solo los primeros 3 repositorios
                result += f"  - {os.path.basename(repo_path)}\n"
                
                # Detectar tipo de repositorio
                if 'JpaRepository' in content:
                    result += "    Tipo: JpaRepository\n"
                elif 'CrudRepository' in content:
                    result += "    Tipo: CrudRepository\n"
                elif 'PagingAndSortingRepository' in content:
                    result += "    Tipo: PagingAndSortingRepository\n"
                
                # Detectar consultas personalizadas
                custom_queries = re.findall(r'@Query\([^)]*\)', content)
                if custom_queries:
                    result += f"    Consultas personalizadas: {len(custom_queries)} detectadas\n"
            
            result += "\n"
        
        # Buscar herramientas de migración
        migration_tools = []
        flyway_files = self.find_files(project_path, "flyway")
        liquibase_files = self.find_files(project_path, "liquibase")
        
        if flyway_files:
            migration_tools.append("Flyway")
        if liquibase_files:
            migration_tools.append("Liquibase")
        
        if migration_tools:
            result += f"Herramientas de migración detectadas: {', '.join(migration_tools)}\n"
        
        # Buscar configuraciones de base de datos
        config_files = []
        config_files.extend(self.find_files(project_path, "application.properties"))
        config_files.extend(self.find_files(project_path, "application.yml"))
        config_files.extend(self.find_files(project_path, "application.yaml"))
        
        db_configs = []
        for config_file in config_files:
            try:
                if config_file.endswith('.properties'):
                    with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        db_lines = [line for line in content.split('\n') if any(keyword in line for keyword in 
                                 ['datasource', 'jpa', 'hibernate', 'database', 'jdbc'])]
                        db_configs.extend(db_lines)
                
                elif config_file.endswith('.yml') or config_file.endswith('.yaml'):
                    with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        db_lines = [line for line in content.split('\n') if any(keyword in line for keyword in 
                                 ['datasource', 'jpa', 'hibernate', 'database', 'jdbc'])]
                        db_configs.extend(db_lines)
            
            except Exception as e:
                result += f"Error al analizar configuraciones de base de datos: {str(e)}\n"
        
        if db_configs:
            result += "Configuraciones de base de datos:\n"
            for config in db_configs[:10]:  # Mostrar solo las primeras 10
                result += f"  - {config}\n"
        
        result += "\n"
        return result

    def analyze_tests(self, project_path):
        result = "=== PRUEBAS Y CALIDAD ===\n\n"
        
        # Buscar directorios de pruebas
        test_dirs = []
        for root, dirs, files in os.walk(project_path):
            if ('test' in root.lower() and 'java' in root.lower()) or ('src/test' in root):
                test_dirs.append(root)
        
        if not test_dirs:
            result += "No se encontraron directorios de pruebas.\n"
            return result
        
        # Contar archivos de prueba
        test_files = []
        for test_dir in test_dirs:
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    if file.endswith('.java'):
                        test_files.append(os.path.join(root, file))
        
        result += f"Se encontraron {len(test_files)} archivos de prueba.\n\n"
        
        # Analizar tipos de pruebas
        test_types = {"Unit": 0, "Integration": 0, "Other": 0}
        for test_file in test_files:
            filename = os.path.basename(test_file)
            if 'Test.java' in filename and 'IT' not in filename and 'Integration' not in filename:
                test_types["Unit"] += 1
            elif 'IT.java' in filename or 'IntegrationTest.java' in filename:
                test_types["Integration"] += 1
            else:
                test_types["Other"] += 1
        
        result += "Distribución de pruebas:\n"
        for test_type, count in test_types.items():
            if count > 0:
                percentage = (count / len(test_files)) * 100
                result += f"  - {test_type}: {count} archivos ({percentage:.1f}%)\n"
        
        # Buscar herramientas de testing
        build_files = []
        build_files.extend(self.find_files(project_path, "pom.xml"))
        build_files.extend(self.find_files(project_path, "build.gradle"))
        
        testing_tools = set()
        for build_file in build_files:
            try:
                if build_file.endswith('pom.xml'):
                    tree = ET.parse(build_file)
                    root = tree.getroot()
                    
                    # Namespace para XML
                    ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}
                    
                    # Buscar dependencias de testing
                    dependencies = root.findall('.//maven:dependency', namespaces=ns) or root.findall('.//dependency')
                    for dep in dependencies:
                        dep_group = dep.findtext('maven:groupId', namespaces=ns) or dep.findtext('groupId')
                        dep_artifact = dep.findtext('maven:artifactId', namespaces=ns) or dep.findtext('artifactId')
                        
                        if any(keyword in dep_artifact.lower() for keyword in ['junit', 'mockito', 'testcontainers', 'assertj', 'hamcrest']):
                            testing_tools.add(dep_artifact)
                
                elif build_file.endswith('build.gradle'):
                    with open(build_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Buscar dependencias de testing
                        if 'junit' in content.lower():
                            testing_tools.add("JUnit")
                        if 'mockito' in content.lower():
                            testing_tools.add("Mockito")
                        if 'testcontainers' in content.lower():
                            testing_tools.add("Testcontainers")
                        if 'assertj' in content.lower():
                            testing_tools.add("AssertJ")
                        if 'hamcrest' in content.lower():
                            testing_tools.add("Hamcrest")
            
            except Exception as e:
                result += f"Error al analizar herramientas de testing: {str(e)}\n"
        
        if testing_tools:
            result += f"\nHerramientas de testing detectadas: {', '.join(sorted(testing_tools))}\n"
        
        # Buscar configuraciones de calidad de código
        quality_tools = []
        if self.find_files(project_path, "sonar"):
            quality_tools.append("SonarQube")
        if self.find_files(project_path, "checkstyle"):
            quality_tools.append("Checkstyle")
        if self.find_files(project_path, "pmd"):
            quality_tools.append("PMD")
        if self.find_files(project_path, "spotbugs"):
            quality_tools.append("SpotBugs")
        if self.find_files(project_path, "jacoco"):
            quality_tools.append("JaCoCo")
        
        if quality_tools:
            result += f"Herramientas de calidad de código detectadas: {', '.join(quality_tools)}\n"
        
        # Evaluar cobertura de pruebas (heurística simple)
        if test_files:
            # Buscar clases principales
            main_java_files = []
            for java_dir in self.find_java_directories(project_path):
                for root, dirs, files in os.walk(java_dir):
                    for file in files:
                        if file.endswith('.java'):
                            main_java_files.append(os.path.join(root, file))
            
            if main_java_files:
                coverage_ratio = len(test_files) / len(main_java_files)
                result += f"\nRatio pruebas/clases: {coverage_ratio:.2f} "
                if coverage_ratio >= 1.0:
                    result += "(Excelente cobertura)\n"
                elif coverage_ratio >= 0.5:
                    result += "(Buena cobertura)\n"
                else:
                    result += "(Cobertura baja)\n"
        
        result += "\n"
        return result

    def analyze_devops(self, project_path):
        result = "=== OBSERVABILIDAD Y DEVOPS ===\n\n"
        
        # Buscar configuraciones de logging
        logging_configs = []
        logging_configs.extend(self.find_files(project_path, "logback.xml"))
        logging_configs.extend(self.find_files(project_path, "logback-spring.xml"))
        logging_configs.extend(self.find_files(project_path, "log4j"))
        logging_configs.extend(self.find_files(project_path, "logging"))
        
        if logging_configs:
            result += "Configuraciones de logging detectadas:\n"
            for config in logging_configs:
                result += f"  - {os.path.basename(config)}\n"
            result += "\n"
        
        # Buscar configuraciones de métricas y trazabilidad
        monitoring_tools = []
        if self.find_files(project_path, "prometheus"):
            monitoring_tools.append("Prometheus")
        if self.find_files(project_path, "grafana"):
            monitoring_tools.append("Grafana")
        if self.find_files(project_path, "elk"):
            monitoring_tools.append("ELK")
        if self.find_files(project_path, "zipkin"):
            monitoring_tools.append("Zipkin")
        if self.find_files(project_path, "sleuth"):
            monitoring_tools.append("Sleuth")
        if self.find_files(project_path, "actuator"):
            monitoring_tools.append("Spring Boot Actuator")
        
        if monitoring_tools:
            result += f"Herramientas de monitoreo detectadas: {', '.join(monitoring_tools)}\n"
        
        # Buscar configuraciones CI/CD
        ci_cd_files = []
        ci_cd_files.extend(self.find_files(project_path, "jenkins"))
        ci_cd_files.extend(self.find_files(project_path, "github"))
        ci_cd_files.extend(self.find_files(project_path, "gitlab"))
        ci_cd_files.extend(self.find_files(project_path, "azure-pipelines"))
        ci_cd_files.extend(self.find_files(project_path, ".github"))
        ci_cd_files.extend(self.find_files(project_path, ".gitlab"))
        ci_cd_files.extend(self.find_files(project_path, ".jenkins"))
        ci_cd_files.extend(self.find_files(project_path, "Jenkinsfile"))
        ci_cd_files.extend(self.find_files(project_path, "docker-compose"))
        ci_cd_files.extend(self.find_files(project_path, "Dockerfile"))
        ci_cd_files.extend(self.find_files(project_path, "kubernetes"))
        ci_cd_files.extend(self.find_files(project_path, "k8s"))
        
        if ci_cd_files:
            result += "\nConfiguraciones CI/CD detectadas:\n"
            for file in ci_cd_files[:10]:  # Mostrar solo las primeras 10
                result += f"  - {os.path.basename(file)}\n"
        
        # Buscar configuraciones de despliegue en propiedades
        config_files = []
        config_files.extend(self.find_files(project_path, "application.properties"))
        config_files.extend(self.find_files(project_path, "application.yml"))
        config_files.extend(self.find_files(project_path, "application.yaml"))
        
        devops_properties = []
        for config_file in config_files:
            try:
                if config_file.endswith('.properties'):
                    with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        devops_lines = [line for line in content.split('\n') if any(keyword in line for keyword in 
                                 ['cloud', 'kubernetes', 'k8s', 'docker', 'actuator', 'management', 'metrics'])]
                        devops_properties.extend(devops_lines)
                
                elif config_file.endswith('.yml') or config_file.endswith('.yaml'):
                    with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        devops_lines = [line for line in content.split('\n') if any(keyword in line for keyword in 
                                 ['cloud', 'kubernetes', 'k8s', 'docker', 'actuator', 'management', 'metrics'])]
                        devops_properties.extend(devops_lines)
            
            except Exception as e:
                result += f"Error al analizar configuraciones DevOps: {str(e)}\n"
        
        if devops_properties:
            result += "\nConfiguraciones DevOps en propiedades:\n"
            for prop in devops_properties[:10]:  # Mostrar solo las primeras 10
                result += f"  - {prop}\n"
        
        result += "\n"
        return result

    def compare_with_monolith(self, analysis_results):
        result = "=== COMPARACIÓN CON ARQUITECTURA MONOLÍTICA ===\n\n"
        
        # Determinar si es microservicio o monolito
        is_microservices = "Microservicios" in analysis_results.get("contexto_general", "")
        
        if is_microservices:
            result += "El proyecto sigue una arquitectura de microservicios.\n\n"
            result += "✅ Ventajas respecto a un monolito:\n"
            result += "  - Mejor escalabilidad horizontal por servicio\n"
            result += "  - Mayor independencia en el desarrollo y despliegue\n"
            result += "  - Tecnologías específicas por dominio\n"
            result += "  - Mayor tolerancia a fallos\n"
            result += "  - Equipos más autónomos y especializados\n\n"
            result += "⚠️ Desafíos:\n"
            result += "  - Mayor complejidad en la operación\n"
            result += "  - Necesidad de orquestación (Kubernetes, Docker Compose)\n"
            result += "  - Comunicación entre servicios más compleja\n"
            result += "  - Mayor overhead en transacciones distribuidas\n"
            result += "  - Mayor consumo de recursos\n"
            result += "  - Dificultad para debugging distribuido\n\n"
            result += "🔧 Recomendaciones para microservicios:\n"
            result += "  - Implementar API Gateway para un punto único de entrada\n"
            result += "  - Usar service discovery (Eureka, Consul)\n"
            result += "  - Implementar circuit breakers (Resilience4j, Hystrix)\n"
            result += "  - Centralizar la configuración (Spring Cloud Config)\n"
            result += "  - Implementar trazabilidad distribuida (Zipkin, Sleuth)\n"
        else:
            result += "El proyecto sigue una arquitectura monolítica.\n\n"
            result += "✅ Ventajas respecto a microservicios:\n"
            result += "  - Menor complejidad operativa\n"
            result += "  - Desarrollo y testing más sencillos\n"
            result += "  - Transacciones ACID más fáciles de implementar\n"
            result += "  - Menor overhead de comunicación\n"
            result += "  - Debugging más simple\n"
            result += "  - Menor consumo de recursos\n\n"
            result += "⚠️ Desafíos:\n"
            result += "  - Escalabilidad limitada\n"
            result += "  - Acoplamiento más fuerte entre componentes\n"
            result += "  - Dificultad para adoptar tecnologías heterogéneas\n"
            result += "  - Despliegues más riesgosos\n"
            result += "  - Equipos menos autónomos\n\n"
            result += "🔧 Recomendaciones para monolitos:\n"
            result += "  - Modularizar el código siguiendo DDD y bounded contexts\n"
            result += "  - Implementar módulos bien definidos con interfaces claras\n"
            result += "  - Usar arquitectura hexagonal para desacoplar la lógica de negocio\n"
            result += "  - Considerar la migración gradual a microservicios si es necesario\n"
            result += "  - Implementar pruebas automatizadas robustas\n"
        
        result += "\n"
        return result

    def display_results(self, analysis_results):
        self.output_area.delete(1.0, tk.END)
        
        for section, content in analysis_results.items():
            self.output_area.insert(tk.END, content)
            self.output_area.insert(tk.END, "\n")
        
        # Añadir resumen y recomendaciones finales
        self.output_area.insert(tk.END, "=== RESUMEN Y RECOMENDACIONES FINALES ===\n\n")
        
        # Generar recomendaciones basadas en el análisis
        recommendations = self.generate_recommendations(analysis_results)
        for rec in recommendations:
            self.output_area.insert(tk.END, f"• {rec}\n")
        
        self.output_area.insert(tk.END, "\n=== ANÁLISIS COMPLETADO ===\n")
        self.output_area.insert(tk.END, "Revise los resultados arriba y genere un reporte si es necesario.\n")
    
    def generate_recommendations(self, analysis_results):
        recommendations = []
        
        # Recomendaciones basadas en la arquitectura
        if "Microservicios" in analysis_results.get("contexto_general", ""):
            recommendations.append("Considerar implementar un API Gateway para unificar el acceso a los microservicios.")
            recommendations.append("Evaluar el uso de service discovery (Eureka, Consul) para la localización de servicios.")
            recommendations.append("Implementar circuit breakers (Resilience4j) para mejorar la tolerancia a fallos.")
        else:
            recommendations.append("Considerar modularizar la aplicación siguiendo principios de Domain-Driven Design.")
            recommendations.append("Evaluar la separación en módulos independientes para facilitar una futura migración a microservicios.")
        
        # Recomendaciones de seguridad
        seguridad_content = analysis_results.get("seguridad", "")
        if "CSRF: Deshabilitado" in seguridad_content:
            recommendations.append("Revisar la configuración de CSRF. No deshabilitar sin una justificación de seguridad adecuada.")
        if not any(keyword in seguridad_content for keyword in ["JWT", "OAuth2", "Spring Security"]):
            recommendations.append("Considerar implementar Spring Security para proteger los endpoints de la aplicación.")
        
        # Recomendaciones de pruebas
        pruebas_content = analysis_results.get("pruebas", "")
        if "Cobertura baja" in pruebas_content:
            recommendations.append("Aumentar la cobertura de pruebas, especialmente para la lógica de negocio crítica.")
        if "Testcontainers" not in pruebas_content and "Microservicios" in analysis_results.get("contexto_general", ""):
            recommendations.append("Considerar usar Testcontainers para pruebas de integración con bases de datos reales.")
        
        # Recomendaciones de DevOps
        devops_content = analysis_results.get("devops", "")
        if "Spring Boot Actuator" not in devops_content:
            recommendations.append("Implementar Spring Boot Actuator para monitorización y gestión de la aplicación.")
        if not any(keyword in devops_content for keyword in ["Prometheus", "Grafana"]):
            recommendations.append("Considerar implementar métricas con Prometheus y dashboards con Grafana.")
        
        # Recomendaciones de persistencia
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
    
    # Métodos utilitarios
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
        # Heurística mejorada para detectar microservicios
        # 1. Buscar múltiples módulos en Maven/Gradle
        # 2. Buscar múltiples aplicaciones Spring Boot
        # 3. Buscar configuraciones de Docker/Kubernetes para múltiples servicios
        
        # Verificar si es un proyecto multi-módulo de Maven
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
        
        # Verificar si hay múltiples archivos de aplicación
        app_files = self.find_files(project_path, "Application.java")
        if len(app_files) > 1:
            return True
        
        # Verificar configuraciones de Docker/Kubernetes para múltiples servicios
        docker_files = self.find_files(project_path, "Dockerfile")
        if len(docker_files) > 1:
            return True
        
        k8s_files = self.find_files(project_path, "deployment.yaml")
        k8s_files.extend(self.find_files(project_path, "deployment.yml"))
        k8s_files.extend(self.find_files(project_path, "service.yaml"))
        k8s_files.extend(self.find_files(project_path, "service.yml"))
        
        if len(k8s_files) > 1:
            return True
        
        # Buscar indicadores de Spring Cloud
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

def main():
    root = tk.Tk()
    app = SpringBootAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
