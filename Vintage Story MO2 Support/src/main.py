import sys, winreg, configparser, os, shutil, re, zipfile, argparse, json, datetime
import urllib.request as ur
from urllib.request import urlretrieve
from PyQt6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QFileDialog,
    QWidget,
    QLabel,
    QCheckBox,
    QApplication,
    QMessageBox,
    QComboBox,
    QInputDialog
)
from PyQt6.QtCore import Qt

# Constants
config = configparser.ConfigParser()

# Check if the config file exists
config_file_path = os.path.join(os.path.dirname(sys.argv[0]), 'config.ini')
if not os.path.exists(config_file_path):
    
    # Create a new config file with default values
    config['PATHS'] = {'VSPath' : '', 'MO2Path' : ''}
    config['SETTINGS'] = {'DeleteOldVersions': 'False', 'KeepDownloads': 'False'}
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)

# Make the config accesible
config.read(config_file_path)

# Check if the profiles and configsets folders exist, if not create them
#if not os.path.exists(os.path.dirname(sys.argv[0]) + '\\profiles'):
#    os.mkdir(os.path.dirname(sys.argv[0]) + '\\profiles')

if not os.path.exists(os.path.dirname(sys.argv[0]) + '\\configsets'):
    os.mkdir(os.path.dirname(sys.argv[0]) + '\\configsets')

