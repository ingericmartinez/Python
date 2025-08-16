import tkinter as tk
from tkinter import filedialog, scrolledtext
import os

# --- Lógica de Análisis ---

def check_dependencies(project_path):
    """Revisa los archivos de build en busca de dependencias clave de OAuth2."""
    results = {
        "client_dependency": False,
        "resource_server_dependency": False,
        "build_file_found": None
    }
    
    # Buscar pom.xml para Maven
    pom_path = os.path.join(project_path, 'pom.xml')
    if os.path.exists(pom_path):
        results["build_file_found"] = "pom.xml"
        with open(pom_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'spring-boot-starter-oauth2-client' in content:
                results["client_dependency"] = True
            if 'spring-boot-starter-oauth2-resource-server' in content:
                results["resource_server_dependency"] = True
        return results

    # Buscar build.gradle o build.gradle.kts para Gradle
    for gradle_file in ['build.gradle', 'build.gradle.kts']:
        gradle_path = os.path.join(project_path, gradle_file)
        if os.path.exists(gradle_path):
            results["build_file_found"] = gradle_file
            with open(gradle_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'spring-boot-starter-oauth2-client' in content:
                    results["client_dependency"] = True
                if 'spring-boot-starter-oauth2-resource-server' in content:
                    results["resource_server_dependency"] = True
            return results
            
    return results

def check_security_config(project_path):
    """Revisa los archivos .java y .kt en busca de configuraciones de seguridad."""
    results = {
        "has_oauth2login": False,
        "has_resourceserver": False,
        "config_files_found": []
    }
    
    src_path = os.path.join(project_path, 'src', 'main')
    if not os.path.exists(src_path):
        return results

    for root, _, files in os.walk(src_path):
        for file in files:
            if file.endswith('.java') or file.endswith('.kt'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Buscar las configuraciones clave en clases de seguridad
                        if '@EnableWebSecurity' in content or '@Configuration' in content:
                            if '.oauth2Login()' in content:
                                results["has_oauth2login"] = True
                                results["config_files_found"].append(file)
                            if '.oauth2ResourceServer()' in content:
                                results["has_resourceserver"] = True
                                if file not in results["config_files_found"]:
                                    results["config_files_found"].append(file)
                except Exception as e:
                    print(f"No se pudo leer el archivo {file_path}: {e}")

    return results

# --- Interfaz Gráfica (GUI) ---

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Proyectos Spring Boot - Okta/OAuth2")
        self.root.geometry("700x600")

        # Frame principal
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Botón para seleccionar directorio
        btn_select_dir = tk.Button(main_frame, text="Seleccionar Directorio del Proyecto", command=self.run_analysis)
        btn_select_dir.pack(pady=10, fill=tk.X)

        # Etiqueta para mostrar la ruta seleccionada
        self.selected_dir_label = tk.Label(main_frame, text="Ningún directorio seleccionado", fg="blue")
        self.selected_dir_label.pack(pady=5)

        # Área de texto para mostrar los resultados
        self.results_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, state='disabled', font=("Courier New", 10))
        self.results_text.pack(pady=10, fill=tk.BOTH, expand=True)

    def run_analysis(self):
        project_path = filedialog.askdirectory()
        if not project_path:
            return # El usuario canceló la selección

        self.selected_dir_label.config(text=f"Analizando: {project_path}")
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)

        # Ejecutar análisis
        dep_results = check_dependencies(project_path)
        config_results = check_security_config(project_path)

        # Determinar el modo principal
        is_client = dep_results["client_dependency"] or config_results["has_oauth2login"]
        is_resource_server = dep_results["resource_server_dependency"] or config_results["has_resourceserver"]
        
        mode = "Indeterminado"
        if is_client and not is_resource_server:
            mode = "Iniciador de Login (Cliente OIDC)"
        elif is_resource_server and not is_client:
            mode = "Validador de Token (Servidor de Recursos)"
        elif is_client and is_resource_server:
            mode = "Híbrido (Cliente y Servidor de Recursos)"
        
        # --- Generar Reporte ---
        report = []
        report.append("--- REPORTE DE ANÁLISIS DE CONFIGURACIÓN OAUTH2/OIDC ---")
        report.append(f"\nMODO DE OPERACIÓN PROBABLE: {mode}\n")
        report.append("="*50)
        
        # Checklist de Dependencias
        report.append("\nCHECKLIST DE DEPENDENCIAS:")
        if dep_results["build_file_found"]:
            report.append(f"Archivo de build encontrado: {dep_results['build_file_found']}")
            
            icon_client = "✔️" if dep_results["client_dependency"] else "❌"
            report.append(f"  [{icon_client}] Dependencia 'oauth2-client' encontrada.")
            
            icon_rs = "✔️" if dep_results["resource_server_dependency"] else "❌"
            report.append(f"  [{icon_rs}] Dependencia 'oauth2-resource-server' encontrada.")
        else:
            report.append("  [❌] No se encontró pom.xml ni build.gradle.")

        # Checklist de Configuración en Código
        report.append("\nCHECKLIST DE CONFIGURACIÓN EN CÓDIGO:")
        icon_login = "✔️" if config_results["has_oauth2login"] else "❌"
        report.append(f"  [{icon_login}] Configuración '.oauth2Login()' encontrada.")

        icon_token = "✔️" if config_results["has_resourceserver"] else "❌"
        report.append(f"  [{icon_token}] Configuración '.oauth2ResourceServer()' encontrada.")
        
        if config_results["config_files_found"]:
            report.append("\n  Archivos de configuración analizados:")
            for f in set(config_results["config_files_found"]):
                report.append(f"    - {os.path.basename(f)}")

        # Conclusión y Recomendación
        report.append("\n" + "="*50)
        report.append("\nCONCLUSIÓN:")
        if mode == "Iniciador de Login (Cliente OIDC)":
            report.append("  [APROBADO ✔️] La aplicación está configurada para iniciar un flujo de login.")
            report.append("  Debe redirigir a un proveedor de identidad como Okta cuando un usuario")
            report.append("  intenta acceder a una ruta protegida.")
        elif mode == "Validador de Token (Servidor de Recursos)":
            report.append("  [APROBADO ✔️] La aplicación está configurada como una API protegida.")
            report.append("  No iniciará un login, sino que esperará un Access Token (Bearer Token)")
            report.append("  en las cabeceras de las peticiones para autorizar el acceso.")
        elif mode == "Híbrido (Cliente y Servidor de Recursos)":
            report.append("  [PRECAUCIÓN ⚠️] La aplicación tiene configuraciones para ambos modos.")
            report.append("  Esto es válido, pero asegúrate de que sea intencional (ej. una app")
            report.append("  que sirve su propio frontend y a la vez expone una API protegida).")
        else:
            report.append("  [NO APROBADO ❌] No se encontraron configuraciones estándar de OAuth2.")
            report.append("  La aplicación podría no estar protegida con Okta/OAuth2, o usar una")
            report.append("  configuración no convencional que este script no puede detectar.")

        # Escribir el reporte en la GUI
        self.results_text.insert(tk.END, "\n".join(report))
        self.results_text.config(state='disabled')


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

