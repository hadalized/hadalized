# hadalized

## Introduction

Python package and application to build hadalized theme files for different
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


## Usage

Assuming `uv` is installed,

```sh
uv run --exact hadalized`
```
will produce rendered theme files in `./build`.


## Roadmap

- [ ] Introduce proper cli entry point rather than simply running a function.
  This may or may not be a separate python package utilizing `uv` workspaces.
- [ ] Add targetted builds. For example, specify that only "neovim" themes are
  built.


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
