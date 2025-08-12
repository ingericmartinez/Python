import os
import zipfile
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

class EARAnalyzer:
    def __init__(self, ear_path: str, output_dir: str = "output"):
        self.ear_path = ear_path
        self.output_dir = output_dir
        self.temp_dir = os.path.join(output_dir, "temp")
        self.plantuml_jar = "plantuml.jar"  # Asume que PlantUML está en el mismo directorio
        self.cfr_jar = "cfr.jar"  # Decompilador CFR
        
        # Configuración de directorios
        Path(self.output_dir).mkdir(exist_ok=True)
        Path(self.temp_dir).mkdir(exist_ok=True)
        
        # Diccionarios para almacenar la información
        self.ejbs = {}
        self.controllers = {}
        self.services = {}
        self.flows = []

    def extract_ear(self):
        """Extrae el contenido del archivo EAR"""
        print(f"Extrayendo {self.ear_path}...")
        with zipfile.ZipFile(self.ear_path, 'r') as ear_zip:
            ear_zip.extractall(self.temp_dir)
        print("Extracción completada.")

    def find_jar_files(self, dir_path: str) -> List[str]:
        """Encuentra todos los archivos JAR en un directorio"""
        jar_files = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.jar'):
                    jar_files.append(os.path.join(root, file))
        return jar_files

    def decompile_jar(self, jar_path: str, output_dir: str):
        """Descompila un JAR usando CFR"""
        if not os.path.exists(self.cfr_jar):
            print(f"Error: No se encontró {self.cfr_jar}. Descárgalo de http://www.benf.org/other/cfr/")
            return
        
        cmd = [
            'java', '-jar', self.cfr_jar,
            jar_path,
            '--outputdir', output_dir,
            '--silent'
        ]
        try:
            subprocess.run(cmd, check=True)
            print(f"Descompilación completada para {os.path.basename(jar_path)}")
        except subprocess.CalledProcessError as e:
            print(f"Error al descompilar {jar_path}: {e}")

    def analyze_java_files(self, dir_path: str):
        """Analiza archivos Java para identificar componentes clave"""
        print(f"Analizando archivos Java en {dir_path}...")
        
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(root, file)
                    self.analyze_java_file(file_path)

    def analyze_java_file(self, file_path: str):
        """Analiza un archivo Java individual"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Identificar EJBs
            if '@Stateless' in content or '@Stateful' in content or '@MessageDriven' in content:
                class_name = self.extract_class_name(content)
                methods = self.extract_methods(content)
                self.ejbs[class_name] = {
                    'file': file_path,
                    'methods': methods
                }
            
            # Identificar Controladores (Spring MVC, JAX-RS, etc.)
            elif '@Controller' in content or '@RestController' in content or '@Path' in content:
                class_name = self.extract_class_name(content)
                methods = self.extract_methods(content)
                self.controllers[class_name] = {
                    'file': file_path,
                    'methods': methods
                }
            
            # Identificar Servicios (Spring Service, etc.)
            elif '@Service' in content:
                class_name = self.extract_class_name(content)
                methods = self.extract_methods(content)
                self.services[class_name] = {
                    'file': file_path,
                    'methods': methods
                }

    def extract_class_name(self, content: str) -> Optional[str]:
        """Extrae el nombre de la clase del contenido Java"""
        match = re.search(r'class\s+([^\s{]+)', content)
        return match.group(1) if match else None

    def extract_methods(self, content: str) -> List[Dict]:
        """Extrae información de métodos de una clase Java"""
        methods = []
        # Expresión regular para capturar métodos públicos (simplificado)
        pattern = re.compile(r'public\s+([^\s(]+)\s+([^\s(]+)\s*\(([^)]*)\)\s*[^{]*\{')
        
        for match in pattern.finditer(content):
            return_type = match.group(1)
            method_name = match.group(2)
            params = match.group(3)
            methods.append({
                'name': method_name,
                'return_type': return_type,
                'parameters': params
            })
        
        return methods

    def trace_flows(self):
        """Rastrea los flujos entre componentes"""
        print("Trazando flujos de negocio...")
        
        # Buscar llamadas desde controladores a servicios/EJBs
        for ctrl_name, ctrl_data in self.controllers.items():
            for method in ctrl_data['methods']:
                flow = {
                    'start': f"{ctrl_name}.{method['name']}",
                    'steps': []
                }
                
                # Buscar llamadas a servicios/EJBs en el cuerpo del método (simplificado)
                method_file = ctrl_data['file']
                method_content = self.get_method_content(method_file, method['name'])
                
                if method_content:
                    # Buscar referencias a servicios/EJBs
                    for service_name in self.services:
                        if service_name in method_content:
                            flow['steps'].append(service_name)
                    
                    for ejb_name in self.ejbs:
                        if ejb_name in method_content:
                            flow['steps'].append(ejb_name)
                    
                    if flow['steps']:
                        self.flows.append(flow)

    def get_method_content(self, file_path: str, method_name: str) -> Optional[str]:
        """Obtiene el contenido de un método específico (implementación simplificada)"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Buscar el método por su firma (simplificado)
                pattern = re.compile(rf'public\s+[^\s]+\s+{method_name}\s*\([^)]*\)\s*{{([^}}]+)}}')
                match = pattern.search(content)
                return match.group(1) if match else None
        except Exception as e:
            print(f"Error al leer {file_path}: {e}")
            return None

    def generate_plantuml_diagrams(self):
        """Genera diagramas de secuencia PlantUML para los flujos encontrados"""
        print("Generando diagramas PlantUML...")
        
        for i, flow in enumerate(self.flows):
            puml_content = self.create_sequence_diagram(flow)
            puml_file = os.path.join(self.output_dir, f"flow_{i+1}.puml")
            
            with open(puml_file, 'w') as f:
                f.write(puml_content)
            
            # Generar imagen del diagrama si PlantUML está disponible
            if os.path.exists(self.plantuml_jar):
                self.generate_plantuml_image(puml_file)

    def create_sequence_diagram(self, flow: Dict) -> str:
        """Crea contenido PlantUML para un diagrama de secuencia"""
        lines = [
            "@startuml",
            "title Flujo de Negocio: " + flow['start'],
            "actor Usuario as user",
            "participant \"" + flow['start'].split('.')[0] + "\" as controller"
        ]
        
        # Agregar participantes
        participants = set()
        for step in flow['steps']:
            participants.add(step)
        
        for participant in participants:
            lines.append(f'participant "{participant}" as {participant.replace(".", "_")}')
        
        # Agregar mensajes
        lines.append("\nuser -> controller : " + flow['start'].split('.')[1] + "()")
        
        last_participant = "controller"
        for step in flow['steps']:
            step_id = step.replace(".", "_")
            lines.append(f"{last_participant} -> {step_id} : método()")
            last_participant = step_id
        
        lines.append("@enduml")
        return '\n'.join(lines)

    def generate_plantuml_image(self, puml_file: str):
        """Genera una imagen a partir del archivo PlantUML"""
        cmd = [
            'java', '-jar', self.plantuml_jar,
            puml_file,
            '-output', self.output_dir
        ]
        try:
            subprocess.run(cmd, check=True)
            print(f"Diagrama generado para {os.path.basename(puml_file)}")
        except subprocess.CalledProcessError as e:
            print(f"Error al generar diagrama: {e}")

    def analyze(self):
        """Ejecuta el análisis completo"""
        self.extract_ear()
        
        # Descompilar todos los JARs encontrados
        jar_files = self.find_jar_files(self.temp_dir)
        for jar in jar_files:
            jar_name = os.path.basename(jar)
            output_dir = os.path.join(self.temp_dir, f"decompiled_{jar_name}")
            Path(output_dir).mkdir(exist_ok=True)
            self.decompile_jar(jar, output_dir)
            self.analyze_java_files(output_dir)
        
        # Analizar flujos y generar diagramas
        self.trace_flows()
        self.generate_plantuml_diagrams()
        
        print(f"Análisis completado. Resultados en {self.output_dir}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Analiza un EAR para extraer flujos de negocio y generar diagramas.')
    parser.add_argument('ear_file', help='Ruta al archivo EAR a analizar')
    parser.add_argument('--output', help='Directorio de salida', default='output')
    
    args = parser.parse_args()
    
    analyzer = EARAnalyzer(args.ear_file, args.output)
    analyzer.analyze()
