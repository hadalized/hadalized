"""Base container for all model classes."""

from typing import ClassVar, Self

from pydantic import PrivateAttr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    # TomlConfigSettingsSource,
)

from hadalized.const import APP_NAME, APP_VERSION


class BaseNode(BaseSettings):
    """An extension of BaseSettings that all model classes inherit.

    Unless overriden, by default only initialization settings are respected.

    Full setting sources are exposed in the ``UserConfig`` subclass.
    """

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        frozen=True,
        extra="forbid",
    )

    _hash: int | None = PrivateAttr(default=None)
    """Cached hash computation so that instances can be passed to cached
    functions and used in dicts."""

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Set source loading priority.

        Returns:
            Priority order in which config settings are loaded.

        """
        return (init_settings,)

    @property
    def app_info(self) -> str:
        """App name and version."""
        return f"{APP_NAME} v{APP_VERSION}"

    def model_dump_lua(self) -> str:
        """Dump the model as a lua table.

        Returns:
            A human readable lua table string.

        """
        import luadata

        # TODO: Unclear if we want to import luadata just for this
        return luadata.serialize(self.model_dump(mode="json"), indent="  ")

    def replace(self, **kwargs) -> Self:
        """Create a new instance with input arguments merged in.

        Returns:
            A new instance.

        """
        return self.model_validate(self.model_dump() | kwargs)

    def encode(self) -> bytes:
        """Encode the data structure json dump.

        Returns:
            A byte encoding of the model to pass into built hash proxy.

        """
        return self.model_dump_json().encode()

    def __getitem__(self, key: str):
        """Provide dict-like lookup for all models.

        Returns:
            The field specified by the input key.

        """
        return getattr(self, key)

    def __hash__(self) -> int:
        """Make an instance hashable for use in cache and dict lookups.

        Defined for type checking purposes. Frozen models are hashable.

        Returns:
            The BaseModel hash.

        """
        if self._hash is None:
            self._hash = hash(self.model_dump_json())
        return self._hash

    def __len__(self) -> int:
        """Report the number of model fields.

        Returns:
            The length of the set of model fields.

        """
        return len(self.__class__.model_fields)

    def __or__(self, other: BaseNode) -> Self:
        """Shallow merge explicitly set fields.

        Only the explicitly set fields of ``other`` are merged in.

        Args:
            other: An instance of the same type or parent type to ``self``.

        Returns:
            A new instance with the set fields of `other` merged in.

        """
        merged = self.model_dump(exclude_unset=True) | other.model_dump(
            exclude_unset=True
        )
        return self.model_validate(merged)

    # def merge(self, parent: BaseNode) -> Self:
    #     """Shallow merge a parent instance.
    #
    #     Args:
    #         parent: A model with a subset of the fields defined in the
    #             instance.
    #
    #     Returns:
    #         A new instance of the same type as the instance with the set
    #         parent fields.
    #
    #     """
    #     merged = self.model_dump() | parent.model_dump(exclude_unset=True)
    #     return self.model_validate(merged)
