import sys
import os
import markdown
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

def markdown_to_text(markdown_string):
    """
    Core logic: Converts a markdown string to plain text.
    Optimized by:
      - Enabling 'extra' extension pack for tables, code blocks, etc.
      - Attempting to use the fast C-based 'lxml' parser if available, falling back to 'html.parser'.
    """
    # Using 'extra' extension package ensures tables, footnotes, fenced code blocks, etc. are processed.
    html = markdown.markdown(markdown_string, extensions=['extra'])
    
    # Try using lxml for speed, fallback to standard html.parser
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")
        
    return soup.get_text(separator='\n')

class ConversionWorker(QThread):
    """Worker thread to handle file reading, conversion, and writing in the background."""
    finished = pyqtSignal(str, str)  # Emits (input_path, output_path) on success
    failed = pyqtSignal(str, str)    # Emits (input_path, error_message) on failure

    def __init__(self, input_path):
        super().__init__()
        self.input_path = input_path

    def run(self):
        try:
            # File reads can be slow on network drives or slow HDDs
            with open(self.input_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            plain_text = markdown_to_text(md_content)
            
            output_path = os.path.splitext(self.input_path)[0] + ".txt"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(plain_text)
                
            self.finished.emit(self.input_path, output_path)
        except Exception as e:
            self.failed.emit(self.input_path, str(e))

class MarkdownConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.active_workers = []  # Keep references to prevent garbage collection
        self.initUI()

    def initUI(self):
        # Set up the main window
        self.setWindowTitle("Markdown to Text Converter")
        self.resize(400, 280)
        
        # Enable Drag and Drop for the main window
        self.setAcceptDrops(True)

        # Create a vertical layout
        layout = QVBoxLayout()

        # Create the Drop Zone Label
        self.drop_label = QLabel()
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_label_style("idle")
        layout.addWidget(self.drop_label)

        # Create the Browse Button
        self.browse_btn = QPushButton("Browse for File")
        self.browse_btn.setMinimumHeight(40)
        self.browse_btn.clicked.connect(self.browse_file)
        layout.addWidget(self.browse_btn)

        self.setLayout(layout)

    def set_label_style(self, state, text=None):
        """Helper to change styling without losing padding, border-radius, or size structure."""
        base_style = """
            QLabel {
                border-radius: 8px;
                padding: 20px;
                font-size: 14px;
                %s
            }
        """
        
        if state == "idle":
            style = base_style % "border: 2px dashed #aaa; color: #555;"
            default_text = "Drag and Drop a .md file here\n\n— OR —"
        elif state == "processing":
            style = base_style % "border: 2px dashed #008CBA; color: #008CBA; font-weight: bold;"
            default_text = "Converting file(s)..."
        elif state == "success":
            style = base_style % "border: 2px solid #4CAF50; color: #4CAF50; font-weight: bold;"
            default_text = "Success!"
        elif state == "error":
            style = base_style % "border: 2px solid #F44336; color: #F44336; font-weight: bold;"
            default_text = "An error occurred."
        else:
            style = base_style % "border: 2px dashed #aaa; color: #555;"
            default_text = ""

        self.drop_label.setStyleSheet(style)
        if text:
            self.drop_label.setText(text)
        elif default_text:
            self.drop_label.setText(default_text)

    # --- Drag and Drop Events ---
    
    def dragEnterEvent(self, event):
        """Fires when a file is dragged over the window."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Fires when the user drops files."""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        md_files = [f for f in files if f.lower().endswith('.md')]
        
        if not md_files:
            self.set_label_style("error", "Error: Please drop valid .md file(s).")
            return

        self.process_files(md_files)

    # --- Button Event ---

    def browse_file(self):
        """Fires when the Browse button is clicked."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Markdown File", 
            "", 
            "Markdown Files (*.md);;All Files (*)"
        )
        if file_path:
            self.process_files([file_path])

    # --- Core Processing Trigger ---

    def process_files(self, file_paths):
        """Launches background workers for file conversion."""
        self.set_label_style("processing", f"Converting {len(file_paths)} file(s)...")
        
        self.total_to_process = len(file_paths)
        self.processed_count = 0
        self.success_files = []
        self.failed_files = []

        for path in file_paths:
            worker = ConversionWorker(path)
            worker.finished.connect(self.on_worker_success)
            worker.failed.connect(self.on_worker_failed)
            self.active_workers.append(worker)
            worker.start()

    def on_worker_success(self, input_path, output_path):
        self.processed_count += 1
        self.success_files.append(os.path.basename(output_path))
        self.check_progress()

    def on_worker_failed(self, input_path, error_message):
        self.processed_count += 1
        self.failed_files.append((os.path.basename(input_path), error_message))
        self.check_progress()

    def check_progress(self):
        """Called when a worker finishes to aggregate results and update UI."""
        if self.processed_count >= self.total_to_process:
            # Clean up worker references
            self.active_workers.clear()
            
            # Formulate final status message
            if not self.failed_files:
                if len(self.success_files) == 1:
                    msg = f"Success!\nSaved as:\n{self.success_files[0]}"
                else:
                    msg = f"Success!\nConverted {len(self.success_files)} files successfully."
                self.set_label_style("success", msg)
            elif not self.success_files:
                msg = "Failed to convert files:\n" + "\n".join([f"{f}: {err}" for f, err in self.failed_files])
                self.set_label_style("error", msg)
            else:
                msg = (f"Completed with issues.\n"
                       f"Saved {len(self.success_files)} files.\n"
                       f"Failed {len(self.failed_files)} files.")
                self.set_label_style("error", msg)

if __name__ == '__main__':
    # Standard PyQt initialization
    app = QApplication(sys.argv)
    window = MarkdownConverterApp()
    window.show()
    sys.exit(app.exec())
