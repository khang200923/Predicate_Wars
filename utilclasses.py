# This file is part of Predicate Wars.

# Predicate Wars is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.

# Predicate Wars is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with Predicate Wars. If not, see <https://www.gnu.org/licenses/>.
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
