# hadalized color theme build

Python package with CLI to build hadalized-style application themes.

## Introduction

The application can build any theme conforming to the hadalized `Palette`
schema for any application with a `BuildConfig` and appropriate theme
template.

The builtin [hadalized color palettes](./src/hadalized/colors.py)
are defined as oklch color values. Application theme templates are rendered
with the appropriate color type (e.g., hex values for neovim). Under the hood
the `coloraide` python package is used to transform between colorspaces and fit
to gamuts.

Creating a theme builder arises from the desire to use the OKLCH color space
as the basis for any application color theme. When developing the palette, it
quickly becomes tedius to manually convert oklch values to their hex
equivalents.

The builder primarily targets the neovim colorscheme files in
[hadalized.nvim](https://github.com/shawnohare/hadalized.nvim), as that is
the editor we primarily use.

## Example CLI Usage

Assuming `uv` is installed,

```sh
uv run --exact hadalized build --out="build"
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

## Roadmap / TODOs

- [ ] Consider removing the "in-memory" cache functionality.
- [ ] (A) Add ability to map named colors such as `red` to an abstracted name
  such as `color1`, similar to `base16`. Use these abstracted names color theme
  templates. This might be painful to work with in practice, as one has to keep
  the mapping in their head.
- [ ] (B) As an extension of (A), consider lightweight pandoc inspired features
  where an intermediate and generic theme can be defined and referenced in
  editor templates. For example, allow a user to define `integer = "blue"` and
  reference `theme.integer` to color neovim `Integer` highlight groups.
