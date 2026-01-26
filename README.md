# hadalized

## Introduction

Python package and cli application to build hadalized theme files for different
applications.

The underlying [hadalized palettes](./src/hadalized/config.py)
are defined as oklch color values. Application theme templates are rendered
with the appropriate color type (e.g., hex values for neovim). Under the hood
the `coloraide` python package is used to transform between colorspaces and fit
to gamuts.

Creating a theme builder arises from the desire to use the OKLCH color space
as the basis for any application color theme. When developing the palette, it
quickly becomes tedius to manually convert oklch values to their hex
equivalents.

The builder primarily targets the neovim colorscheme files in
[hadalized.nvim](https://github.com/shawnohare/hadalized.nvim)


## Example CLI Usage

Assuming `uv` is installed,

```sh
uv run --exact hadalized build --out="./build"
```
will produce rendered theme files for all builtin applications in `./build`.


## Development

Assuming `uv` and `just` are installed

```sh
uv sync --locked
source .venv/bin/evaluate
# make changes
just fmt
just check
just test
# commit changes
```

## Roadmap

- [x] Introduce proper cli as main entry point. (Done in v0.3 via cyclopts).
- [x] Add targetted builds. For example, specify that only "neovim" themes are
  built. (Done in v0.3)
- [ ] Create example of a custom python config, e.g., for adding an app that
  is not supported in the builtin builds.
- [ ] (?) Allow specifying a configuration file (py or toml) to pass to cli.
  This might imply using BaseSettings. The current setup assumes a python
  configuration file.

