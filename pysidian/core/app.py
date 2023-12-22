import platform
import os
from typing_extensions import TypedDict, NotRequired
from zrcl3.singleton import SingletonMeta
from zrcl3.auto_save_dict.on_trigger import OnChangeSaveDict

class VaultCtx(TypedDict):
    path : str
    ts : int
    open : NotRequired[bool]

class ObsidianApp(metaclass=SingletonMeta):
    @property
    def roamingSettingPath(self):
        if platform.system() == "Windows":
            return os.path.join(os.getenv('APPDATA'), 'obsidian', 'obsidian.json')
        else:
            return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'obsidian', 'obsidian.json')
    
    def __init__(self):
        self.__setting = OnChangeSaveDict(self.roamingSettingPath)
        
    @property
    def setting(self):
        return self.__setting
    
obsidianApp = ObsidianApp()