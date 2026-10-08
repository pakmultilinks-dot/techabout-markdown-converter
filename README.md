# Markdown Converter

A script that converts a Markdown file into a styled HTML page.
Standard library only, no third-party packages. Built for TechAbout
task 9 (ZR-26-00754).

## What it does

Reads a `.md` file and produces a complete, self-contained HTML page
(with embedded CSS, no external files). Supported Markdown:

- Headings `#` through `######`
- **Bold**, *italic*, and `inline code`
- Links `[text](url)` and images `![alt](url)`
- Fenced code blocks (```) with optional language label
- Unordered (`-`) and ordered (`1.`) lists
- Blockquotes (`>`) and horizontal rules (`---`)
- Paragraphs separated by blank lines

Raw HTML in the input is escaped, so it can never break the page.

## Usage

```bash
python markdown_converter.py notes.md --output notes.html
python markdown_converter.py notes.md --output notes.html --title "My Notes"
python markdown_converter.py notes.md   # prints HTML to stdout
```

The page title defaults to the document's first heading.

## Sample files

`sample/demo.md` is a demo document exercising every feature;
`sample/demo.html` is the converted page. Open it in any browser.

## Tests

```bash
python test_markdown_converter.py
```

17 tests covering headings, paragraphs, bold/italic, inline code
(including protection of markup inside code spans), links, images,
fenced code blocks, both list types, blockquotes, horizontal rules,
HTML escaping, formatting inside headings, page structure, and empty
input.

## Files

| File | Purpose |
|---|---|
| `markdown_converter.py` | The script |
| `test_markdown_converter.py` | 17 unit tests |
| `sample/demo.md` | Sample Markdown input |
| `sample/demo.html` | Sample HTML output |
