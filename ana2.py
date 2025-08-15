# gui_ear_analyzer_v3_jdk.py
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
import queue
import os
import zipfile
import xml.etree.ElementTree as ET
import tempfile
import re
from pathlib import Path
import subprocess # Módulo para ejecutar comandos externos como javap

# --- Lógica Principal de Análisis (Modificada para usar javap) ---

# Namespace para parsear descriptores XML
NS = {
    'javaee': 'http://java.sun.com/xml/ns/javaee',
    'j2ee': 'http://java.sun.com/xml/ns/j2ee'
}

# Regex para encontrar JNDI lookups en archivos .class binarios
JNDI_REGEX = re.compile(rb'(java:global|java:comp/env|ejb/)[a-zA-Z0-9/._-]+')

# Regex para extraer nombres de métodos públicos de la salida de javap
METHOD_REGEX = re.compile(r'^\s+(?:public|protected|private)\s+.*\s+([a-zA-Z0-9_$<>]+)\(.*\);')

def find_first(element, paths):
    for path in paths:
        for prefix, uri in NS.items():
            namespaced_path = path.replace('ns:', prefix + ':')
            found = element.find(namespaced_path, NS)
            if found is not None:
                return found
    return None

def find_all(element, paths):
    results = []
    for path in paths:
        for prefix, uri in NS.items():
            namespaced_path = path.replace('ns:', prefix + ':')
            found = element.findall(namespaced_path, NS)
            results.extend(found)
    return results
    
def inspect_methods_with_javap(class_file_path):
    """
    Usa javap para desensamblar un archivo .class y extraer los nombres de sus métodos.
    """
    methods = []
    try:
        # Ejecuta javap en el archivo .class y captura la salida
        result = subprocess.run(
            ['javap', '-public', class_file_path],
            capture_output=True, text=True, check=False, encoding='utf-8', errors='ignore'
        )
        
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                match = METHOD_REGEX.match(line)
                if match:
                    method_name = match.group(1)
                    # Filtra constructores generados por el compilador
                    if method_name not in ["<init>", "<clinit>"]:
                        methods.append(method_name)
    except FileNotFoundError:
        # Esto ocurre si javap no está en el PATH del sistema
        return ["javap_not_found"]
    except Exception:
        # Ignora otros posibles errores
        return []
    return sorted(list(set(methods)))


def analyze_web_xml(xml_content):
    web_info = {'servlets': {}, 'ejb_refs': {}}
    try:
        root = ET.fromstring(xml_content)
        servlet_mappings = {}
        for mapping in find_all(root, ['ns:servlet-mapping']):
            s_name = find_first(mapping, ['ns:servlet-name'])
            url_pattern = find_first(mapping, ['ns:url-pattern'])
            if s_name is not None and url_pattern is not None:
                servlet_mappings[s_name.text.strip()] = url_pattern.text.strip()
        
        for servlet in find_all(root, ['ns:servlet']):
            s_name = find_first(servlet, ['ns:servlet-name'])
            s_class = find_first(servlet, ['ns:servlet-class'])
            if s_name is not None and s_class is not None and s_name.text.strip() in servlet_mappings:
                web_info['servlets'][servlet_mappings[s_name.text.strip()]] = s_class.text.strip()
    except ET.ParseError:
        pass
    return web_info

def analyze_ejb_jar_xml(xml_content):
    ejb_info = {'session': [], 'mdb': [], 'entity': []}
    try:
        root = ET.fromstring(xml_content)
        beans = find_first(root, ['ns:enterprise-beans'])
        if beans:
            for bean_type in ['session', 'message-driven', 'entity']:
                for bean in find_all(beans, [f'ns:{bean_type}']):
                    ejb_name = find_first(bean, ['ns:ejb-name'])
                    if ejb_name is not None:
                        ejb_info[bean_type].append(ejb_name.text.strip())
    except ET.ParseError:
        pass
    return ejb_info

