# Theming and Appearance Customization

Grok Build's TUI is fully themeable. All colors flow from a central `Theme` struct -- there are no hardcoded colors anywhere in the renderer. You can switch themes on the fly, customize every aspect of the scrollback layout, and fine-tune animations and block styling through configuration files.

---

## Available Themes

Grok ships with four built-in themes:

| Theme | Config Names | Description | Truecolor Required |
|-------|-------------|-------------|--------------------|
| **GrokNight** | `groknight`, `grok-night`, `dark` | Neutral gray base with accent colors. Default theme. Survives quantization cleanly on 256-color and 16-color terminals. | No |
| **GrokDay** | `grokday`, `grok-day`, `light`, `day` | Light theme designed for bright terminal backgrounds. | No |
| **TokyoNight** | `tokyonight`, `tokyo-night`, `tokyo` | Blue-tinted backgrounds inspired by the Tokyo Night color scheme. Loses its character when quantized. | Yes |
| **RosePineMoon** | `rosepine`, `rose-pine`, `rosepine-moon`, `rose-pine-moon` | Warm, muted palette from the Rose Pine color family. | Yes |

Theme names are case-insensitive.

---

## Switching Themes

### In the TUI

Use the `/theme` slash command to open a live preview picker. As you navigate through themes, the TUI updates in real time. Press Enter to commit your choice (persisted to disk) or Escape to cancel.

### Via Config File

Set the theme in `~/.grok/config.toml`:

```toml
[ui]
theme = "tokyonight"
```

### Via CLI Flag

Start with the light theme:

```bash
grok --light
```

---

## Auto Theme (System Appearance)

Set `theme = "auto"` to have Grok follow your operating system's light/dark appearance and switch themes automatically:

```toml
[ui]
theme = "auto"
```

By default, dark mode maps to **GrokNight** and light mode maps to **GrokDay**. Override either mapping with `auto_dark_theme` and `auto_light_theme`:

```toml
[ui]
theme = "auto"
auto_dark_theme = "tokyonight"
auto_light_theme = "grokday"
```

`theme = "system"` is an alias for `theme = "auto"`.

### How Detection Works

| Platform | Method |
|----------|--------|
| **macOS** | Reads `AppleInterfaceStyle` system preference |
| **Linux** | Queries XDG Desktop Portal (`org.freedesktop.appearance.color-scheme`) |
| **Windows** | Reads the system personalization registry |
| **SSH / headless** | Falls back to an OSC 11 terminal background query at startup |

Once running, Grok polls for appearance changes every 5 seconds. Toggling your OS between light and dark mode takes effect within seconds without restarting.

### Via `/theme` Command

The `/theme` slash command includes an auto sub-menu where you can configure the dark/light theme pair interactively.

---

## Color Support Detection

On startup, Grok detects your terminal's color capability level:

| Level | Description | Detection |
|-------|-------------|-----------|
| **Truecolor** (24-bit) | Full RGB color. All themes render as designed. | `COLORTERM=truecolor` or equivalent terminal capability |
| **256-color** | Indexed palette. RGB values are mapped to the nearest palette entry. | Standard xterm-256color |
| **16-color** | ANSI names only. Colors are mapped to the closest ANSI color. | Basic terminal support |

### Automatic Quantization

Every theme is defined using full RGB values. At startup, `Theme::current()` quantizes all colors to match the detected capability level. This means:

- On **truecolor** terminals, colors pass through unchanged.
- On **256-color** terminals, each RGB value is mapped to the nearest indexed palette entry.
- On **16-color** terminals, colors map to ANSI names.

GrokNight and GrokDay use neutral grays that quantize cleanly. TokyoNight and RosePineMoon use distinctive tinted backgrounds that lose their character when quantized, which is why they are hidden from the theme picker on non-truecolor terminals.

### Runtime-Generated Colors

Colors generated at runtime (syntax highlighting, background blending) are also quantized through the same pipeline, ensuring consistent appearance across all terminal types.

---