# Main PyQt6 window class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Basic Window setup
        self.setWindowTitle("VS MO2 Manager")
        self.setFixedSize(400, 450)

        # Main widget to hold all other widgets
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Top level layout vertical stack
        layout = QVBoxLayout(main_widget)
        

        #############################################
        # Paths section

        # Label for Paths section
        file_section_label = QLabel("Paths")
        file_section_label.font().setBold
        file_section_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_section_label.setStyleSheet("font-size: 20px;")  # Set font size

        # First text bar and browse button for MO2 folder
        self.MO2_path_text = QLineEdit()
        self.browse_MO2_path = QPushButton("Browse...")
        self.browse_MO2_path.clicked.connect(self.select_MO2_path)
        
        # Second text bar and browse button for VS folder
        self.VS_path_text = QLineEdit()
        self.browse_VS_path = QPushButton("Browse...")
        self.browse_VS_path.clicked.connect(self.select_VS_path)      

        
        #############################################
        # Buttons for ModDB protocol and migration
        
        # Label for ModDB protocol section
        protocol_label = QLabel("ModDB Protocol")
        protocol_label.font().setBold
        protocol_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        protocol_label.setStyleSheet("font-size: 20px;")
        
        # Set protocol button
        self.set_button = QPushButton("Set ModDB Protocol")
        self.set_button.clicked.connect(self.set_moddb_protocol)
        
        # Reset protocol button
        self.reset_button = QPushButton("Reset ModDB Protocol")
        self.reset_button.clicked.connect(self.reset_moddb_protocol)

        # Checkboxes for a feature toggle
        self.feature_delete_old_versions = QCheckBox("Delete old versions:")
        self.feature_delete_old_versions.stateChanged.connect(self.toggle_feature)

        self.feature_keep_downloads = QCheckBox("Keep downloaded files:")
        self.feature_keep_downloads.stateChanged.connect(self.toggle_feature)
        

        ##############################################
        # Config section
        
        # Label for Config section
        config_label = QLabel("Config")
        config_label.font().setBold
        config_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        config_label.setStyleSheet("font-size: 20px;")

        # Buttons for config preset tools
        self.save_config_set_button = QPushButton("Save current set")
        self.save_config_set_button.clicked.connect(self.create_config_set)
        self.remove_config_set_button = QPushButton("Remove current set")
        self.remove_config_set_button.clicked.connect(self.remove_config_set)
        self.rename_config_set_button = QPushButton("Rename current set")
        self.rename_config_set_button.clicked.connect(self.rename_config_set)
        self.load_config_set_button = QPushButton("Load selected set")
        self.load_config_set_button.clicked.connect(self.load_config_set)

        # Dropdown for selecting config set
        config_select = QVBoxLayout()
        dropdown_label = QLabel("Current Config Set:")
        self.config_dropdown = QComboBox()
        config_select.addWidget(dropdown_label)
        config_select.addWidget(self.config_dropdown)
        
        
        ##################################################
        # Misc Buttons
        
        self.misc_label = QLabel("Misc")
        self.misc_label.font().setBold
        self.misc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.misc_label.setStyleSheet("font-size: 20px;")

        # Migrate mods button
        self.migrate_button = QPushButton("Migrate Mods")
        self.migrate_button.clicked.connect(self.migrate_mods)
        
        # Exit button
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(sys.exit)
        
        
        
        # Build Sections
        
        # Set up layout for Paths section
        path_column = QVBoxLayout()
        
        # First text bar and browse button
        MO2_path_row = QHBoxLayout()
        MO2_path_row.addWidget(QLabel("MO2 Folder:"))
        MO2_path_row.addWidget(self.MO2_path_text)
        MO2_path_row.addWidget(self.browse_MO2_path)
        
        # Second text bar and browse button
        VS_path_row = QHBoxLayout()
        VS_path_row.addWidget(QLabel("VS Folder:    "))
        VS_path_row.addWidget(self.VS_path_text)
        VS_path_row.addWidget(self.browse_VS_path)
        
        # Add the rows to the file layout
        path_column.addWidget(file_section_label)
        path_column.addLayout(MO2_path_row)
        path_column.addLayout(VS_path_row)
        
        # Protocol section
        protocol_row = QHBoxLayout()
        protocol_row.addWidget(self.reset_button)
        protocol_row.addWidget(self.set_button)

        # Feature section
        feature_row = QHBoxLayout()
        feature_row.addWidget(self.feature_keep_downloads)
        feature_row.addWidget(self.feature_delete_old_versions)
        

        
        # Config section
        config_row = QHBoxLayout()
        config_row.addWidget(config_label)

        config_preset_tools1 = QHBoxLayout()
        config_preset_tools1.addWidget(self.save_config_set_button)
        config_preset_tools1.addWidget(self.remove_config_set_button)
        config_preset_tools2 = QHBoxLayout()
        config_preset_tools2.addWidget(self.load_config_set_button)
        config_preset_tools2.addWidget(self.rename_config_set_button)

        # Misc section
        misc_row = QHBoxLayout()
        misc_row.addWidget(self.migrate_button)
        misc_row.addWidget(self.exit_button)
        

        # Add all to main layout
        layout.addLayout(path_column)
        layout.addSpacing(20)  # Spacer
        layout.addWidget(protocol_label)
        layout.addLayout(protocol_row)
        layout.addLayout(feature_row)
        layout.addSpacing(20)  # Spacer
        layout.addWidget(config_label)
        layout.addLayout(config_select)
        layout.addLayout(config_preset_tools1)
        layout.addLayout(config_preset_tools2)
        layout.addStretch()
        layout.addWidget(self.misc_label)
        layout.addLayout(misc_row)
        self.load_settings_from_config()
        self.read_config_sets()
    
    def load_settings_from_config(self):
        #Load paths and settings from the config file and populate the textboxes and checkboxes.
         
        if config.has_section('PATHS'):
            # Get the MO2Path and VSPath values if they exist
            mo2_path = config.get('PATHS', 'MO2Path', fallback='')
            vs_path = config.get('PATHS', 'VSPath', fallback='')
            
            # Populate the textboxes
            self.MO2_path_text.setText(mo2_path)
            self.VS_path_text.setText(vs_path)
        if config.has_section('SETTINGS'):
            # Get the settings values if they exist
            delete_old_versions = config.getboolean('SETTINGS', 'DeleteOldVersions', fallback=False)
            keep_downloads = config.getboolean('SETTINGS', 'KeepDownloads', fallback=False)
            
            # Set the checkboxes based on the settings
            self.feature_delete_old_versions.setChecked(delete_old_versions)
            self.feature_keep_downloads.setChecked(keep_downloads)

    def select_MO2_path(self):
        # Get the folder path using a file dialog
        
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select MO2 Folder"
        )
        if folder_path:
            # Normalize the path and set it in the text box
            normalized_path = os.path.normpath(folder_path)
            self.MO2_path_text.setText(normalized_path)
            
            # Save the path to the config file
            if not config.has_section('PATHS'):
                config.add_section('PATHS')
            config.set('PATHS', 'MO2Path', normalized_path)
            with open(config_file_path, 'w') as configfile:
                config.write(configfile)
    
    def select_VS_path(self):
        # Get the folder path using a file dialog
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select VS Folder"
        )
        if folder_path:
            # Normalize the path and set it in the text box
            normalized_path = os.path.normpath(folder_path)
            self.VS_path_text.setText(normalized_path)
            
            # Save the path to the config file
            if not config.has_section('PATHS'):
                config.add_section('PATHS')
            config.set('PATHS', 'VSPath', normalized_path)
            with open(config_file_path, 'w') as configfile:
                config.write(configfile)
    
    def set_moddb_protocol(self):
        # Set the ModDB protocol
        
        program_path = os.path.abspath(sys.argv[0])
        # Open the registry key for the ModDB protocol
        key1 = winreg.OpenKeyEx(winreg.HKEY_CLASSES_ROOT,'vintagestorymodinstall\\shell\\open\\command',0,winreg.KEY_SET_VALUE)

        # Set the value to the path of the program and the arguments
        winreg.SetValueEx(key1,"",0,winreg.REG_SZ,'"' + program_path + '" --install "%1"')
        winreg.CloseKey(key1)       

    def reset_moddb_protocol(self):
        # Reset the ModDB protocol

        # Check if the VS path is set
        if self.VS_path_text.text() == "":
            QMessageBox.warning(self, "Warning", "Please select the path to your Vintage Story installation.")
            return
        else:
            VS_path = self.VS_path_text.text()
            # Open the registry key for the ModDB protocol
            key1 = winreg.OpenKeyEx(winreg.HKEY_CLASSES_ROOT,'vintagestorymodinstall\\shell\\open\\command',0,winreg.KEY_SET_VALUE)

            # Set the value to the path of the Vintage Story executable and the arguments
            winreg.SetValueEx(key1,"",0,winreg.REG_SZ, '"' + VS_path + '\\VintageStory.exe" -i "%1"')
            winreg.CloseKey(key1)
        
    def toggle_feature(self, state):
        #Toggle a feature based on checkbox state

        # Check which checkbox was clicked and update the config file accordingly
        checked = (state == Qt.CheckState.Checked.value)
        if self.sender() == self.feature_delete_old_versions:
            config.set('SETTINGS', 'DeleteOldVersions', str(checked))
        elif self.sender() == self.feature_keep_downloads:
            config.set('SETTINGS', 'KeepDownloads', str(checked))
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)
    
    def read_config_sets(self):
        # Read the config sets from the configsets folder and populate the dropdown
        config_sets = os.listdir(os.path.dirname(sys.argv[0]) + '\\configsets')
        for config_set in config_sets:
                self.config_dropdown.addItem(config_set)
    
    def create_config_set(self):
        # Create a new config set or overwrite an existing one
        
        # VS config path
        config_path = os.getenv('APPDATA') + '\\VintagestoryData\\ModConfig\\'
        
        # Prompt the user for a new config set name
        new_set_name = QInputDialog.getText(self, "New Config Set", "Enter the name of the new config set:",text=self.config_dropdown.currentText())
        
        # Check if the user cancelled the dialog
        if not new_set_name[1]:
            return
        
        # Check if the new name already exists or if the name is empty
        if os.path.exists(os.path.dirname(sys.argv[0]) + '\\configsets\\' + new_set_name[0]) and self.config_dropdown.currentText() != "":
            
            ## Prompt the user to overwrite the existing config set
            reply = QMessageBox.question(self, "Warning", "A config set with this name already exists. Do you want to overwrite?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            
            ## Check the user's response
            if reply == QMessageBox.StandardButton.No:
                return
            if reply == QMessageBox.StandardButton.Yes:
                
                # Read the config set path normalize
                config_set_path = os.path.join(os.path.dirname(sys.argv[0]), 'configsets', self.config_dropdown.currentText())
                normpath = os.path.normpath(config_set_path)
                
                # remove the old config set folder
                if os.path.exists(normpath):
                    for item in os.listdir(normpath):
                        source_path = os.path.join(normpath, item)
                        if os.path.isfile(source_path):
                            os.remove(source_path)
                        elif os.path.isdir(source_path):
                            shutil.rmtree(source_path)
                
                # Copy the current config files to the new config set folder
                for item in os.listdir(config_path):
                    source_path = os.path.join(config_path, item)
                    if os.path.isfile(source_path):
                        shutil.copy(source_path, normpath + '\\' + item)
                    elif os.path.isdir(source_path):
                        shutil.copytree(source_path, normpath + '\\' + item)
                QMessageBox.information(self, "Info", "Config set overwritten successfully.")
                return

        # Create the new config set folder
        os.mkdir(os.path.dirname(sys.argv[0]) + '\\configsets\\' + new_set_name[0])
        
        # Copy the current config files to the new config set folder
        if os.path.exists(config_path):
            for item in os.listdir(config_path):
                source_path = os.path.join(config_path, item)
                dest_path = os.path.join(os.path.dirname(sys.argv[0]), 'configsets', new_set_name[0], item)
                if os.path.isfile(source_path):
                    shutil.copy(source_path, dest_path)
                elif os.path.isdir(source_path):
                    shutil.copytree(source_path, dest_path)
        
        ## Update the dropdown with the new config set name and set it as the current selection
        self.config_dropdown.addItem(new_set_name[0])
        self.config_dropdown.setCurrentText(new_set_name[0])
        QMessageBox.information(self, "Info", "Config set created successfully.")
    
    def remove_config_set(self):
        
        # Prompt the user for confirmation before removing the config set
        reply = QMessageBox.question(self, "Remove Config Set", "Are you sure you want to remove the current config set?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # read the config set path
            current_set = self.config_dropdown.currentText()
            config_set_path = os.path.join(os.path.dirname(sys.argv[0]), 'configsets', current_set)
            # Check if the config set exists and isn't empty and remove it
            if os.path.exists(config_set_path) and self.config_dropdown.currentText() != "":
                shutil.rmtree(config_set_path)
                self.config_dropdown.removeItem(self.config_dropdown.currentIndex())
                QMessageBox.information(self, "Info", "Config set removed successfully.")
            else:
                QMessageBox.warning(self, "Warning", "Config set not found.")
        else:
            QMessageBox.information(self, "Info", "Config set removal cancelled.")
    
    def load_config_set(self):
        current_set = self.config_dropdown.currentText()
        ## Check if the current set is empty
        if current_set == "":
            QMessageBox.warning(self, "Warning", "No config set selected.")    
            return
        
        # Make Backup folder if it does not exist
        if not os.path.exists(os.path.join(os.path.dirname(sys.argv[0]), 'Backup')):
            os.mkdir(os.path.join(os.path.dirname(sys.argv[0]), 'Backup'))
        config_path = os.getenv('APPDATA') + '\\VintagestoryData\\ModConfig'
        # Get the current date and time for the backup file name         
        current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a zip file for the backup
        backup_path = os.path.join(os.path.dirname(sys.argv[0]), 'Backup', 'config_backup' + current_datetime + '.zip')
        normpath = os.path.normpath(backup_path)
        with zipfile.ZipFile(normpath, 'w') as backup_zip:
            if os.path.exists(config_path):
                # Loop through the files and folders in the config path
                for item in os.listdir(config_path):
                    source_path = os.path.join(config_path, item)
                    # Put the files and folders into the zip file
                    if os.path.isfile(source_path):
                        backup_zip.write(source_path, os.path.relpath(source_path, config_path))
                    elif os.path.isdir(source_path):
                        for root, _, files in os.walk(source_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                backup_zip.write(file_path, os.path.relpath(file_path, config_path))

        # Remove the current config files
        if os.path.exists(config_path):
            for item in os.listdir(config_path):
                source_path = os.path.join(config_path, item)
                if os.path.isfile(source_path):
                    os.remove(source_path)
                elif os.path.isdir(source_path):
                    shutil.rmtree(source_path)
        
        # Read the config set path
        config_set_path = os.path.join(os.path.dirname(sys.argv[0]), 'configsets', current_set)
        # Copy the selected config set files to the Vintage Story config folder
        if os.path.exists(config_set_path):
            for item in os.listdir(config_set_path):
                source_path = os.path.join(config_set_path, item)
                dest_path = os.path.join(config_path, item)
                if os.path.isfile(source_path):
                    shutil.copy(source_path, dest_path)
                elif os.path.isdir(source_path):
                    shutil.copytree(source_path, dest_path)
            QMessageBox.information(self, "Info", "Config set loaded successfully.")
        else:
            QMessageBox.warning(self, "Warning", "Config set not found.")

    def rename_config_set(self):
        # Get the current config set name
        current_set = self.config_dropdown.currentText()
        if current_set == "":
            QMessageBox.warning(self, "Warning", "No config set selected.")
            return

        # Prompt the user for a new name
        new_name, ok = QInputDialog.getText(self, "Rename Config Set", "Enter the new name for the config set:", text=current_set)
        if ok and new_name:
            # Rename the folder
            old_path = os.path.join(os.path.dirname(sys.argv[0]), 'configsets', current_set)
            new_path = os.path.join(os.path.dirname(sys.argv[0]), 'configsets', new_name)
            os.rename(old_path, new_path)

            # Update the dropdown
            index = self.config_dropdown.currentIndex()
            self.config_dropdown.setItemText(index, new_name)
            QMessageBox.information(self, "Info", "Config set renamed successfully.")

    def migrate_mods(self):
        #Migrate mods to MO2 mods folder

        mo2_path = self.MO2_path_text.text()
        # Check if the MO2 path is set
        if mo2_path == "":
            QMessageBox.warning(self, "Warning", "Please select the path to your Mod Organizer installation.")
            return
        else:
            # User selects the source folder containing the mods to migrate
            QMessageBox.information(self, "Info", "Please Select the source folder containing the mods to migrate.")
            mods_path = QFileDialog.getExistingDirectory(
                self, "Select mods folder"
            )
            # List all files in the selected folder
            files = os.listdir(mods_path)
            # List of banned default files not to be copied
            bannedFiles = ("VSCreativeMod.dll", "VSCreativeMod.pdb", "VSEssentials.dll", "VSEssentials.pdb", "VSSurvivalMod.dll", "VSSurvivalMod.pdb")
            # Loop through the files
            for file in files:
                banned = file in bannedFiles
                if not banned:
                    fullpath = (mods_path + "\\" + file)
                    # Read the zip file
                    with zipfile.ZipFile(fullpath, mode="r") as archive:
                        # Read the modinfo.json file inside the zip
                        with archive.open("modinfo.json") as modInfo:
                            # Parse the modinfo.json file to get the official mod name
                            modJson = modInfo.read().decode("utf-8")
                            modJson = re.split('"name": "',modJson,1,flags=re.IGNORECASE)[1]
                            modName = re.split('"',modJson,1)[0]
                    # Clean the mod name from illegal characters in folders
                    legalName = re.sub(':',"-",modName)
                    # Create a new folder for the mod in MO2's mods folder
                    newDir = mo2_path + "\\mods\\" + legalName
                    os.mkdir(newDir)
                    # Move the downloaded zip file into the new folder
                    shutil.copy(mods_path + "\\" + file,newDir)

            QMessageBox.warning(self, "Info", "Mods migrated successfully.")

def install_mod(args):
    # Install a mod to MO2 using the VSDB protocol
    
    #Set local work directory
    baseDir = (os.path.dirname(sys.argv[0]))
    os.chdir(baseDir)

    # Constants
    MO2path = config.get('PATHS','MO2Path')
    # Check if the MO2 path is set
    if MO2path == "":
        input("Please set the path to your Mod Organizer installation using the manager.")
        return
    # ModDB API URL
    modAPIUrl = "https://mods.vintagestory.at/api/mod/"

    # Parse VSDB arguments
    modID = args.split('@',1)[0].rsplit('://',1)[1]
    modVersion = args.split('@',1)[1].rsplit('/',1)[0]

    # Retrieve Json from ModDB API
    url = modAPIUrl + modID
    with ur.urlopen(url) as response:
        modJson = response.read()


    # Parse Json
    jsonObject = json.loads(modJson)

    # Check releases for requested release (new to old)
    i = 0
    releaseFound = False
    while releaseFound == False or i == 100:
        if (jsonObject['mod']['releases'][i]['modversion']) == modVersion:
            releaseFound = True
        else:
            i = i+1

    # Lookup URL for requested version
    downloadURL = jsonObject['mod']['releases'][i]['mainfile']

    # Change work directory to MO2's downloads folder
    os.chdir(MO2path + '\\downloads')

    # Download the file
    file = downloadURL.rsplit('dl=',1)[1]
    urlretrieve(downloadURL,file)

    # Open the zip file and check the contained modinfo.json for an official mod name
    zipPath = (os.getcwd() + "\\" + file)
    with zipfile.ZipFile(zipPath, mode="r") as archive:
        with archive.open("modinfo.json") as modInfo:
            
            modJson = modInfo.read().decode("utf-8")
            modJson = re.split('"name": "',modJson,1,flags=re.IGNORECASE)[1]
            modName = re.split('"',modJson,1)[0]

    # Clean name from illegal characters in folders        
    legalName = re.sub(':',"-",modName)
    newDir = MO2path + "\\mods\\" + legalName

    # Create new folder for mod in MO2's mods folder
    if not(os.path.exists(newDir) and os.path.isdir(newDir)):
        os.mkdir(newDir)

    # Remove old files if the setting is enabled
    if config.getboolean('SETTINGS', 'DeleteOldVersions'):   

        oldFiles = os.listdir(newDir)
        
        for file in oldFiles:
            if os.path.isfile(newDir + "\\" + file):
                if file.endswith(".zip"):
                    os.remove(newDir + "\\" + file)
                
    else:
        if os.path.exists(newDir + "\\Old Files") == False:
            os.mkdir(newDir + "\\Old Files")
        oldFiles = os.listdir(newDir)
        for file in oldFiles:
            if os.path.isfile(newDir + "\\" + file):
                shutil.move(newDir + "\\" + file, newDir + "\\Old Files")
    

    # Move or copy the downloaded zip file into the new folder based on the setting
    if config.getboolean('SETTINGS', 'KeepDownloads'):
        shutil.copy(zipPath,newDir)
    else:
        shutil.move(zipPath,newDir)
    

if __name__ == "__main__":
    # Register arguments for the script
    parser = argparse.ArgumentParser(description="VS MO2 Manager")
    parser.add_argument("--install", action="store_true", help="Install a mod to MO2 using the VSDB protocol")
    parser.add_argument("mod_data", nargs="?", help="Mod data in the format 'modID@modVersion'")
    args = parser.parse_args()

    # Check if the script is run with the --install argument
    if args.install:
        # Run the program in install mode
        if args.mod_data:
            install_mod(args.mod_data)
        else:
            print("Error: Mod data is required for installation.")
            sys.exit(1)
        
    else:
        # Run the program in GUI mode
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())

"""
TO DO:
launch MO2 with profile args
Fix windowicon
"""
