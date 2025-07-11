from PyQt6.QtCore import QDir
from ..basic_game import BasicGame
import os

class VintageStoryGame(BasicGame):
    Name = "Vintage Story Support Plugin"
    Author = "Qwerdo"
    Version = "1.1"
    
    GameName = "Vintage Story"
    GameShortName = "VintageStory"
    GameBinary = "Vintagestory.exe"
    GameDataPath = "Mods"
    GameDocumentsDirectory = os.getenv("APPDATA") + "/VintagestoryData"
