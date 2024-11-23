# helper.py
import os
import re
import shutil
from typing import List, Dict, Any, Optional
import json

def sanitize_title(title: str) -> str:
    """Sanitize the presentation title to create a valid filename."""
    return re.sub(r'[^a-zA-Z0-9_\-]', '', title.replace(' ', '_'))

def is_html(content: str) -> bool:
    """
    Determine if the content string contains any HTML tags.

    Args:
        content (str): The content string to check.

    Returns:
        bool: True if content contains HTML tags, False otherwise.
    """
    return bool(re.search(r'<[^>]+>', content))
def generate_rows_html(rows: Dict[str, Any], unique_prefix: str, level: int, indent: str) -> str:
    """
    Generates HTML for a row structure.
    """
    number = rows.get("number", 1)
    row_content = rows.get("content", [])
    
    rows_html = f'{indent}<div class="row">\n'
    
    for idx, row in enumerate(row_content):
        rows_html += generate_columns_html(row.get("columns", {}), f"{unique_prefix}-row-{idx}", level, indent + "    ")
    
    rows_html += f'{indent}</div>\n'
    return rows_html

# helper.py

def generate_columns_html(columns: Dict[str, Any], unique_prefix: str, level: int, indent: str) -> str:
    """
    Generates HTML for a column structure.
    """
    number = columns.get("number", 1)
    sizes = columns.get("size", ["100%"] * number)
    column_content = columns.get("content", [])

    columns_html = f'{indent}<div class="columns">\n'

    for idx in range(number):
        size = sizes[idx] if idx < len(sizes) else "100%"
        content = column_content[idx] if idx < len(column_content) else ""

        columns_html += f'{indent}    <div class="column resizable" style="flex: 0 0 {size};">\n'

        if isinstance(content, str):
            if is_html(content):
                columns_html += f'{indent}        {content}\n'
            else:
                columns_html += f'{indent}        <p>{content}</p>\n'
        elif isinstance(content, dict):
            if "html-content" in content:
                columns_html += f'{indent}        {content["html-content"]}\n'
            else:
                # Handle nested structures like rows, columns, folds, etc.
                columns_html += generate_section_content([content], level + 1)

        columns_html += f'{indent}    </div>\n'

    columns_html += f'{indent}</div>\n'
    return columns_html



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

# Helper function to generate chart HTML
def generate_chart_html(chart_data: Dict[str, Any], indent: str) -> str:
    chart_json = json.dumps(chart_data).replace("'", "&apos;")
    return (
        f'{indent}<div class="chart-container" data-chart-data=\'{chart_json}\'>\n'
        f'{indent}    <canvas></canvas>\n'
        f'{indent}</div>\n'
    )

# Helper function to generate fold HTML
# helper.py

def generate_fold_html(fold: Dict[str, Any], unique_id: str, level: int, indent: str) -> str:
    try:
        fold_html = f'{indent}<button class="collapsible" aria-expanded="false" aria-controls="{unique_id}">{fold["title"]}</button>\n'
    except KeyError:
        fold_html = f'{indent}<button class="collapsible" aria-expanded="false" aria-controls="{unique_id}">Click to Expand</button>\n'
    
    fold_html += f'{indent}<div id="{unique_id}" class="content-panel">\n'
    
    # If the fold contains a chart
    if "chart" in fold:
        fold_html += generate_chart_html(fold["chart"], indent + "    ")
    
    # If the fold contains "html-content"
    if "html-content" in fold:
        fold_html += f'{indent}    {fold["html-content"]}\n'
    
    # If the fold contains "content"
    if "content" in fold:
        for content in fold["content"]:
            if is_html(content):
                fold_html += f'{indent}    {content}\n'
            else:
                fold_html += f'{indent}    <p>{content}</p>\n'
    
    # If the fold contains nested folds, recurse
    if "folds" in fold:
        fold_html += generate_section_content([fold], level + 1)
    
    fold_html += f'{indent}</div>\n'
    return fold_html


# Main function to generate section content
# helper.py

