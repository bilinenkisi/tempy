class BaseException(Exception):
  pass
class NotOverridableTempDirectoryException(Exception):
  """raise: when the folder is already exists"""