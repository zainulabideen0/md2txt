import sys
import os
import markdown
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QFileDialog)
from PyQt6.QtCore import Qt

def markdown_to_text(markdown_string):
    """Core logic: Converts a markdown string to plain text."""
    html = markdown.markdown(markdown_string)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator='\n')

class MarkdownConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set up the main window
        self.setWindowTitle("Markdown to Text Converter")
        self.resize(400, 250)
        
        # Enable Drag and Drop for the main window
        self.setAcceptDrops(True)

        # Create a vertical layout
        layout = QVBoxLayout()

        # Create the Drop Zone Label
        self.drop_label = QLabel("Drag and Drop a .md file here\n\n— OR —")
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Style the label to look like a drop zone
        self.drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 8px;
                padding: 20px;
                font-size: 14px;
                color: #555;
            }
        """)
        layout.addWidget(self.drop_label)

        # Create the Browse Button
        self.browse_btn = QPushButton("Browse for File")
        self.browse_btn.setMinimumHeight(40)
        self.browse_btn.clicked.connect(self.browse_file)
        layout.addWidget(self.browse_btn)

        self.setLayout(layout)

    # --- Drag and Drop Events ---
    
    def dragEnterEvent(self, event):
        """Fires when a file is dragged over the window."""
        # Check if the dragged object contains file URLs
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Fires when the user drops the file."""
        # Extract the file path from the drop event
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for file_path in files:
            if file_path.lower().endswith('.md'):
                self.convert_file(file_path)
            else:
                self.drop_label.setText("Error: Please drop a valid .md file.")

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
            self.convert_file(file_path)

    # --- Core Processing ---

    def convert_file(self, input_path):
        """Reads the MD, converts it, and writes the TXT file."""
        try:
            # Read the Markdown
            with open(input_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Convert using our helper function
            plain_text = markdown_to_text(md_content)
            
            # Generate output path (same directory, just change extension to .txt)
            output_path = os.path.splitext(input_path)[0] + ".txt"
            
            # Write the Plain Text
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(plain_text)
                
            # Update the UI with a success message
            filename = os.path.basename(output_path)
            self.drop_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                    padding: 20px;
                    font-size: 14px;
                    color: #4CAF50;
                    font-weight: bold;
                }
            """)
            self.drop_label.setText(f"Success!\nSaved as:\n{filename}")
            
        except Exception as e:
            # Display any errors in the UI
            self.drop_label.setStyleSheet("border: 2px solid red; color: red;")
            self.drop_label.setText(f"An error occurred:\n{str(e)}")

if __name__ == '__main__':
    # Standard PyQt initialization
    app = QApplication(sys.argv)
    window = MarkdownConverterApp()
    window.show()
    sys.exit(app.exec())
