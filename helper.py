import os
import re
import shutil
from typing import List, Dict, Any, Optional

def sanitize_title(title: str) -> str:
    """
    Sanitize the presentation title to create a valid filename.
    
    Replaces spaces with underscores and removes any characters 
    that are not alphanumeric, underscores, or hyphens.

    Args:
        title (str): The title of the presentation.

    Returns:
        str: A sanitized filename derived from the title.
    """
    return re.sub(r'[^a-zA-Z0-9_\-]', '', title.replace(' ', '_'))

def generate_toc(sections: List[Dict[str, Any]]) -> str:
    """
    Generate the Table of Contents (TOC) HTML based on the provided sections.

    Each section is represented as a clickable link in the sidebar.

    Args:
        sections (List[Dict[str, Any]]): A list of dictionaries where each dictionary represents a section 
            with a "title" and optional "content" and "folds".

    Returns:
        str: HTML string for the TOC links.
    """
    toc_html = ""
    for i, section in enumerate(sections):
        # Skip the first section if it's the title slide (empty title)
        if i == 0 and not section.get("title"):
            continue
        # TOC link index starts from 0, corresponding to section index 1
        toc_index = i - 1
        toc_html += f'<a href="#" onclick="navigateTo({toc_index}); return false;">{section["title"]}</a>\n'
    return toc_html

def generate_section_content(sections: List[Dict[str, Any]]) -> str:
    """
    Generate the HTML content for all sections of the presentation.

    Each section is enclosed in a <div> with class "section". 
    Supports:
    - Text content on the left.
    - Optional single image on the right, scaled appropriately.
    - Optional collapsible elements for additional details.
    - Optional dark background styling via 'dark' flag.

    Args:
        sections (List[Dict[str, Any]]): A list of dictionaries where each dictionary represents a section.

    Returns:
        str: HTML string for all sections.
    """
    sections_html = ""
    for i, section in enumerate(sections):
        sections_html += f'<div id="section-{i}" class="section{" dark" if section.get("dark") else ""}">\n'
        sections_html += '    <div class="content-wrapper">\n'
        sections_html += '        <div class="text-content">\n'
        for content in section.get("content", []):
            sections_html += f'            {content}\n'
        # Handle collapsible sections
        for fold in section.get("folds", []):
            sections_html += f'            <button class="collapsible">{fold["title"]}</button>\n'
            sections_html += '            <div class="content-panel">\n'
            for line in fold.get("content", []):
                sections_html += f'                <p>{line}</p>\n'
            sections_html += '            </div>\n'
        sections_html += '        </div>\n'
        # Handle image
        image_url = section.get("image")
        if image_url:
            # Assuming images are stored in 'images/' directory within the output folder
            image_filename = os.path.basename(image_url)
            sections_html += '        <div class="image-content">\n'
            sections_html += f'            <img src="images/{image_filename}" alt="Section Image">\n'
            sections_html += '        </div>\n'
        sections_html += '    </div>\n'
        sections_html += '</div>\n\n'
    return sections_html

def copy_images(
    sections: List[Dict[str, Any]],
    images_source_dir: Optional[str],
    destination_images_folder: str
) -> None:
    """
    Copy images from the source folder to the destination folder.

    Args:
        sections (List[Dict[str, Any]]): List of section dictionaries.
        images_source_dir (Optional[str]): Path to the source images folder.
            If None, assumes images are already in the destination folder.
        destination_images_folder (str): Path to the destination images folder.

    Returns:
        None
    """
    if images_source_dir:
        # If an external images directory is specified, copy images from there
        if not os.path.isdir(images_source_dir):
            print(f"Specified images directory '{images_source_dir}' does not exist.")
            return
        for section in sections:
            image_path = section.get("image")
            if image_path:
                src_image = os.path.join(images_source_dir, image_path)
                if os.path.isfile(src_image):
                    shutil.copy(src_image, destination_images_folder)
                    print(f"Copied image {src_image} to {destination_images_folder}")
                else:
                    print(f"Image file {src_image} not found. Skipping.")
    else:
        # If no external images directory, assume images are already in the output images folder
        print("No external images directory specified. Assuming images are already in the output folder.")

def copy_project_images(
    sections: List[Dict[str, Any]],
    images_source_dir: Optional[str],
    destination_images_folder: str
) -> None:
    """
    Wrapper function to copy images from the specified source directory to the destination.

    Args:
        sections (List[Dict[str, Any]]): List of section dictionaries.
        images_source_dir (Optional[str]): Path to the source images folder.
        destination_images_folder (str): Path to the destination images folder.

    Returns:
        None
    """
    os.makedirs(destination_images_folder, exist_ok=True)
    copy_images(sections, images_source_dir, destination_images_folder)

