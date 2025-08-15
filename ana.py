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
# New import for deep class inspection
from javaclass.parser import JavaClassParser

# --- Core Analysis Logic (to be run in a separate thread) ---

# Namespace mapping for parsing XML descriptors
NS = {
    'javaee': 'http://java.sun.com/xml/ns/javaee',
    'j2ee': 'http://java.sun.com/xml/ns/j2ee'
}

# Regex to find potential JNDI lookup strings in binary .class files
JNDI_REGEX = re.compile(rb'(java:global|java:comp/env|ejb/)[a-zA-Z0-9/._-]+')

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
    
def inspect_class_methods(class_file_bytes):
    """
    Parses a .class file's binary content and returns a list of its method names.
    """
    methods = []
    try:
        java_class = JavaClassParser(class_file_bytes)
        parsed_methods = java_class.get_methods()
        # Filter out compiler-generated methods for clarity
        methods = sorted([m.name for m in parsed_methods if m.name not in ["<init>", "<clinit>"]])
    except Exception:
        # Ignore files that aren't valid class files
        return []
    return methods

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
        
        for ref in find_all(root, ['ns:ejb-ref', 'ns:ejb-local-ref']):
            ref_name = find_first(ref, ['ns:ejb-ref-name'])
            ejb_link = find_first(ref, ['ns:ejb-link'])
            if ref_name is not None:
                web_info['ejb_refs'][ref_name.text.strip()] = ejb_link.text.strip() if ejb_link is not None else 'Unknown'
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

def process_archive_module(archive_path):
    """
    Processes a single archive (WAR or JAR) to find JNDI lookups and class methods.
    Returns two dictionaries: one for JNDI lookups and one for class methods.
    """
    jndi_lookups = {}
    class_methods = {}
    if not zipfile.is_zipfile(archive_path):
        return jndi_lookups, class_methods
        
    with zipfile.ZipFile(archive_path, 'r') as zf:
        for file_info in zf.infolist():
            if file_info.filename.endswith('.class'):
                class_name = file_info.filename.replace('/', '.').replace('.class', '')
                try:
                    with zf.open(file_info.filename) as class_file:
                        content = class_file.read()
                        
                        # Find JNDI strings
                        matches = JNDI_REGEX.findall(content)
                        if matches:
                            decoded_matches = sorted(list(set([m.decode('utf-8', 'ignore') for m in matches])))
                            jndi_lookups[class_name] = decoded_matches
                        
                        # Find methods
                        methods = inspect_class_methods(content)
                        if methods:
                            class_methods[class_name] = methods
                except Exception:
                    continue
    return jndi_lookups, class_methods

def perform_analysis(ear_path):
    report = []
    ear_name = Path(ear_path).name
    report.append(f"Legacy Application Analysis Report: {ear_name}")
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
                    header = "Web Modules (WARs)" if module_type == 'web' else "Business Logic Modules (EJB JARs)"
                    report.append(f"\n\n## {header} - Deep Inspection ##")
                    for module_name in module_list:
                        report.append(f"\n--- MODULE: {module_name} ---")
                        module_path = Path(temp_dir) / module_name
                        if not module_path.exists():
                            report.append("  Module file not found.")
                            continue

                        # Process XML descriptors first
                        if module_type == 'web':
                            try:
                                with zipfile.ZipFile(module_path, 'r') as war_zip:
                                    web_xml = war_zip.read('WEB-INF/web.xml')
                                    web_info = analyze_web_xml(web_xml)
                                    if web_info['servlets']:
                                        report.append("\n  [XML] Declared Entrypoints (URL -> Class):")
                                        for url, s_class in sorted(web_info['servlets'].items()):
                                            report.append(f"    - {url:<30} -> {s_class}")
                            except (KeyError, FileNotFoundError):
                                report.append("\n  [XML] WEB-INF/web.xml not found or failed to parse.")
                        else: # ejb
                             try:
                                with zipfile.ZipFile(module_path, 'r') as ejb_zip:
                                    ejb_xml = ejb_zip.read('META-INF/ejb-jar.xml')
                                    ejb_info = analyze_ejb_jar_xml(ejb_xml)
                                    if ejb_info['session']: report.append(f"\n  [XML] Session Beans: {', '.join(sorted(ejb_info['session']))}")
                             except (KeyError, FileNotFoundError):
                                report.append("\n  [XML] META-INF/ejb-jar.xml not found or failed to parse.")
                        
                        # Deep inspection of bytecode
                        jndi_lookups, class_methods = process_archive_module(module_path)
                        
                        if jndi_lookups:
                            report.append("\n  [BYTECODE] Potential JNDI Lookups:")
                            for c, lookups in sorted(jndi_lookups.items()):
                                report.append(f"    - In Class: {c}")
                                report.append(f"      Found: {', '.join(lookups)}")
                        
                        if class_methods:
                            report.append("\n  [BYTECODE] Class and Method Inspection:")
                            for c, methods in sorted(class_methods.items()):
                                report.append(f"    - CLASS: {c}")
                                methods_str = ", ".join(methods)
                                report.append(f"      METHODS: {methods_str}")

        except Exception as e:
            return f"An error occurred during analysis: {e}"

    return "\n".join(report)


# --- Tkinter GUI Application Class (No changes needed here) ---

class EarAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Legacy EAR Analyzer v2 (with Method Inspection)")
        self.root.geometry("900x700")
        self.ear_path = None
        self.q = queue.Queue()
        top_frame = tk.Frame(root, padx=10, pady=10)
        top_frame.pack(fill=tk.X)
        self.select_button = tk.Button(top_frame, text="Select EAR File", command=self.select_ear)
        self.select_button.pack(side=tk.LEFT)
        self.run_button = tk.Button(top_frame, text="Run Full Analysis", command=self.run_analysis, state=tk.DISABLED)
        self.run_button.pack(side=tk.LEFT, padx=10)
        self.status_label = tk.Label(top_frame, text="Please select an EAR file to begin.")
        self.status_label.pack(side=tk.LEFT)
        self.report_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier New", 10))
        self.report_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

    def select_ear(self):
        path = filedialog.askopenfilename(title="Select an EAR file", filetypes=(("Enterprise Archive", "*.ear"), ("All files", "*.*")))
        if path:
            self.ear_path = path
            self.status_label.config(text=f"Selected: {Path(self.ear_path).name}")
            self.run_button.config(state=tk.NORMAL)
            self.report_text.delete('1.0', tk.END)

    def run_analysis(self):
        if not self.ear_path:
            messagebox.showerror("Error", "No EAR file selected.")
            return
        self.run_button.config(state=tk.DISABLED); self.select_button.config(state=tk.DISABLED)
        self.status_label.config(text="Analyzing... this may take some time depending on file size.")
        self.report_text.delete('1.0', tk.END)
        self.thread = threading.Thread(target=self.worker, args=(self.ear_path,))
        self.thread.start()
        self.root.after(100, self.check_queue)

    def worker(self, ear_path):
        report_content = perform_analysis(ear_path)
        self.q.put(report_content)

    def check_queue(self):
        try:
            result = self.q.get_nowait()
            self.report_text.insert(tk.END, result)
            self.status_label.config(text="Analysis complete.")
            self.run_button.config(state=tk.NORMAL)
            self.select_button.config(state=tk.NORMAL)
        except queue.Empty:
            self.root.after(100, self.check_queue)

if __name__ == '__main__':
    main_window = tk.Tk()
    app = EarAnalyzerApp(main_window)
    main_window.mainloop()