## Cursor Color

Grok automatically sets your terminal cursor color to the current theme's `accent_user` color using the OSC 12 escape sequence. This provides a subtle visual indicator that you are in a Grok session. The cursor color is:

- Applied on startup and on theme switch.
- Reset to the terminal's default on exit via OSC 112.

This works in terminals that support OSC 12 (most modern terminals).

---

## Compact Mode

Toggle compact mode with the `/compact-mode` slash command. Compact mode:

- Removes outer vertical padding (top/bottom margins become 0).
- Reduces horizontal padding to the minimum (1 column).
- Reduces top padding in the prompt area and info blocks.

The setting is persisted in `~/.grok/config.toml` under `[ui].compact_mode` and survives restarts.

This is useful on smaller screens or when you want to maximize content area.

---

## Syntax Highlighting

Each theme includes a matching `.tmTheme` file for syntax highlighting in code blocks:

- `grok-night.tmTheme` -- used by GrokNight
- `grok-day.tmTheme` -- used by GrokDay
- `tokyo-night.tmTheme` -- used by TokyoNight

The syntax highlighter automatically uses the theme file corresponding to the active theme.

---

## Deep Customization with pager.toml

For fine-grained control over the TUI appearance, create `~/.grok/pager.toml`. This file controls scrollback layout, block styling, animations, and more. All settings have sensible defaults -- you only need to specify values you want to override.

### Layout

Control viewport padding and block spacing:

```toml
[scrollback.layout]
outer_vpad = 1          # Vertical padding (top/bottom) for the viewport
outer_hpad_left = 2     # Left margin (minimum: 1)
outer_hpad_right = 2    # Right margin (minimum: 1)
block_pad_left = 2      # Padding between accent line and content
block_pad_right = 2     # Padding after content at right edge
```

### Scrollbar

```toml
[scrollback.scrollbar]
enabled = true          # Show/hide the scrollbar
gap_left = 0            # Gap between content and scrollbar (0 = adjacent)
gap_right = 0           # Gap between scrollbar and screen edge (0 = at edge)
# scrollbar_bg = "none" # Override background color (or "none" for theme default)
# scrollbar_fg = "none" # Override thumb color (or "none" for theme default)
```

### Scroll Behavior

```toml
[scrollback.scroll]
margin = 0                  # Context lines above/below selected entry (0 = edge)
min_page_fraction = 0       # Minimum scroll as % of viewport (0-100)
follow_indicator = "center" # "center" = show down-arrow, "none" = hidden
follow_auto_select = true   # Auto-select latest entry when following
follow_by_overscroll = true # Scrolling past bottom engages follow mode
anchor_on_fold = true       # Keep block header at same screen position when folding
```

### Display Options

```toml
[scrollback.display]
sticky_headers = true              # Pin user prompts as headers when scrolled past
tab_width = 4                      # Spaces per tab character (0 = pass through)
expandable_indicator = true        # Show ">" on foldable collapsed entries
expandable_indicator_char = ">"    # Character to use (default: ">")
collapsed_accent_char = "|"        # Accent for collapsed groupable blocks
dim_accent = 0.5                   # Blend factor for dimmed accents (0.0-1.0)
line_under_last_entry = false      # Horizontal line below last entry
selection_buttons = false          # Show copy/view buttons on selection box
```

### Animation

```toml
[animation]
fps = 30           # Frame rate (1-60). Higher = smoother, more CPU
wave_rows = 32     # Rows per wave cycle for accent animation
# show_fps = false # FPS counter overlay (dev feature)
```

### Block Styling: Edit Diffs

```toml
[scrollback.blocks.edit]
indent = true                   # Indent diff content
vpad = false                    # Vertical padding around diffs
expanded_by_default = true      # Start diffs expanded (false = collapsed)
hunk_separator = "..."          # Separator between hunks ("...", "---", "", etc.)
dual_line_numbers = false       # Two-column line numbers (old + new, like GitHub)
line_summary = false            # Show +N/-M line counts in header
# bg = "none"                   # Block background ("none", "light", "dark")
```

