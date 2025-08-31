import argparse
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from jinja2 import DictLoader, Environment, select_autoescape

from parser import CategoryManager


@dataclass
class Builder:
    source_dir: Path
    template_dir: Path
    output_dir: Path
    assets_dir: Path

    def prepare(self):
        category_managers: list[CategoryManager] = []
        template_store = {}

        template_renderer = Environment(
            loader=DictLoader(template_store), autoescape=select_autoescape()
        )

        for file in self.template_dir.glob("*.html"):
            template_store[file.stem] = file.read_text()
        
        for category_dir in self.source_dir.iterdir():
            if not category_dir.is_dir():
                continue

            if manager := CategoryManager.create(category_dir, self.assets_dir):
                category_managers.append(manager)

        # Base files must be html (for now)
        base_files = [file for file in self.source_dir.iterdir() if file.is_file()]

        logging.info("Found %d categories", len(category_managers))
        logging.info("Found %d base files", len(base_files))
        logging.info("Found %d templates", len(template_store))

        for file in base_files:
            template_store[file.name] = file.read_text()

        return template_renderer, category_managers, base_files

    def build(self):
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True)

        template_renderer, templates, base_files = self.prepare()

        mappings = {}
        mappings["category_links"] = {
            template.name: template.link for template in templates
        }
        mappings["base_links"] = {
            file.stem.capitalize(): "/" + file.name for file in base_files
        }

        shutil.copytree(self.assets_dir, self.output_dir / "assets", dirs_exist_ok=True)

        # Render base files
        for file in base_files:
            template = template_renderer.get_template(file.name)
            content = template.render(mappings)
            output_path = self.output_dir / file.name
            output_path.write_text(content)
        logging.info("Finished rendering base files")

        for manager in templates:
            # Copy template style files to assets folder
            if manager.style_file:
                shutil.copy(manager.style_file, self.output_dir / "assets" / manager.style_file.name)

            for file in manager.render_files(template_renderer, mappings):
                output_path = self.output_dir / file.output_path
                # write_text fn fails if the parent folders doesn't exist
                if not output_path.parent.exists():
                    output_path.parent.mkdir(parents=True)

                output_path.write_text(file.contents)
        logging.info("Build complete. Output files written to %s", self.output_dir)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser("Basic Static Site Generator")
    arg_parser.add_argument(
        "--src-dir", help="Path to directory containing source files"
    )
    arg_parser.add_argument("--assets-dir", help="Path to directory containing assets")
    arg_parser.add_argument(
        "--templates-dir", help="Path to directory containing template files"
    )
    arg_parser.add_argument("--output-dir", help="Path to output directory")

    args = arg_parser.parse_args()

    src_dir = Path(args.src_dir).absolute()
    assets_dir = Path(args.assets_dir).absolute()
    template_dir = Path(args.templates_dir).absolute()
    output_dir = Path(args.output_dir).absolute()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    builder = Builder(src_dir, template_dir, output_dir, assets_dir)
    builder.build()
