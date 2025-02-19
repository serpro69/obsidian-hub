# The goal is to sort lists by their obsidian link alias.
import os
import re
from glob import glob
from typing import List, Tuple, Optional, Any
import logging

PLUGIN_LIST_HEADING = '## Plugins in this category'


def extract_alias(markdown_link_list_item: str) -> str:
    # Return the alias if we have it, otherwise the page name.
    match = re.compile(r'^- \[\[(.*?)(?:\|(.*?))?]].*') \
        .search(markdown_link_list_item)

    if match is None:
        # If we find neither alias nor page, sort as blank.
        return ""

    for text in match.groups()[::-1]:
        if text is not None:
            return text

    return ""


def sort_list(markdown_list: str) -> str:
    lines = markdown_list.splitlines()
    sorted_lines = sorted(lines, key=lambda line: extract_alias(line))
    return "\n".join(sorted_lines) + "\n"


def read_file(file_path: str) -> str:
    with open(file_path) as f:
        return f.read()

def write_file(file_path: str , contents: str) -> None:
    with open(file_path, 'w') as f:
        f.write(contents)


def extract_list_pos(markdown_text: str, header: str) -> Optional[Tuple[int, int]]:
    """
    Returns the text positions for the first Markdown list
    within the block defined by the header.
    """

    # Find the header, which will be the beginning of our search range.
    try:
        header_start_pos = markdown_text.index(header)
    except ValueError as e:
        # No header found.
        return None

    header_end_pos = header_start_pos + len(header)

    # Find the following heading, which will be the end of our search range.
    next_header_match =  re.compile('^#+', re.M) \
        .search(markdown_text[header_end_pos:])
    if next_header_match is None:
        return None

    next_header_start_pos = header_end_pos + next_header_match.span(0)[0]

    # Find a Markdown list within this block of text.
    list_match = re.compile(r'\n*((?:- \[\[.*?\]\].*?\n)+)', re.M) \
        .search(markdown_text[header_end_pos:next_header_start_pos])
    if list_match is None:
        # No list found.
        return None

    # Find the precise text range for this list block in the overall markdown_text.
    start_pos = header_end_pos + list_match.span(1)[0]
    end_pos = start_pos + len(list_match.group(1))
    return (start_pos, end_pos)


def plugin_page_paths() -> List[str]:
    return glob("../../02 - Community Expansions/02.01 Plugins by Category/*.md")

def getLogger() -> logging.Logger:
    return logging.getLogger('sort_lists')

def main() -> None:
    logging.basicConfig(level=logging.INFO)

    for page_path in plugin_page_paths():
        sort_links_under_heading(page_path)


def sort_links_under_heading(page_path: str, heading: str = PLUGIN_LIST_HEADING) -> None:
    page_contents = read_file(page_path)
    log = getLogger()
    log.debug(f"Sorting page: {page_path}")
    log.debug(f"Within heading: {heading}")
    list_pos = extract_list_pos(page_contents, heading)

    if list_pos is None:
        log.warning(f"Could not find heading in page. Skipping {page_path}")
        return

    [list_start, list_end] = list_pos
    original_list = page_contents[list_start:list_end]
    log.debug(f"Original List:\n{original_list}")
    sorted_list = sort_list(original_list)
    log.debug(f"Sorted List:\n{sorted_list}")
    new_page_contents = page_contents[:list_start] + sorted_list + page_contents[list_end:]
    if page_contents != new_page_contents:
        log.info(f"Sort changed {page_path}")
    write_file(page_path, new_page_contents)


if __name__ == '__main__':
    main()
