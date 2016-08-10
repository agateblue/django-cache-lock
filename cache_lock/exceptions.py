class ConcurrentModificationError(ValueError):
    """Base error class for write concurrency errors"""
    pass


class StaleWrite(ConcurrentModificationError):
    """Tried to write a version of a model that is older than the current version in the database"""
    pass


class AlreadyLocked(ConcurrentModificationError):
    """Tried to aquire a lock on a row that is already locked"""
    pass


class WriteWithoutLock(ConcurrentModificationError):
    """Tried to save a lock-required model row without locking it first"""
    pass

class InvalidLock(ValueError):
    """Tried to acquire a lock on an unlockable value"""
    pass