def generate_section_content(sections: List[Dict[str, Any]], level: int = 0) -> str:
    sections_html = ""
    indent = "    " * level  # Indentation for readability

    for i, section in enumerate(sections):
        # Determine CSS classes
        classes = "section" if level == 0 else "nested-section"
        if section.get("dark"):
            classes += " dark"

        sections_html += f'{indent}<div class="{classes}">\n'
        sections_html += f'{indent}    <div class="content-wrapper">\n'
        sections_html += f'{indent}        <div class="text-content">\n'

        # Handle "html-content" separately
        for content in section.get("html-content", []):
            sections_html += f'{indent}            {content}\n'

        # Handle "content" which can include rows, columns, plain text, or nested structures
        for content in section.get("content", []):
            if isinstance(content, str):
                if is_html(content):
                    sections_html += f'{indent}            {content}\n'
                else:
                    sections_html += f'{indent}            <p>{content}</p>\n'
            elif isinstance(content, dict):
                if "rows" in content:
                    sections_html += generate_rows_html(content["rows"], f"section-{level}-{i}", level, indent + "            ")
                elif "columns" in content:
                    sections_html += generate_columns_html(content["columns"], f"section-{level}-{i}", level, indent + "            ")
                else:
                    # Handle other structured content like folds
                    sections_html += generate_fold_html(content, f"fold-{level}-{i}", level, indent + "            ")

        # Handle collapsible sections (folds)
        for j, fold in enumerate(section.get("folds", [])):
            unique_id = f"collapsible-{level}-{i}-{j}"  # Unique ID for each fold
            sections_html += generate_fold_html(fold, unique_id, level, indent + "        ")

        sections_html += f'{indent}        </div>\n'

        # Handle images
        image_url = section.get("image", "static/images/placeholder.png")
        if image_url:
            image_filename = os.path.basename(image_url)
            sections_html += f'{indent}        <div class="image-content">\n'
            sections_html += f'{indent}            <img src="images/{image_filename}" alt="{section.get("title", "Image")} Image">\n'
            sections_html += f'{indent}        </div>\n'

        sections_html += f'{indent}    </div>\n'
        sections_html += f'{indent}</div>\n\n'

    return sections_html



def copy_images(
    sections: List[Dict[str, Any]],
    images_source_dir: Optional[str],
    destination_images_folder: str,
    placeholder_image: str = os.path.join(os.getcwd(), "static/images/placeholder.png")
) -> None:
    """
    Recursively copies images from the source directory to the destination images folder.
    Updates the 'image' field in the section dictionary to use the placeholder image if needed.

    Args:
        sections (List[Dict[str, Any]]): List of section dictionaries.
        images_source_dir (Optional[str]): Path to the source images directory.
        destination_images_folder (str): Path to the destination images folder.
        placeholder_image (str): Path to the placeholder image.

    Returns:
        None
    """
    # Ensure the destination directory exists
    os.makedirs(destination_images_folder, exist_ok=True)

    # Verify the placeholder image exists
    if not os.path.isfile(placeholder_image):
        print(f"Placeholder image '{placeholder_image}' does not exist. Skipping.")
        placeholder_image = None

    for section in sections:
        image_path = section.get("image")
        if image_path:
            src_image = os.path.join(images_source_dir, image_path) if images_source_dir else None
            dest_image = os.path.join(destination_images_folder, os.path.basename(image_path))

            if src_image and os.path.isfile(src_image):
                shutil.copy(src_image, dest_image)
                print(f"Copied image '{src_image}' to '{destination_images_folder}'")
            else:
                print(f"Image '{image_path}' not found. Using placeholder.")
                if placeholder_image:
                    dest_placeholder = os.path.join(destination_images_folder, os.path.basename(placeholder_image))
                    if not os.path.isfile(dest_placeholder):
                        shutil.copy(placeholder_image, dest_placeholder)
                    section["image"] = os.path.basename(placeholder_image)  # Update image to placeholder
                    print(f"Copied placeholder image to '{dest_placeholder}'")
        else:
            # No image specified, use the placeholder
            print("No image specified. Using placeholder.")
            if placeholder_image:
                dest_placeholder = os.path.join(destination_images_folder, os.path.basename(placeholder_image))
                if not os.path.isfile(dest_placeholder):
                    shutil.copy(placeholder_image, dest_placeholder)
                section["image"] = os.path.basename(placeholder_image)  # Update image to placeholder
                print(f"Copied placeholder image to '{dest_placeholder}'")

        # Recursively handle nested folds
        for fold in section.get("folds", []):
            copy_images([fold], images_source_dir, destination_images_folder, placeholder_image)



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