### Block Styling: Thinking/Reasoning

```toml
[scrollback.blocks.thinking]
accent_enabled = true       # Show accent line for thinking blocks
animate = true              # Animate accent line while thinking
truncated_lines = 3         # Lines to show in truncated mode
bg_blend = 0.7              # Blend factor for markdown colors (0.0-1.0)
header = true               # Show "Thinking..." header
header_bright = false       # Bright header style (vs dim/muted)
```

### Block Styling: Tool Calls

```toml
[scrollback.blocks.tool]
muted_collapsed = true     # Gray out collapsed tool calls
dim_details = true          # Dim parenthetical details (line counts, match counts)
bullet = "diamond"          # Bullet style before tool headers
```

Available bullet styles:

| Config Value | Character | Description |
|-------------|-----------|-------------|
| `none` | (nothing) | No bullet |
| `dot` | `*` | Middle dot (smallest) |
| `small-circle` | bullet | Bullet character |
| `circle` | filled circle | Filled circle |
| `small-triangle` | small triangle | Right-pointing small triangle |
| `triangle` | triangle | Right-pointing triangle |
| `diamond` | diamond | Filled diamond (default) |

### Block Styling: Execute (Shell Commands)

```toml
[scrollback.blocks.execute]
first_lines = 2                   # Output lines shown at start in truncated mode
last_lines = 3                    # Output lines shown at end in truncated mode
accent_enabled = true             # Show accent line (animated while running)
header_style = "label"            # "shell" ($ prefix) or "label" (Run prefix)
muted_command_collapsed = true    # Mute command text when collapsed
```

### Block Styling: User Prompts (Scrollback)

```toml
[scrollback.blocks.prompt]
vpad = true            # Vertical padding
invert = false         # Inverted text style
bg = "light"           # Background ("none", "light", "dark")
show_prefix = true     # Show the prompt prefix character
min_lines = 2          # Minimum content lines in truncated/sticky mode
```

### Prompt Input Widget

```toml
[prompt]
collapse_unfocused = true    # Collapse when scrollback is focused
mouse_hover = true           # Show hover highlight on mouse over
show_prefix = true           # Show the prompt prefix character
```

### Todo Badges

```toml
[todo]
badge_format = "default"   # "default" = [1 2 3 4], "colon" = [>:1 #:4], "comma" = [1 >, 4 #]
```

### Terminal Behavior

```toml
[terminal]
alt_screen = "auto"    # "auto", "always", or "never"
```

Alt-screen policies:
- `auto` -- fullscreen in plain terminals and normal tmux; inline in tmux control mode and Zellij.
- `always` -- always enter fullscreen.
- `never` -- never enter fullscreen; run inline in the main scrollback.

### Plugins UI

```toml
disable_plugins = false   # Set to true to hide /hooks, /plugins commands and annotations
```

---

## Theme Color Slots

Each theme defines the following color slots that are used throughout the TUI:

**Backgrounds:** `bg_base`, `bg_light`, `bg_dark`, `bg_highlight`, `bg_hover`, `bg_terminal`

**Accents:** `accent_user`, `accent_assistant`, `accent_thinking`, `accent_tool`, `accent_system`, `accent_error`, `accent_success`, `accent_running`, `accent_skill`, `accent_plan`, `accent_feedback`, `accent_model`

**Text:** `text_primary`, `text_secondary`

**Grays:** `gray_dim`, `gray`, `gray_bright`

**Semantic:** `command`, `path`, `running`, `warning`, `fuzzy_accent`

**Diff:** `diff_delete_bg`, `diff_delete_fg`, `diff_insert_bg`, `diff_insert_fg`, `diff_equal_fg`, `diff_gutter_fg`

**Markdown:** heading colors (h1-h6), `md_code`, `md_code_bg`, `md_text`, `md_muted`, task check colors

These are all managed internally by the theme system and quantized automatically for your terminal.
