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


@cache
def _encode(val: Template | BaseNode) -> bytes:
    if isinstance(val, Template):
        data: bytes = b"null"
        if (fname := val.filename) is not None:
            with suppress(FileNotFoundError):
                data = Path(fname).read_bytes()
    else:
        data = val.model_dump_json().encode()

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

    def __init__(self, config: Config | None = None):
        """Prepare an instance for writing files.

        Initializtion does not connect to the cache database or write
        any files.

        Args:
            config: A configuration instance if customization is required.

        """
        config = config or Config()
        self.config = config
        self.cache = Cache(cache_dir=config.cache_dir, in_memory=config.cache_in_memory)
        self.build_dir: Path = self.config.build_dir
        self._fs_template_env = Environment(
            loader=FileSystemLoader(searchpath=self.config.template_dir),
            undefined=StrictUndefined,
            autoescape=select_autoescape("html", "xml"),
        )
        self._parsed = False

    def _skip(self, path: Path, digest: str) -> bool:
        return (
            not self.config.disable_cache
            and path.exists()
            and self.cache.get(path) == digest
        )

    def get_template(self, name: str) -> Template:
        """Load theme template.

        Returns:
            A jinja2.Template instance.

        """
        try:
            template = self._fs_template_env.get_template(name)
        except TemplateNotFound:
            template = self._package_template_env.get_template(name)
        return template

    def _parse(self):
        """Parse each palette in the underlying configuration."""
        if not self._parsed:
            self.config = self.config.parse_palettes()
            self._parsed = True

    def build(self, config: BuildConfig, output_dir: Path | None = None) -> list[Path]:
        """Generate color theme files for a specific app.

        Returns:
            A list of theme file paths that were built.

        """
        self._parse()
        template = self.get_template(config.template)
        files_built: list[Path] = []
        match config.context_type:
            case ContextType.palette:
                context_nodes = self.config.palettes.values()
            case ContextType.full:
                context_nodes = [self.config]

        logger.info(f"Handling themes for {config.name}.")
        for node in context_nodes:
            relpath = config.format_path(node)
            path = self.build_dir / relpath
            context = node.to(config.color_type)
            digest = _hash(template, context)

            # Render and write theme file.
            if not self._skip(path, digest):
                path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"Building {path} {digest}.")
                text = template.render(context=context)
                path.write_text(text, encoding="utf-8")
                if not self.config.disable_cache:
                    self.cache.add(path, digest)
                files_built.append(path)
            elif self.config.verbose:
                logger.info(f"Skip write {path} with hash {digest}.")

            # Copy built theme file.
            if output_dir is not None:
                copy_path = (output_dir / path.name).absolute()
                logger.info(f"Copying {relpath} to {output_dir}")
                output_dir.mkdir(parents=True, exist_ok=True)
                path.copy(copy_path)

        return files_built

    def run(self) -> list[Path]:
        """Generate all relevant app theme files.

        Returns:
            A list of file paths that were generated.

        """
        written = []
        for directive in self.config.builds.values():
            written += self.build(directive)
        return written

    def __enter__(self):
        """Connect to the cache db.

        Returns:
            The instance with a connection to the cache db.

        """
        if not self.config.disable_cache:
            self.cache.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close cache db connection."""
        if exc_type is not None:
            logger.error((exc_type, exc_value, traceback))
        if not self.config.disable_cache:
            self.cache.close()
