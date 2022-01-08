from io import FileIO
import os, atexit
import tempfile, hashlib
import shutil
from typing import Union, overload
from filelock import Timeout, FileLock
import enum
from tempy.exceptions import NotOverridableTempDirectoryException

TEMPDIR = tempfile.gettempdir()
PROCESS_SEED = os.getpid()
class OverrideProtectionMethods(enum.Enum):
  ERROR = 0
  REMOVE = 1
  NONE = 2
class TempDir(object):
    @overload
    def __init__(self, seed: int = PROCESS_SEED,*, override_protection: OverrideProtectionMethods = OverrideProtectionMethods.ERROR) ->"TempDir":
        ...
    @overload
    def __init__(self,seed:str = ...,*, override_protection: OverrideProtectionMethods = OverrideProtectionMethods.ERROR) ->"TempDir":
        ...
    @overload
    def __init__(self, seed: int = PROCESS_SEED,*, override_protection: OverrideProtectionMethods = OverrideProtectionMethods.ERROR,parent:"TempDir") ->"TempDir":
        """__init__ to initialize a child temp directory by using seed"""
        ...
    @overload
    def __init__(self, seed: str = ...,*, override_protection: OverrideProtectionMethods = OverrideProtectionMethods.ERROR,parent:"TempDir"=...) ->"TempDir":
        """__init__ to initialize a child temp directory by name"""
        ...
    def __init__(self, seed = ...,*, override_protection: OverrideProtectionMethods = OverrideProtectionMethods.ERROR,parent:"TempDir"=None) ->"TempDir":
        seed = seed or PROCESS_SEED
        self.__parent = parent
        self.__lock = None
        self.__seed = seed if isinstance(seed,str) else hashlib.md5((self.__parent.seed+str(seed)).encode()).hexdigest() if self.__parent else hashlib.md5((str(seed)).encode()).hexdigest()
        self.__temp_dir = os.path.join(self.parent.directory, self.seed) if self.__parent else os.path.join(TEMPDIR, self.seed)
        self.__open_files = []
        self.__exit_called = False
        self.__override_protection = override_protection
        atexit.register(self.__exit__, ..., ..., ...)
        if os.path.exists(self.__temp_dir):
            if self.__override_protection == OverrideProtectionMethods.ERROR:
                
                raise NotOverridableTempDirectoryException(
                    f"'{self.__temp_dir}' is already exists!"
                )
            elif self.__override_protection == OverrideProtectionMethods.REMOVE:
              shutil.rmtree(self.__temp_dir)
              os.mkdir(self.__temp_dir)
            elif self.__override_protection == OverrideProtectionMethods.NONE:
              ...
        else:
            os.mkdir(self.__temp_dir)

        if not os.path.exists(os.path.join(self.__temp_dir, ".lock")):
            self.__lock = FileLock(os.path.join(self.__temp_dir, ".lock"))
            self.__lock.acquire()
    
    
    @property
    def parent(self):
      return self.__parent
    @property
    def directory(self):
        return self.__temp_dir

    @property
    def seed(self):
        return self.__seed

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__exit_called:
            return
        self.__exit_called = True
        file: FileIO
        for file in self.__open_files:
            if file.closed:
                os.remove(file.name)
                self.__open_files.remove(file)
            else:
                file.close()
                os.remove(file.name)
                self.__open_files.remove(file)
        if self.__lock:

            self.__lock.release()
            shutil.rmtree(self.__temp_dir)

    def close(self):
        self.__exit__(..., ..., ...)

    def open(self, path, *args, **kwargs):
        file = open(os.path.join(self.__temp_dir, path), *args, **kwargs)
        self.__open_files.append(file)
        return file

    def mkdir(self,*,name: str=...):
      if name:
        return TempDir(name,parent=self)
    
