from typing import List
from pathlib import Path
import mobase, shutil, sys

class MyPlugin(mobase.IPluginInstallerCustom):  # The base class depends on the actual type of plugin

    

    def __init__(self):
        super().__init__()  # You need to call this manually.

    def init(self, organizer: mobase.IOrganizer):
        self._organizer = organizer
        return True

    def name(self) -> str:
        print("test")
        return "VS Archive Installer"
    
    def displayName(self) -> str:
        return "VS Archive Installer"
    
    def author(self) -> str:
        return "Qwerdo"

    def description(self) -> str:
        return ("Installs archives without extracting them. ")

    def version(self) -> mobase.VersionInfo:
        return mobase.VersionInfo(1, 0, 0, mobase.ReleaseType.FINAL)

    def isActive(self) -> bool:
        return self._organizer.pluginSetting(self.name(), "enabled")

    def settings(self) -> List[mobase.PluginSetting]:
        return [
            mobase.PluginSetting("enabled", "enable this plugin", True)
        ]
    
    def priority(self) -> int:
        return 1000
    # Required method: Specify supported file extensions
    def supportedExtensions(self) -> set[str]:
        return {"zip"}
    def isArchiveSupported(self, tree) -> bool:
        # Check if the archive is a zip file
        
        return True
    
    # Required method: Define installation logic
    def install(self, mod_name, game_name:str, archive_name:str, version:str,nexus_id:int) -> mobase.InstallResult:
        
        

        # Get the mods directory from the organizer
        mods_directory = Path(self._organizer.modsPath())
        new_mod_directory = mods_directory.__str__() +'\\' + mod_name.__str__()

        try:
            # Create the mod directory if it doesn't exist
            Path.mkdir(new_mod_directory, parents=True, exist_ok=True)

            # Copy the archive to the mod directory
            archive_path = Path(archive_name)
            shutil.copy(archive_path, new_mod_directory + "\\" + archive_path.name)

            # Return success
            return mobase.InstallResult.SUCCESS

        except Exception as e:
            # Return failure
            return mobase.InstallResult.FAILED










def createPlugin() -> mobase.IPluginInstallerCustom:
    return MyPlugin()