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
    if type(content) is dict :
        return False
    return bool(re.search(r'<[^>]+>', content))

def generate_rows_html(rows: Dict[str, Any], unique_prefix: str, level: int, indent: str) -> str:
    """
    Generates HTML for a rows structure, handling nested columns and other content.
    """
    number = rows.get("number", 1)
    row_content = rows.get("content", [])

    # Use "rows" class to align with CSS
    rows_html = f'{indent}<div class="rows">\n'

    for idx, row in enumerate(row_content):
        if "columns" in row:
            # If the row contains columns, generate them
            rows_html += generate_columns_html(row["columns"], f"{unique_prefix}-row-{idx}", level + 1, indent + "    ")
        elif "rows" in row:
            # If the row contains nested rows, recursively generate them
            rows_html += generate_rows_html(row["rows"], f"{unique_prefix}-row-{idx}", level + 1, indent + "    ")
        else:
            # Handle other content types like 'html-content' or 'folds'
            if "html-content" in row:
                rows_html += f'{indent}    {row["html-content"]}\n'
            if "folds" in row:
                for j, fold in enumerate(row["folds"]):
                    unique_id = f"fold-{unique_prefix}-row-{idx}-fold-{j}"
                    rows_html += generate_fold_html(fold, unique_id, level + 1, indent + "    ")

    rows_html += f'{indent}</div>\n'
    return rows_html



