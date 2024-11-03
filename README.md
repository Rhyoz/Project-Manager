Boligventilasjon Project Management

A PyQt5 application for managing Boligventilasjon projects, including project creation, tracking, and documentation.
Features

   - Create and manage projects with detailed information.
   - Support for residential complexes with multiple units.
   - Generate and view DOCX reports for projects and units.
   - Import and view floor plans for projects and units.
   - Track project status (Active, Completed, Finished).
   - User-friendly interface with shortcuts for efficient navigation.

Requirements

    Python 3.6 or higher.
    The following Python packages (listed in requirements.txt):
        PyQt5==5.15.4
        SQLAlchemy==1.4.46
        pywin32==303 (Windows only)
        openpyxl==3.0.10
        python-docx==0.8.11

Installation

    Clone the repository:

    bash

git clone https://github.com/Rhyoz/Project-Manager.git
cd Project-Manager

Create a virtual environment (optional but recommended):

bash

python -m venv venv

Activate the virtual environment:

    On Windows:

    bash

venv\Scripts\activate

On macOS/Linux:

bash

    source venv/bin/activate

Install the required packages:

bash

    pip install -r requirements.txt

Configuration

    Set up the configuration file:

    Ensure that a config.ini file exists in the root directory with the following content:

    ini

    [Paths]
    template_dir = ./Template
    project_dir = ./Projects
    docx_temp_dir = ./Temp
    logs_dir = ./Logs

    Set up templates:
        Run the application (see Running the Application below).
        In the menu bar, navigate to File ➔ Setup Template.
        Follow the prompts to select the Innregulering.docx and Sjekkliste.docx template files.
        These templates are required for generating project documents.

Running the Application

Run the main.py file to start the application:

bash

python main.py

The main window of the Project-Manager application will appear.
Usage
Adding a New Project

    Navigate to the Project Overview tab (should be the default tab upon startup).
    Click on the "Add New Project" button.
    Fill out the project details in the dialog:
       - Project Name and/or Project Number.
       - Worker (choose between "Alex" or "William").
       - Start Date (defaults to the current date).
       - Status (defaults to "Active").
       - Check Residential Complex if applicable.
           - Specify the number of units.
           - Provide unique names for each unit.
       - Optionally add Extra information and Main Contractor.

Managing Projects

    View Projects:
        Projects are organized into tabs based on their status:
            Project Overview: Active projects.
            Completed Projects: Projects marked as completed.
            Finished Projects: Projects marked as finished.
            Detailed Project View: All projects without status filtering.

    Edit or Delete Projects:
        Right-click on a project in the list to open the context menu.
        Choose Edit (functionality placeholder) or Delete.

    Change Project Status:
        Use the Move buttons to update the project's status:
            Move(1) and Move(2) buttons allow transitioning between statuses.

Working with Units (for Residential Complexes)

    Toggle Unit Completion:
        Expand a residential project to view its units.
        Check or uncheck the box next to a unit to mark it as done or not done.

    View and Manage Unit Documents:
        Use the Innregulering and Sjekkliste buttons next to each unit to view or save the respective documents.

Floor Plans

    Import Floor Plans:
        Use the Floor Plan(s) split button to import PDF floor plans for projects or units.
        For residential complexes, you can also manage the Master Floor Plan.

    View Floor Plans:
        After importing, click on View in the Floor Plan(s) menu to open the floor plan PDF.

Generating Reports

    View DOCX Overview:
        Click on the View DOCX button to generate and open a DOCX report of the projects in the current tab.

    Save DOCX Overview:
        Use the Save As... option in the View DOCX split button to save the report to a specified location.

Keyboard Shortcuts

    Switch Between Tabs:
        Alt+1: Project Overview
        Alt+2: Completed Projects
        Alt+3: Finished Projects
        Alt+4: Detailed Project View

Logging

    Log Files:
        Application logs are stored in the Logs directory.
        Logs include information about actions taken within the application and any errors encountered.

Troubleshooting

    Missing Template Files:
        Ensure that the Template directory contains Innregulering.docx and Sjekkliste.docx.
        Use the Setup Template option in the File menu to correctly set up templates.

    Database Issues:
        If you encounter database errors, ensure that you have the necessary permissions to read/write in the project directory.

    Dependency Errors:
        Verify that all required Python packages are installed.
        Reinstall dependencies using pip install -r requirements.txt.

License

This project is licensed under the MIT License - see the LICENSE file for details.
