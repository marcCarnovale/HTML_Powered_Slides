import os
import re
import shutil
from typing import List, Dict, Any, Optional

def sanitize_title(title: str) -> str:
    """Sanitize the presentation title to create a valid filename."""
    return re.sub(r'[^a-zA-Z0-9_\-]', '', title.replace(' ', '_'))

def generate_toc(sections: List[Dict[str, Any]]) -> str:
    """Generate the Table of Contents (TOC) HTML based on main sections."""
    toc_html = ""
    for i, section in enumerate(sections):
        if i == 0 and not section.get("title"):
            continue  # Skip title slide
        toc_index = i - 1  # Adjust index for TOC
        toc_html += f'<a href="#" onclick="navigateTo({toc_index}); return false;">{section["title"]}</a>\n'
    return toc_html

def generate_section_content(sections: List[Dict[str, Any]], level: int = 0) -> str:
    """
    Recursively generate HTML content for sections with nested folds.
    
    Args:
        sections (List[Dict[str, Any]]): A list of section dictionaries.
        level (int): Current nesting level for indentation.
    
    Returns:
        str: HTML string for all sections.
    """
    sections_html = ""
    indent = "    " * level  # Indentation for readability
    for i, section in enumerate(sections):
        # Assign 'section' class only to top-level sections
        if level == 0:
            classes = "section"
            if section.get("dark"):
                classes += " dark"
            sections_html += f'{indent}<div class="{classes}">\n'
        else:
            # Use a different class for nested folds
            classes = "nested-section"
            if section.get("dark"):
                classes += " dark"
            sections_html += f'{indent}<div class="{classes}">\n'

        sections_html += f'{indent}    <div class="content-wrapper">\n'
        sections_html += f'{indent}        <div class="text-content">\n'

        # Add main content
        for content in section.get("content", []):
            sections_html += f'{indent}            {content}\n'

        # Handle collapsible sections (folds)
        for j, fold in enumerate(section.get("folds", [])):
            unique_id = f"collapsible-{level}-{i}-{j}"
            sections_html += f'{indent}            <button class="collapsible" aria-expanded="false" aria-controls="{unique_id}">{fold["title"]}</button>\n'
            sections_html += f'{indent}            <div id="{unique_id}" class="content-panel">\n'
            # Recursive call for nested folds
            sections_html += generate_section_content([fold], level + 1)
            sections_html += f'{indent}            </div>\n'

        sections_html += f'{indent}        </div>\n'

        # Handle images
        image_url = section.get("image")
        if image_url:
            image_filename = os.path.basename(image_url)
            sections_html += f'{indent}        <div class="image-content">\n'
            sections_html += f'{indent}            <img src="images/{image_filename}" alt="Section Image">\n'
            sections_html += f'{indent}        </div>\n'

        sections_html += f'{indent}    </div>\n'
        sections_html += f'{indent}</div>\n\n'
    return sections_html

def copy_images(
    sections: List[Dict[str, Any]],
    images_source_dir: Optional[str],
    destination_images_folder: str
) -> None:
    """
    Copies images from the source directory to the destination images folder.
    
    Args:
        sections (List[Dict[str, Any]]): List of section dictionaries.
        images_source_dir (Optional[str]): Path to the source images directory.
        destination_images_folder (str): Path to the destination images folder.
    
    Returns:
        None
    """
    if images_source_dir:
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
        print("No external images directory specified. Assuming images are already in the output folder.")

def copy_project_images(
    sections: List[Dict[str, Any]],
    images_source_dir: Optional[str],
    destination_images_folder: str
) -> None:
    """
    Prepares the destination images folder and copies images.
    
    Args:
        sections (List[Dict[str, Any]]): List of section dictionaries.
        images_source_dir (Optional[str]): Path to the source images directory.
        destination_images_folder (str): Path to the destination images folder.
    
    Returns:
        None
    """
    os.makedirs(destination_images_folder, exist_ok=True)
    copy_images(sections, images_source_dir, destination_images_folder)
