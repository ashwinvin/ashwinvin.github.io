import argparse
import os
import shutil
from markdown_it import MarkdownIt

from string import Template
from pathlib import Path

md_renderer = MarkdownIt("gfm-like")

template_cache = {}

def prepare_file_name(file: Path):
    return file.stem.lower().replace(" ", "_") + ".html"

def get_directories(template_dir: Path, src_dir: Path):
    templates_found = [file.stem for file in  template_dir.glob("*.html")]
    for folder in src_dir.iterdir():
        if folder.name in templates_found:
            yield folder

def recurse_directory(directory_path: Path):
    for file in directory_path.iterdir():
        if file.is_dir():
            yield from recurse_directory(file)
        yield file

def render(file_path: Path, template_path: Path):
    mapping = {}

    rendered_md = md_renderer.render(file_path.read_text())
    mapping["content"] = rendered_md
    
    if (style_file := template_path.with_suffix(".css")).exists():
        mapping["style"] = f'<link rel="stylesheet" href="/assets/{style_file.name}">'

    if template_path.name not in template_cache:
        template_cache[template_path.name] = template_path.read_text()

    return Template(template_cache[template_path.name]).safe_substitute(mapping)

def build(template_dir: Path, src_dir: Path, output_dir: Path, assets_dir: Path):
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    # Copy html files directly to output directory
    for file in src_dir.iterdir():
        if file.is_file():
            shutil.copy(file, output_dir / file.name)

    # Copy assets to output directory
    shutil.copytree(assets_dir, output_dir / assets_dir.name, dirs_exist_ok=True)

    for directory in get_directories(template_dir, src_dir):
        template_path = (template_dir / directory.name).with_suffix(".html")

        for file in recurse_directory(directory):
            # Find the directory structure
            _file_dir_parent = os.path.sep.join(file.parts[len(src_dir.parts): -1])
            temp_out_dir = output_dir / _file_dir_parent
            if not temp_out_dir.exists():
                temp_out_dir.mkdir(parents=True)

            contents = render(file, template_path)
            (temp_out_dir / prepare_file_name(file) ).write_text(contents)

        # Copy template style file to output directory
        if (style_file := template_path.with_suffix(".css")).exists():
            shutil.copy(style_file, output_dir / assets_dir.name / style_file.name)

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser("Basic Static Site Generator")
    arg_parser.add_argument("--src-dir",help="Path to directory containing source files")
    arg_parser.add_argument("--assets-dir",help="Path to directory containing assets")
    arg_parser.add_argument("--templates-dir",help="Path to directory containing template files")
    arg_parser.add_argument("--build-dir",help="Path to output directory")
    
    args = arg_parser.parse_args()

    src_dir = Path(args.src_dir).absolute()
    assets_dir = Path(args.assets_dir).absolute()
    template_dir = Path(args.templates_dir).absolute()
    build_dir = Path(args.build_dir).absolute()

    build(template_dir, src_dir, build_dir, assets_dir)