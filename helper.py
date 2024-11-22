# helper.py
import os
import re
import shutil
from typing import List, Dict, Any, Optional
import json

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

def generate_breadcrumbs(sections: List[Dict[str, Any]]) -> str:
    """Generate the Breadcrumbs HTML based on main sections."""
    breadcrumbs_html = '<ol>\n'
    for i, section in enumerate(sections):
        breadcrumbs_html += f'    <li><a href="#" onclick="navigateTo({i}); return false;">{section["title"]}</a></li>\n'
    breadcrumbs_html += '</ol>'
    return breadcrumbs_html

def generate_section_content(sections: List[Dict[str, Any]], level: int = 0) -> str:
    sections_html = ""
    indent = "    " * level  # Indentation for readability

    for i, section in enumerate(sections):
        # Top-level or nested sections
        classes = "section" if level == 0 else "nested-section"
        if section.get("dark"):
            classes += " dark"
        sections_html += f'{indent}<div class="{classes}">\n'
        sections_html += f'{indent}    <div class="content-wrapper">\n'
        sections_html += f'{indent}        <div class="text-content">\n'

        # Add main content
        for content in section.get("content", []):
            sections_html += f'{indent}            <p>{content}</p>\n'

        # Handle collapsible sections (folds)
        for j, fold in enumerate(section.get("folds", [])):
            unique_id = f"collapsible-{level}-{i}-{j}"  # Unique ID for each fold
            sections_html += f'{indent}            <button class="collapsible" aria-expanded="false" aria-controls="{unique_id}">{fold["title"]}</button>\n'
            sections_html += f'{indent}            <div id="{unique_id}" class="content-panel">\n'
            
            # If the fold contains a chart, include it
            if "chart" in fold:
                # Serialize the chart data as JSON
                chart_json = json.dumps(fold["chart"]).replace("'", "&apos;")
                sections_html += f'{indent}                <div class="chart-container" data-chart-data=\'{chart_json}\'>\n'
                sections_html += f'{indent}                    <canvas></canvas>\n'
                sections_html += f'{indent}                </div>\n'
            # If the fold has additional content, handle it
            else:
                for fold_content in fold.get("content", []):
                    sections_html += f'{indent}                <p>{fold_content}</p>\n'

            sections_html += f'{indent}            </div>\n'

        sections_html += f'{indent}        </div>\n'

        # Handle images
        image_url = section.get("image")
        if image_url:
            image_filename = os.path.basename(image_url)
            sections_html += f'{indent}        <div class="image-content">\n'
            sections_html += f'{indent}            <img src="images/{image_filename}" alt="{section["title"]} Image">\n'
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
            # Handle nested folds
            for fold in section.get("folds", []):
                nested_image = fold.get("image")
                if nested_image:
                    src_nested_image = os.path.join(images_source_dir, nested_image)
                    if os.path.isfile(src_nested_image):
                        shutil.copy(src_nested_image, destination_images_folder)
                        print(f"Copied image {src_nested_image} to {destination_images_folder}")
                    else:
                        print(f"Image file {src_nested_image} not found. Skipping.")
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

