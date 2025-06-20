import logging
import os
import typing
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Dict

from jinja2 import Environment
from markdown_it import MarkdownIt

md_renderer = MarkdownIt("gfm-like")


@dataclass
class RenederedTemplate:
    output_relative_path: Path
    contents: str

    @classmethod
    def create(cls, src_relative_path: Path, contents: str):
        file_name = src_relative_path.stem.lower().replace(" ", "_")
        return RenederedTemplate(
            src_relative_path.with_stem(file_name).with_suffix(".html"), contents
        )


@dataclass
class TemplateManager:
    template_name: str
    _template_path: Path
    source_dir: Path

    @classmethod
    def create(
        cls,
        template_path: Path,
        source_path: Path,
    ) -> "TemplateManager | None":
        for folder in source_path.iterdir():
            if folder.name == template_path.stem:
                return TemplateManager(
                    template_path.stem,
                    template_path.absolute(),
                    folder.absolute(),
                )

        logging.warning(
            f"Unable to find associated files for template {template_path.name}"
        )

    @staticmethod
    def _get_files(directory_path: Path):
        for file in directory_path.iterdir():
            if file.is_dir():
                yield from TemplateManager._get_files(file)
            if file.is_file():
                yield file.absolute()

    @property
    def link(self):
        return "/" + self.template_name

    @property
    def get_style_file(self) -> Path | None:
        if (style_path := self._template_path.with_suffix(".css")).exists():
            return style_path

    def get_category_links(self) -> Dict[Path, Path]:
        """
        Returns a dictionary containing links to each page as keys and their absolute path as values.
        Both the keys and values point to the source files.
        """
        page_links = {}

        for page_path in TemplateManager._get_files(self.source_dir):
            page_link = self.template_name / page_path.relative_to(self.source_dir)
            if page_link not in page_links:
                page_links[page_link] = page_path

        return page_links

    def render_files(
        self, renderer: Environment, mappings: Dict[str, typing.Iterable[str] | str]
    ):
        category_links = self.get_category_links()

        # Style file of each template will be copied to the assets folder
        if style_file := self.get_style_file:
            mappings["style"] = "/assets" + os.path.sep + style_file.name

        mappings["category_sub_links"] = category_links.keys()  # type: ignore
        template = renderer.get_template(self.template_name)

        rendered_count = 0

        for file_link, file in category_links.items():
            md_content = md_renderer.render(file.read_text())
            if md_content is None:
                logging.warning(f"{file} returned None upon rendering.")
                continue

            mappings["content"] = md_content
            contents = template.render(mappings)
            rendered_count += 1
            yield RenederedTemplate.create(file_link, contents)
        
        logging.info("[Template Manager][%s] has finished rendering %d files", self.template_name, rendered_count)
