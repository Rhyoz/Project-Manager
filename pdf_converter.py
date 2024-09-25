# pdf_converter.py
import subprocess
import os
from PyQt5.QtCore import QObject, pyqtSignal
import sys
from logger import get_logger

logger = get_logger(__name__)

class PDFConverter(QObject):
    conversion_complete = pyqtSignal(str)
    conversion_failed = pyqtSignal(str)

    def __init__(self, excel_path, pdf_path):
        super().__init__()
        self.excel_path = excel_path
        self.pdf_path = pdf_path

    def run_conversion(self):
        try:
            if os.name == 'nt':
                import win32com.client
                excel = win32com.client.Dispatch("Excel.Application")
                excel.Visible = False
                wb = excel.Workbooks.Open(self.excel_path)
                wb.ExportAsFixedFormat(0, self.pdf_path)
                wb.Close(False)
                excel.Quit()
                logger.info(f"Converted Excel to PDF: {self.excel_path} -> {self.pdf_path}")
                self.conversion_complete.emit(self.pdf_path)
            elif sys.platform.startswith('darwin') or os.name == 'posix':
                # Use LibreOffice for macOS and Linux
                subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', self.excel_path, '--outdir', os.path.dirname(self.pdf_path)], check=True)
                logger.info(f"Converted Excel to PDF using LibreOffice: {self.excel_path} -> {self.pdf_path}")
                self.conversion_complete.emit(self.pdf_path)
            else:
                raise OSError("Unsupported operating system for PDF conversion.")
        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            self.conversion_failed.emit(str(e))