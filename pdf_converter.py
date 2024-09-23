# pdf_converter.py
import subprocess
import os
from PyQt5.QtCore import QObject, pyqtSignal, QThread

class PDFConverter(QObject):
    conversion_complete = pyqtSignal(str)
    conversion_failed = pyqtSignal(str)

    def __init__(self, excel_path, pdf_path):
        super().__init__()
        self.excel_path = excel_path
        self.pdf_path = pdf_path

    def run_conversion(self):
        try:
            # This example uses Windows COM interface; adjust accordingly for other OS
            if os.name == 'nt':
                import win32com.client
                excel = win32com.client.Dispatch("Excel.Application")
                excel.Visible = False
                wb = excel.Workbooks.Open(self.excel_path)
                wb.ExportAsFixedFormat(0, self.pdf_path)
                wb.Close(False)
                excel.Quit()
                self.conversion_complete.emit(self.pdf_path)
            else:
                # For macOS or Linux, you might need to use LibreOffice or another tool
                # Example using LibreOffice:
                subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', self.excel_path, '--outdir', os.path.dirname(self.pdf_path)], check=True)
                self.conversion_complete.emit(self.pdf_path)
        except Exception as e:
            self.conversion_failed.emit(str(e))
