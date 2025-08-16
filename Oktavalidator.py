import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import re

# --- Validation Logic ---

def check_file_contains(filepath, patterns):
    """Checks if a file exists and contains any of the given regex patterns."""
    if not os.path.exists(filepath):
        return False
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            for pattern in patterns:
                if re.search(pattern, content):
                    return True
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
    return False

def check_java_files_for(directory, patterns):
    """Searches all .java files in a directory for the given regex patterns."""
    if not os.path.exists(directory):
        return False
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".java"):
                if check_file_contains(os.path.join(root, file), patterns):
                    return True
    return False

def run_okta_validations(project_path):
    """Runs all Okta-specific validations and returns a results dictionary."""
    results = {}
    is_maven = os.path.exists(os.path.join(project_path, 'pom.xml'))
    is_gradle = os.path.exists(os.path.join(project_path, 'build.gradle'))

    # 1. Dependency Check
    build_file_path = ""
    if is_maven:
        build_file_path = os.path.join(project_path, 'pom.xml')
    elif is_gradle:
        build_file_path = os.path.join(project_path, 'build.gradle')
    
    results['dep_okta_starter'] = check_file_contains(build_file_path, [r'okta-spring-boot-starter'])

    # 2. Configuration Properties Check
    prop_path = os.path.join(project_path, 'src', 'main', 'resources', 'application.properties')
    yml_path = os.path.join(project_path, 'src', 'main', 'resources', 'application.yml')
    
    prop_patterns = [r'okta\.oauth2\.issuer', r'okta\.oauth2\.client-id', r'okta\.oauth2\.client-secret']
    yml_patterns = [r'issuer:', r'client-id:', r'client-secret:'] # Simple check under okta.oauth2 context

    results['config_issuer'] = check_file_contains(prop_path, [prop_patterns[0]]) or check_file_contains(yml_path, [yml_patterns[0]])
    results['config_client_id'] = check_file_contains(prop_path, [prop_patterns[1]]) or check_file_contains(yml_path, [yml_patterns[1]])
    results['config_client_secret'] = check_file_contains(prop_path, [prop_patterns[2]]) or check_file_contains(yml_path, [yml_patterns[2]])

    # 3. Java Code Check
    java_source_path = os.path.join(project_path, 'src', 'main', 'java')
    results['code_security_config'] = check_java_files_for(java_source_path, [r'@Configuration', r'SecurityFilterChain'])
    results['code_oauth2login'] = check_java_files_for(java_source_path, [r'\.oauth2Login'])
        
    return results

# --- Graphical User Interface (GUI) ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Okta Integration Validator for Spring Boot")
        self.geometry("700x500")
        self.resizable(False, False)

        self.project_path = tk.StringVar()

        # Styles
        style = ttk.Style(self)
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('TButton', font=('Helvetica', 12))
        style.configure('Result.TLabel', font=('Helvetica', 12))
        style.configure('TFrame', background='#f0f0f0')
        self.configure(background='#f0f0f0')
        
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Project Selection Section ---
        selection_frame = ttk.Frame(main_frame)
        selection_frame.pack(fill=tk.X, pady=(0, 20))

        select_btn = ttk.Button(selection_frame, text="📁 Select Project Folder", command=self.select_project)
        select_btn.pack(side=tk.LEFT, padx=(0, 10))

        path_label = ttk.Label(selection_frame, textvariable=self.project_path, relief="sunken", padding=5, background="white")
        path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.project_path.set("No project folder selected...")

        # --- Validation Button ---
        validate_btn = ttk.Button(main_frame, text="Analyze Project", command=self.validate_project, style='Accent.TButton')
        style.configure('Accent.TButton', font=('Helvetica', 12, 'bold'), foreground='white', background='#007bff')
        validate_btn.pack(fill=tk.X, pady=10)

        # --- Results Frame ---
        self.results_frame = ttk.Frame(main_frame, padding="10", relief="groove")
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.results_frame, text="Validation Checklist", style='Header.TLabel').pack(pady=(0, 15))
        
        self.checks = {}
        self.create_checklist_items()
    
    def create_checklist_items(self):
        """Creates the labels for each item in the checklist."""
        checklist_items = {
            'dep_okta_starter': "Dependency: `okta-spring-boot-starter` is present",
            'config_issuer': "Configuration: `okta.oauth2.issuer` is set",
            'config_client_id': "Configuration: `okta.oauth2.client-id` is set",
            'config_client_secret': "Configuration: `okta.oauth2.client-secret` is set",
            'code_security_config': "Code: `SecurityFilterChain` bean is defined",
            'code_oauth2login': "Code: `.oauth2Login()` is configured"
        }
        
        for key, text in checklist_items.items():
            frame = ttk.Frame(self.results_frame)
            frame.pack(fill=tk.X, pady=4)
            
            icon_label = ttk.Label(frame, text="⚪", font=('Helvetica', 14))
            icon_label.pack(side=tk.LEFT, padx=(10, 10))
            
            text_label = ttk.Label(frame, text=text, style='Result.TLabel')
            text_label.pack(side=tk.LEFT)
            
            self.checks[key] = icon_label

    def select_project(self):
        """Opens the folder selection dialog."""
        path = filedialog.askdirectory(title="Select the root folder of your Spring Boot project")
        if path:
            self.project_path.set(path)

    def validate_project(self):
        """Runs the validation and updates the GUI."""
        path = self.project_path.get()
        if not os.path.isdir(path) or "No project folder selected" in path:
            messagebox.showerror("Error", "Please select a valid project folder first.")
            return

        results = run_okta_validations(path)
        all_passed = True
        
        for key, icon_label in self.checks.items():
            if results.get(key, False):
                icon_label.config(text="✓", foreground="green")
            else:
                icon_label.config(text="✗", foreground="red")
                all_passed = False
        
        # Summary message
        if all_passed:
            messagebox.showinfo("Result", "Validation Passed 👍\nThe project appears to be correctly configured for Okta.")
        else:
            messagebox.showwarning("Result", "Validation Failed 👎\nSome items are missing for a complete Okta integration. Please review the checklist.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