def generate_columns_html(columns: Dict[str, Any], unique_prefix: str, level: int, indent: str) -> str:
    """
    Generates HTML for a column structure, handling nested rows, columns, and folds.
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
            # Handle multiple keys within a single content dictionary
            if "html-content" in content:
                columns_html += f'{indent}        {content["html-content"]}\n'
            if "folds" in content:
                for j, fold in enumerate(content["folds"]):
                    unique_id = f"fold-{unique_prefix}-col-{idx}-fold-{j}"
                    columns_html += generate_fold_html(fold, unique_id, level + 1, indent + "        ")
            if "rows" in content:
                columns_html += generate_rows_html(content["rows"], f"{unique_prefix}-col-{idx}-row", level + 1, indent + "        ")
            if "columns" in content:
                columns_html += generate_columns_html(content["columns"], f"{unique_prefix}-col-{idx}-col", level + 1, indent + "        ")

        columns_html += f'{indent}    </div>\n'

    columns_html += f'{indent}</div>\n'
    return columns_html




def generate_toc(slides: List[Dict[str, Any]]) -> str:
    """Generate the Table of Contents (TOC) HTML based on main slides."""
    toc_html = ""
    for i, slide in enumerate(slides):
        if i == 0 and not slide.get("title"):
            continue  # Skip title slide
        toc_index = i - 1  # Adjust index for TOC
        toc_html += f'<a href="#" onclick="navigateTo({toc_index}); return false;">{slide["title"]}</a>\n'
    return toc_html

def generate_breadcrumbs(slides: List[Dict[str, Any]]) -> str:
    """Generate the Breadcrumbs HTML based on main slides."""
    breadcrumbs_html = '<ol>\n'
    for i, slide in enumerate(slides):
        breadcrumbs_html += f'    <li><a href="#" onclick="navigateTo({i}); return false;">{slide["title"]}</a></li>\n'
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
def generate_fold_html(fold: Dict[str, Any], unique_id: str, level: int, indent: str) -> str:
    """
    Generates HTML for a collapsible fold with varying background darkness based on depth.

    Args:
        fold (Dict[str, Any]): The fold data containing title, content, and possibly nested folds.
        unique_id (str): A unique identifier for the content panel associated with the collapsible.
        level (int): The current nesting depth level (1-based).
        indent (str): The indentation string for formatting.

    Returns:
        str: The generated HTML string for the fold.
    """
    # Define the maximum depth level supported
    MAX_LEVEL = 5

    # Ensure the current level does not exceed MAX_LEVEL
    current_level = min(level, MAX_LEVEL)

    # Attempt to retrieve the fold title; default if not present
    fold_title = fold.get("title", "Click to Expand")

    # Assign the appropriate 'level-x' class based on current_level
    fold_html = f'{indent}<button class="collapsible level-{current_level}" aria-expanded="false" aria-controls="{unique_id}">{fold_title}</button>\n'

    # Start the content panel with the unique ID
    fold_html += f'{indent}<div id="{unique_id}" class="content-panel">\n'

    # If the fold contains a chart, generate its HTML
    if "chart" in fold:
        fold_html += generate_chart_html(fold["chart"], indent + "    ")

    # If the fold contains "html-content", insert it directly
    if "html-content" in fold:
        fold_html += f'{indent}    {fold["html-content"]}\n'

    # If the fold contains "content", process each content item
    if "content" in fold:
        for content in fold["content"]:
            if is_html(content):
                fold_html += f'{indent}    {content}\n'
            else:
                fold_html += f'{indent}    <p>{content}</p>\n'

    # If the fold contains nested folds, recurse and increment the level
    if "folds" in fold:
        # Ensure 'folds' is a list
        nested_folds = fold["folds"]
        if isinstance(nested_folds, dict):
            # If 'folds' is a single dict, wrap it in a list
            nested_folds = [nested_folds]
        elif not isinstance(nested_folds, list):
            # If 'folds' is neither a dict nor a list, skip processing
            nested_folds = []

        for sub_fold in nested_folds:
            # Generate a unique ID for the nested fold
            sub_unique_id = f"{unique_id}-sub-{nested_folds.index(sub_fold)+1}"
            # Recursively generate HTML for the nested fold, incrementing the level
            fold_html += generate_fold_html(sub_fold, sub_unique_id, level + 1, indent + "    ")

    # Close the content panel div
    fold_html += f'{indent}</div>\n'
    return fold_html



# Main function to generate slide content
def generate_slide_content(slides: List[Dict[str, Any]], level: int = 0) -> str:
    slides_html = ""
    indent = "    " * level  # Indentation for readability

    for i, slide in enumerate(slides):
        # Determine CSS classes
        classes = "slide" if level == 0 else "nested-slide"
        if slide.get("dark"):
            classes += " dark"

        slides_html += f'{indent}<div class="{classes}">\n'
        slides_html += f'{indent}    <div class="content-wrapper">\n'
        slides_html += f'{indent}        <div class="text-content">\n'

        # Handle "html-content" separately
        for content in slide.get("html-content", []):
            slides_html += f'{indent}            {content}\n'

        # Handle "content" which can include rows, columns, plain text, or nested structures
        for content in slide.get("content", []):
            if isinstance(content, str):
                if is_html(content):
                    slides_html += f'{indent}            {content}\n'
                else:
                    slides_html += f'{indent}            <p>{content}</p>\n'
            elif isinstance(content, dict):
                if "rows" in content:
                    slides_html += generate_rows_html(content["rows"], f"slide-{level}-{i}", level, indent + "            ")
                elif "columns" in content:
                    slides_html += generate_columns_html(content["columns"], f"slide-{level}-{i}", level, indent + "            ")
                else:
                    # Handle other structured content like folds
                    slides_html += generate_fold_html(content, f"fold-{level}-{i}", level, indent + "            ")

        # Handle collapsible slides (folds)
        for j, fold in enumerate(slide.get("folds", [])):
            unique_id = f"collapsible-{level}-{i}-{j}"  # Unique ID for each fold
            slides_html += generate_fold_html(fold, unique_id, level, indent + "        ")

        slides_html += f'{indent}        </div>\n'

        # Handle images
        image_url = slide.get("image", "static/images/placeholder.png")
        if image_url:
            image_filename = os.path.basename(image_url)
            slides_html += f'{indent}        <div class="image-content">\n'
            slides_html += f'{indent}            <img src="images/{image_filename}" alt="{slide.get("title", "Image")} Image">\n'
            slides_html += f'{indent}        </div>\n'

        slides_html += f'{indent}    </div>\n'
        slides_html += f'{indent}</div>\n\n'

    return slides_html



def copy_images(
    slides: List[Dict[str, Any]],
    images_source_dir: Optional[str],
    destination_images_folder: str,
    placeholder_image: str = os.path.join(os.getcwd(), "static/images/placeholder.png")
) -> None:
    """
    Recursively copies images from the source directory to the destination images folder.
    Updates the 'image' field in the slide dictionary to use the placeholder image if needed.

    Args:
        slides (List[Dict[str, Any]]): List of slide dictionaries.
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

    for slide in slides:
        image_path = slide.get("image")
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
                    slide["image"] = os.path.basename(placeholder_image)  # Update image to placeholder
                    print(f"Copied placeholder image to '{dest_placeholder}'")
        else:
            # No image specified, use the placeholder
            print("No image specified. Using placeholder.")
            if placeholder_image:
                dest_placeholder = os.path.join(destination_images_folder, os.path.basename(placeholder_image))
                if not os.path.isfile(dest_placeholder):
                    shutil.copy(placeholder_image, dest_placeholder)
                slide["image"] = os.path.basename(placeholder_image)  # Update image to placeholder
                print(f"Copied placeholder image to '{dest_placeholder}'")

        # Recursively handle nested folds
        for fold in slide.get("folds", []):
            copy_images([fold], images_source_dir, destination_images_folder, placeholder_image)



def copy_project_images(
    slides: List[Dict[str, Any]],
    images_source_dir: Optional[str],
    destination_images_folder: str
) -> None:
    """
    Prepares the destination images folder and copies images.
    
    Args:
        slides (List[Dict[str, Any]]): List of slide dictionaries.
        images_source_dir (Optional[str]): Path to the source images directory.
        destination_images_folder (str): Path to the destination images folder.
    
    Returns:
        None
    """
    os.makedirs(destination_images_folder, exist_ok=True)
    copy_images(slides, images_source_dir, destination_images_folder)

