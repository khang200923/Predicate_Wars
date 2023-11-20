from typing import Any, Callable

class LazyDict(dict):
    """
    Lazy dictionary with generation of nonexistent pairs when accessed.
    """
    def __init__(self, generation: Callable[[Any], Any] | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generation = generation
    def __getitem__(self, __key: Any) -> Any:
        try:
            return super().__getitem__(__key)
        except KeyError:
            super().__setitem__(__key, self.generation(__key))
            return super().__getitem__(__key)
