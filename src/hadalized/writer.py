"""Render templates and write outputs."""

from contextlib import suppress
from functools import cache
from hashlib import blake2b
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from jinja2 import (
    Environment,
    FileSystemLoader,
    PackageLoader,
    StrictUndefined,
    Template,
    TemplateNotFound,
    select_autoescape,
)
from loguru import logger

from hadalized import const
from hadalized.cache import Cache
from hadalized.config import BuildConfig, Config, ContextType

if TYPE_CHECKING:
    from hadalized.base import BaseNode
    from hadalized.palette import Palette


@cache
def _encode(val: Template | BaseNode) -> bytes:
    if isinstance(val, Template):
        data: bytes = b"null"
        if (fname := val.filename) is not None:
            with suppress(FileNotFoundError):
                data = Path(fname).read_bytes()
    else:
        data = val.encode()

    return data


def _hash(template: Template, context: BaseNode) -> str:
    data = _encode(template) + b":::" + _encode(context)
    return blake2b(data, digest_size=32).hexdigest()


class ThemeWriter:
    """Generate application theme files."""

    _package_template_env: ClassVar[Environment] = Environment(
        loader=PackageLoader(const.APP_NAME),
        undefined=StrictUndefined,
        # autoescape=True,
        autoescape=select_autoescape("html", "xml"),
    )

    def __init__(self, config: Config):
        """Prepare an instance for writing files.

        Initializtion does not connect to the cache database or write
        any files.

        Args:
            config: A configuration instance if customization is required.

        """
        self.config = config
        self.cache = Cache(config)
        self._fs_template_env = Environment(
            loader=FileSystemLoader(searchpath=config.template_dir),
            undefined=StrictUndefined,
            autoescape=select_autoescape("html", "xml"),
        )
        self._parsed = False

    def _skip(self, path: Path, digest: str) -> bool:
        return (
            not self.config.force
            and not self.config.no_cache
            and path.exists()
            and self.cache.get(path) == digest
        )

    def get_template(self, name: str | Path) -> Template:
        """Load theme template.

        Returns:
            A jinja2.Template instance.

        """
        tname = str(name)
        if self.config.no_templates or self.config.no_config:
            template = self._package_template_env.get_template(tname)
        else:
            try:
                template = self._fs_template_env.get_template(tname)
            except TemplateNotFound:
                template = self._package_template_env.get_template(tname)
        return template

    def _parse(self):
        """Parse each palette in the underlying configuration."""
        if not self._parsed:
            self.config = self.config.parse_palettes()
            self._parsed = True

    def build_file(
        self,
        bconf: BuildConfig,
        data: Palette | Config,
    ) -> tuple[Path, bool]:
        """Build a single color theme file.

        Returns:
            A path of the built file and whether it was generated.

        """
        opt = self.config
        template = self.get_template(bconf.template)
        path = self.config.build_dir / bconf.format_path(data)
        context = data.to(bconf.color_type)
        digest = _hash(template, context)

        if opt.verbose:
            logger.info(f"Checking whether to build {path} with hash {digest}.")
        if self._skip(path, digest):
            return path, False

        if not opt.quiet:
            logger.info(f"Building {path} {digest}.")

        text = template.render(context=context)
        if not opt.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        if opt.use_cache and not opt.dry_run:
            self.cache.add(path, digest)
        return path, True

    def copy_file(self, build_path: Path) -> Path | None:
        """Copy a built theme file to an output directory.

        Args:
            build_path: Path to a built theme file, typically saved in
                the applicate state directory.

        Returns:
            The path of the copied file or None if no copy was performed.

        """
        opt = self.config
        if opt.output_dir is None:
            return None

        output_dir = opt.output_dir
        if opt.prefix:
            output_dir /= build_path.parent.name
        copy_path = (output_dir / build_path.name).absolute()
        if not opt.quiet:
            logger.info(f"Copying {build_path} to {output_dir}")
        if not opt.dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            build_path.copy(copy_path)
        return copy_path

    def build(self, bconf: BuildConfig) -> list[Path]:
        """Generate color theme files for a specific app.

        Args:
            bconf: A configuration specifying how theme files shoud be built.

        Returns:
            A list of theme file paths that were built.

        """
        self._parse()
        opt = self.config
        if opt.verbose:
            logger.info(f"Handling themes for {bconf.name}.")
        includes = set(opt.include_palettes)
        filtered_palettes = {
            k: v
            for k, v in opt.palettes.items()
            if not includes
            or k in includes
            or v.name in includes
            or not set(v.aliases).isdisjoint(includes)
        }

        match bconf.context_type:
            case ContextType.palette:
                contexts = filtered_palettes.values()
            case ContextType.full:
                if not includes:
                    contexts = [self.config]
                else:
                    contexts = [self.config.replace(palettes=filtered_palettes)]

        files_built: list[Path] = []
        for item in contexts:
            build_path, is_built = self.build_file(bconf, item)
            if is_built:
                files_built.append(build_path)
            self.copy_file(build_path)

        return files_built

    def run(self) -> list[Path]:
        """Generate all relevant app theme files.

        Returns:
            A list of file paths that were generated.

        """
        includes = set(self.config.include_builds)
        builds = (
            v
            for k, v in self.config.builds.items()
            if not includes or k in includes or v.name in includes
        )

        written = []
        for directive in builds:
            written += self.build(directive)
        return written

    def __enter__(self):
        """Connect to the cache.

        Returns:
            The instance with a connection to the cache db.

        """
        if self.config.use_cache:
            self.cache.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close cache db connection."""
        if exc_type is not None:
            logger.error((exc_type, exc_value, traceback))
        if self.config.use_cache:
            self.cache.close()
