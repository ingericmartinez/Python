import os
import zipfile
import xml.etree.ElementTree as ET
from glob import glob
import subprocess
import json
import re
import shutil
from tkinter import Tk, filedialog, messagebox, Label, Button, StringVar, Entry

# Config
TMP_DIR = "/tmp/ear_analysis"
DECOMPILED_DIR = os.path.join(TMP_DIR, "decompiled")
REPORT_DIR = os.path.join(TMP_DIR, "reports")

class EARAnalyzer:
    def __init__(self):
        self.ear_path = ""
        self.report_data = {
            "jndi_resources": [],
            "ibm_was_flags": [],
            "jdbc_connections": [],
            "business_services": {},
            "wsdl_files": [],
            "decompiled_classes": []
        }

    def create_dirs(self):
        """Ensure tmp directories exist."""
        os.makedirs(DECOMPILED_DIR, exist_ok=True)
        os.makedirs(REPORT_DIR, exist_ok=True)

    def extract_ear(self):
        """Unpack EAR to /tmp."""
        with zipfile.ZipFile(self.ear_path, 'r') as zip_ref:
            zip_ref.extractall(TMP_DIR)
        print(f"[*] EAR extracted to: {TMP_DIR}")

    def decompile_jars(self):
        """Decompile all JARs using CFR."""
        jar_files = glob(os.path.join(TMP_DIR, "**/*.jar"), recursive=True)
        for jar in jar_files:
            output_path = os.path.join(DECOMPILED_DIR, os.path.basename(jar).replace(".jar", "")
            subprocess.run(["java", "-jar", "cfr.jar", jar, "--outputdir", output_path], check=True)
            self.report_data["decompiled_classes"].append(output_path)
        print("[*] JARs decompiled to /tmp")

    def scan_ibm_was_jndi(self):
        """Detect IBM WAS-specific JNDI (e.g., cell/persistence nodes)."""
        xml_files = glob(os.path.join(TMP_DIR, "**/*.xml"), recursive=True)
        ibm_patterns = [
            r"Cell=.*Node=.*Server=.*",
            r"jdbc/.*-DS",
            r"wmq/.*QCF"
        ]
        
        for xml_file in xml_files:
            try:
                with open(xml_file, 'r') as f:
                    content = f.read()
                    for pattern in ibm_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            self.report_data["ibm_was_flags"].append(f"IBM WAS JNDI in {os.path.basename(xml_file)}: {pattern}")
            except:
                continue

    def generate_reports(self):
        """Generate JSON and HTML reports."""
        # JSON Report
        json_report = os.path.join(REPORT_DIR, "analysis_report.json")
        with open(json_report, 'w') as f:
            json.dump(self.report_data, f, indent=4)
        
        # HTML Report (simplified)
        html_report = os.path.join(REPORT_DIR, "report.html")
        with open(html_report, 'w') as f:
            f.write(f"""
            <html><body>
                <h1>Legacy EAR Analysis Report</h1>
                <h2>JNDI Resources</h2>
                <ul>{''.join(f'<li>{r}</li>' for r in self.report_data['jndi_resources'])}</ul>
                <h2>IBM WAS Flags</h2>
                <ul>{''.join(f'<li>{f}</li>' for f in self.report_data['ibm_was_flags'])}</ul>
                <h2>Decompiled Classes</h2>
                <ul>{''.join(f'<li>{d}</li>' for d in self.report_data['decompiled_classes'])}</ul>
            </body></html>
            """)
        
        print(f"[*] Reports generated in: {REPORT_DIR}")

    def analyze(self, ear_path):
        """Run full analysis pipeline."""
        self.ear_path = ear_path
        self.create_dirs()
        self.extract_ear()
        self.decompile_jars()
        self.scan_ibm_was_jndi()
        self.generate_reports()
        return self.report_data

# GUI
class LegacyAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Legacy EAR Analyzer")
        self.analyzer = EARAnalyzer()
        
        Label(root, text="EAR File Path:").pack()
        self.ear_path_var = StringVar()
        Entry(root, textvariable=self.ear_path_var, width=50).pack()
        Button(root, text="Browse", command=self.browse_ear).pack()
        Button(root, text="Analyze", command=self.run_analysis).pack()
    
    def browse_ear(self):
        """Open file dialog to select EAR."""
        path = filedialog.askopenfilename(filetypes=[("EAR Files", "*.ear")])
        self.ear_path_var.set(path)
    
    def run_analysis(self):
        """Execute analysis and show results."""
        ear_path = self.ear_path_var.get()
        if not ear_path:
            messagebox.showerror("Error", "No EAR file selected!")
            return
        
        try:
            report = self.analyzer.analyze(ear_path)
            messagebox.showinfo(
                "Analysis Complete", 
                f"Report generated at:\n{REPORT_DIR}\n\n"
                f"Found {len(report['jndi_resources'])} JNDI resources.\n"
                f"Found {len(report['ibm_was_flags'])} IBM WAS flags."
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = Tk()
    app = LegacyAnalyzerGUI(root)
    root.mainloop()
