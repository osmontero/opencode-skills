# opencode-skills

A collection of 17 skills for [opencode](https://opencode.ai), an interactive CLI tool for software engineering tasks. Each skill provides specialized instructions, scripts, and resources that opencode loads when the task matches the skill's domain.

## Installation

Copy or symlink the `skills/` directory into your opencode skills location:

```bash
# Option 1: Copy
cp -r /path/to/opencode-skills/skills/* ~/.config/opencode/skills/

# Option 2: Symlink individual skills
ln -s /path/to/opencode-skills/skills/docx ~/.config/opencode/skills/docx

# Option 3: Clone and update skills path
git clone https://github.com/yourusername/opencode-skills.git
cd opencode-skills
cp -r skills/* ~/.config/opencode/skills/
```

The `common/` directory contains shared utilities used by multiple skills. If you use the copy approach above, these will be included naturally since the skill SKILL.md files reference `../../common/scripts/office/` relative to each skill. If installing from this repo, place the entire repo such that the relative paths resolve correctly, or copy both `skills/` and `common/` into `~/.config/opencode/`:

```bash
cp -r skills ~/.config/opencode/
cp -r common ~/.config/opencode/
```

## Skills

| Skill | Description |
|-------|-------------|
| [algorithmic-art](skills/algorithmic-art/) | Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration |
| [brand-guidelines](skills/brand-guidelines/) | Applies your organization's brand colors and typography to any artifact |
| [canvas-design](skills/canvas-design/) | Create beautiful visual art in .png and .pdf documents using design philosophy |
| [claude-api](skills/claude-api/) | Build apps with the Claude API or Anthropic SDK |
| [doc-coauthoring](skills/doc-coauthoring/) | Guide users through a structured workflow for co-authoring documentation |
| [docx](skills/docx/) | Create, read, edit, or manipulate Word documents (.docx files) |
| [frontend-design](skills/frontend-design/) | Create distinctive, production-grade frontend interfaces with high design quality |
| [internal-comms](skills/internal-comms/) | Resources for writing internal communications (status reports, newsletters, FAQs, etc.) |
| [mcp-builder](skills/mcp-builder/) | Guide for creating high-quality MCP (Model Context Protocol) servers |
| [pdf](skills/pdf/) | Read, extract, merge, split, create, and manipulate PDF files |
| [pptx](skills/pptx/) | Create, read, edit, and manipulate PowerPoint presentations (.pptx files) |
| [skill-creator](skills/skill-creator/) | Create new opencode skills, modify and improve existing skills |
| [slack-gif-creator](skills/slack-gif-creator/) | Knowledge and utilities for creating animated GIFs optimized for Slack |
| [theme-factory](skills/theme-factory/) | Toolkit for styling artifacts with a theme (slides, docs, HTML, etc.) |
| [webapp-testing](skills/webapp-testing/) | Toolkit for interacting with and testing local web applications using Playwright |
| [web-artifacts-builder](skills/web-artifacts-builder/) | Suite of tools for creating elaborate multi-component HTML artifacts |
| [xlsx](skills/xlsx/) | Create, read, edit, and analyze Excel spreadsheet files (.xlsx) |

## Shared Resources

The `common/` directory contains deduplicated resources shared across multiple skills:

- `common/scripts/office/` — Office document utilities (pack, unpack, validate, soffice wrapper) shared by the `docx`, `pptx`, and `xlsx` skills

## License

Each skill may have its own license. Check the `LICENSE.txt` file within each skill directory for details.
