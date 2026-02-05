"""Check the basic features work.

Catch cases where e.g. files are missing so the import doesn't work. It is
recommended to check that assets are included.
"""

from hadalized.config import Options, load_config
from hadalized.writer import ThemeWriter

config = load_config(Options(no_config=True))
palette = config.get_palette("hadalized")
template = ThemeWriter(config).get_template("neovim.lua")
if not template:
    raise RuntimeError("Unable to load builtin template.")
else:
    print("Smoke test successful.")
