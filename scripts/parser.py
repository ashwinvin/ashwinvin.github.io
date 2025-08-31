import logging
import os
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from itertools import islice

from jinja2 import Environment
from markdown_it import MarkdownIt
import frontmatter

md_renderer = MarkdownIt("gfm-like")


def shorten_text(text: str, word_limit: int = 50):
    words = (word for word in text.split(" "))
    return " ".join(islice(words, word_limit))


@dataclass
class RenderedDocument:
    category_name: str
    _relative_path: Path
    contents: str
    metadata: dict[str, typing.Any]

    @property
    def output_path(self) -> Path:
        actual_path = self.category_name / self._relative_path
        file_name = actual_path.stem.lower().replace(" ", "_")
        return actual_path.with_stem(file_name).with_suffix(".html")

    @property
    def title(self) -> str:
        return self.metadata.get(
            "title"
        ) or self._relative_path.name.capitalize().replace("_", " ")

    @property
    def tags(self) -> list[str]:
        return self.metadata.get("tags") or []

    @property
    def abstract(self) -> str:
        return self.metadata["abstract"] + f"<a href=/{self.output_path}>...</a>"

    @property
    def private(self) -> bool:
        return self.metadata.get("private") or False


@dataclass
class CategoryManager:
    name: str
    source_dir: Path
    style_file: Path | None

    @classmethod
    def create(
        cls,
        source_dir: Path,
        assets_dir: Path,
    ) -> "CategoryManager":
        style_file = assets_dir / f"{source_dir.name}.css"
        if not style_file.exists():
            style_file = None

        return CategoryManager(source_dir.stem, source_dir, style_file)

    @staticmethod
    def _get_files(directory_path: Path):
        for file in directory_path.iterdir():
            if file.is_dir():
                yield from CategoryManager._get_files(file)
            if file.is_file():
                yield file.absolute()

    @property
    def link(self):
        """
        Path to article index which uses the template
        """
        return "/" + self.name + "/index.html"

    def get_category_children(self) -> Dict[Path, Path]:
        """
        Returns a dictionary containing links to each page as keys and their absolute path as values.
        Both the keys and values point to the source files.
        """
        page_links = {}

        for page_path in CategoryManager._get_files(self.source_dir):
            page_link = page_path.relative_to(self.source_dir)
            page_links[page_link] = page_path

        return page_links

    def render_files(self, renderer: Environment, mappings: Dict[str, typing.Any]):
        category_children = self.get_category_children()

        # Style file of each template will be copied to the assets folder
        if self.style_file:
            mappings["style"] = "/assets" + os.path.sep + self.style_file.name

        rendered_documents: list[RenderedDocument] = []

        for file_link, file in category_children.items():
            metadata, contents = frontmatter.parse(file.read_text())
            md_content = md_renderer.render(contents)
            metadata["abstract"] = shorten_text(md_content)  # TODO: Configurable length

            if md_content is None:
                logging.warning(f"{file} returned None upon rendering.")
                continue
            mappings["content"] = md_content

            template_name = (
                metadata.get("template") or "article"
            )  # TODO: Configurable default template
            template = renderer.get_template(template_name)  # type: ignore
            contents = template.render(mappings)

            rendered_documents.append(
                RenderedDocument(self.name, file_link, contents, metadata)
            )
            yield rendered_documents[-1]

        # Render article index for category
        mappings["category_children"] = rendered_documents  # type: ignore

        cat_index_template = renderer.get_template("category_index")
        cat_index_contents = cat_index_template.render(mappings)
        cat_index_metadata = {}  # TODO
        yield RenderedDocument(
            self.name,
            Path("index.html"),
            cat_index_contents,
            cat_index_metadata,
        )

        logging.info(
            "[Template Manager][%s] has finished rendering %d files",
            self.name,
            len(rendered_documents),
        )