def process_archive_module(archive_path, temp_dir_for_classes):
    jndi_lookups = {}
    class_methods = {}
    
    if not zipfile.is_zipfile(archive_path):
        return jndi_lookups, class_methods
        
    with zipfile.ZipFile(archive_path, 'r') as zf:
        for file_info in zf.infolist():
            if file_info.filename.endswith('.class'):
                class_name = file_info.filename.replace('/', '.').replace('.class', '')
                try:
                    # Extrae el .class a un archivo temporal para que javap pueda leerlo
                    extracted_path = zf.extract(file_info, path=temp_dir_for_classes)
                    
                    # 1. Analiza los métodos usando javap
                    methods = inspect_methods_with_javap(extracted_path)
                    if methods:
                        class_methods[class_name] = methods
                    
                    # 2. Busca JNDI strings en el contenido binario
                    with open(extracted_path, 'rb') as f:
                        content = f.read()
                        matches = JNDI_REGEX.findall(content)
                        if matches:
                            decoded = sorted(list(set([m.decode('utf-8', 'ignore') for m in matches])))
                            jndi_lookups[class_name] = decoded
                except Exception:
                    continue
    return jndi_lookups, class_methods

def perform_analysis(ear_path):
    report = []
    ear_name = Path(ear_path).name
    report.append(f"Análisis de Aplicación Legacy: {ear_name} (Usando javap)")
    report.append("=" * 80)
    
    modules = {'web': [], 'ejb': []}

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            with zipfile.ZipFile(ear_path, 'r') as ear_zip:
                ear_zip.extractall(temp_dir)
                
                app_xml_path = Path(temp_dir) / 'META-INF' / 'application.xml'
                if app_xml_path.exists():
                    root = ET.parse(app_xml_path).getroot()
                    for module in find_all(root, ['ns:module']):
                        web_uri = find_first(module, ['ns:web/ns:web-uri'])
                        ejb_uri = find_first(module, ['ns:ejb'])
                        if web_uri is not None: modules['web'].append(web_uri.text.strip())
                        elif ejb_uri is not None: modules['ejb'].append(ejb_uri.text.strip())

                for module_type, module_list in modules.items():
                    header = "Módulos Web (WARs)" if module_type == 'web' else "Módulos de Lógica (EJB JARs)"
                    report.append(f"\n\n## {header} - Inspección Profunda ##")
                    for module_name in module_list:
                        report.append(f"\n--- MÓDULO: {module_name} ---")
                        module_path = Path(temp_dir) / module_name
                        if not module_path.exists(): continue

                        temp_class_dir = Path(temp_dir) / "classes"
                        os.makedirs(temp_class_dir, exist_ok=True)
                        jndi, methods = process_archive_module(module_path, temp_class_dir)
                        
                        if methods and methods.get(next(iter(methods))) == ["javap_not_found"]:
                            report.append("\n  [ERROR] `javap` no se encontró. Asegúrate de que un JDK esté instalado y en el PATH.")
                            # No continuar si javap falla
                            continue

                        if methods:
                            report.append("\n  [BYTECODE] Inspección de Clases y Métodos (vía javap):")
                            for c, m in sorted(methods.items()):
                                report.append(f"    - CLASE: {c}")
                                report.append(f"      MÉTODOS: {', '.join(m)}")

                        if jndi:
                            report.append("\n  [BYTECODE] Potenciales Lookups JNDI:")
                            for c, l in sorted(jndi.items()):
                                report.append(f"    - En Clase: {c}")
                                report.append(f"      Encontrado: {', '.join(l)}")
        except Exception as e:
            return f"Ocurrió un error durante el análisis: {e}"

    return "\n".join(report)

# --- Clase de la Aplicación GUI con Tkinter (Sin cambios) ---
class EarAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de EAR Legacy v3 (compatible con JDK)")
        self.root.geometry("900x700")
        self.ear_path = None
        self.q = queue.Queue()
        top_frame = tk.Frame(root, padx=10, pady=10)
        top_frame.pack(fill=tk.X)
        self.select_button = tk.Button(top_frame, text="Seleccionar Archivo EAR", command=self.select_ear)
        self.select_button.pack(side=tk.LEFT)
        self.run_button = tk.Button(top_frame, text="Ejecutar Análisis Completo", command=self.run_analysis, state=tk.DISABLED)
        self.run_button.pack(side=tk.LEFT, padx=10)
        self.status_label = tk.Label
