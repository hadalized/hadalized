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
    TemplateNotFound,
    select_autoescape,
)
from jinja2 import (
    Template as JinjaTemplate,
)
from loguru import logger

from hadalized.cache import Cache
from hadalized.config import BuildConfig, Config, ContextType

if TYPE_CHECKING:
    from hadalized.base import BaseNode


@cache
def get_fs_env(path: Path = Path("./templates")) -> Environment:
    """Template environment that reads from a relative directory.

    Returns:
        A jinja2.Environment with a filesystem loader.

    """
    return Environment(
        loader=FileSystemLoader(searchpath=path),
        undefined=StrictUndefined,
        autoescape=select_autoescape("html", "xml"),
    )


class Template:
    """Renders and writes templates."""

    _package_env: ClassVar[Environment] = Environment(
        loader=PackageLoader("hadalized"),
        undefined=StrictUndefined,
        # autoescape=True,
        autoescape=select_autoescape("html", "xml"),
    )
    _default_fs_env: ClassVar[Environment] = get_fs_env()

    def __init__(self, name: str, template_dir: Path | None = None):
        """Load template with the specified name."""
        fs_env = get_fs_env(template_dir) if template_dir else self._default_fs_env
        try:
            template = fs_env.get_template(name)
        except TemplateNotFound:
            template = self._package_env.get_template(name)
        self._template: JinjaTemplate = template
        self.name: str = name
        self._bytes: bytes | None = None

    def __hash__(self) -> int:
        """Hash the underlying template engine template instance.

        Returns:
            An object hash.

        """
        return hash(self._template)

    def render(self, context: BaseNode) -> str:
        """Render the template with the specified context.

        Returns:
            The rendered template that can be written to a theme file.

        """
        return self._template.render(context=context)

    def encode(self) -> bytes:
        """Encode the template source.

        Returns:
            Byte encoding of the raw, unrendered template source file.

        """
        if self._bytes is None:
            data: bytes = b"null"
            if (fname := self._template.filename) is not None:
                with suppress(FileNotFoundError):
                    data = Path(fname).read_bytes()
            self._bytes = data
        return self._bytes


class ThemeWriter:
    """Generate application theme files."""

    def __init__(self, config: Config | None = None):
        """Prepare an instance for writing files.

        Initializtion does not connect to the cache database or write
        any files.

        Args:
            config: A configuration instance if customization is required.

        """
        config = config or Config()
        self.config: Config = config
        self.cache = Cache(cache_dir=config.cache_dir, in_memory=config.cache_in_memory)
        self.build_dir: Path = self.config.build_dir
        self.palettes = list(self.config.palettes.values())

    @staticmethod
    def _hash(template: Template, context: BaseNode) -> str:
        data = template.encode() + b":::" + context.encode()
        return blake2b(data, digest_size=32).hexdigest()

    def _skip(self, path: Path, digest: str) -> bool:
        return path.exists() and self.cache.get(path) == digest

    def build(self, config: BuildConfig, output_dir: Path | None = None) -> list[Path]:
        """Generate color theme files for a specific app.

        Returns:
            A list of theme file paths that were built.

        """
        template = Template(config.template, self.config.template_dir)
        files_built: list[Path] = []
        match config.context_type:
            case ContextType.palette:
                context_nodes = self.palettes
            case ContextType.full:
                context_nodes = [self.config]

        logger.info(f"Handling themes for {config.name}.")
        for node in context_nodes:
            path = self.build_dir / config.format_path(node)
            context = node.to(config.color_type)
            digest = self._hash(template, context)

            # Render and write theme file.
            if not self._skip(path, digest):
                path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"Writing {path}.")
                path.write_text(template.render(context), encoding="utf-8")
                self.cache.add(path, digest)
                files_built.append(path)
            elif self.config.verbose:
                logger.info(f"Skip write {path} with hash {digest}.")

            # Copy built theme file.
            if output_dir is not None:
                copy_path = (output_dir / path.name).absolute()
                if not self._skip(copy_path, digest):
                    logger.info(f"Copying {path.name} to {output_dir}")
                    output_dir.mkdir(parents=True, exist_ok=True)
                    path.copy(copy_path)
                    self.cache.add(copy_path, digest)
            elif self.config.verbose:
                logger.info(f"Skip copy {path} to {output_dir}.")

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
        self.cache.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close cache db connection."""
        if exc_type is not None:
            logger.error((exc_type, exc_value, traceback))
        self.cache.close()
