import os
import argparse
import shutil
from typing import List, Dict, Optional, Any
from helper import (
    sanitize_title,
    generate_toc,
    generate_section_content,
    copy_images
)
from bs4 import BeautifulSoup

def generate_presentation(
    title: str,
    author: str,
    date: str,
    sections: List[Dict[str, Any]],
    output_dir: Optional[str] = None,
    images_source_dir: Optional[str] = None
) -> None:
    """
    Generates an HTML presentation based on the provided details.

    This function handles copying necessary static files and images, generating the main
    presentation HTML, creating the final "Thank You" slide, and appending a clickable
    overlay to the last slide for redirection.

    Args:
        title (str): The title of the presentation.
        author (str): The author of the presentation.
        date (str): The date of the presentation.
        sections (List[Dict[str, Any]]): A list of sections, each represented as a dictionary
            with keys like "title", "content", "image", "folds", and "dark".
        output_dir (Optional[str]): The directory where the presentation will be generated.
            Defaults to a folder named after the sanitized title in the current working directory.
        images_source_dir (Optional[str]): The directory from which images will be sourced.
            If not specified, images are assumed to be in the output directory's "images/" folder.

    Raises:
        FileNotFoundError: If required templates or images are missing.
    """
    # Determine output folder
    if output_dir:
        output_folder = output_dir
    else:
        sanitized_title = sanitize_title(title)
        output_folder = os.path.join(os.getcwd(), sanitized_title)
    os.makedirs(output_folder, exist_ok=True)
    print(f"Output will be saved to: {output_folder}")

    # Paths to templates and CSS
    core_template_path = os.path.join("templates", "core.html")
    end_slide_template_path = os.path.join("templates", "end_slide.html")
    css_path = os.path.join("static", "style.css")
    destination_images_folder = os.path.join(output_folder, "images")

    # Verify template files exist
    if not os.path.isfile(core_template_path):
        raise FileNotFoundError(f"Core template not found at {core_template_path}")
    if not os.path.isfile(end_slide_template_path):
        raise FileNotFoundError(f"Thank You template not found at {end_slide_template_path}")
    if not os.path.isfile(css_path):
        raise FileNotFoundError(f"CSS file not found at {css_path}")

    # Copy static files to output folder
    copy_static_files(css_path, output_folder)

    # Copy images to output folder
    copy_project_images(sections, images_source_dir, destination_images_folder)

    # Generate the main presentation HTML
    main_presentation_filename = generate_html_presentation(
        title, sections, core_template_path, output_folder
    )

    # Generate the final "Thank You" slide
    generate_final_slide(
        end_slide_template_path, main_presentation_filename, output_folder
    )

    # Append the overlay to the final section to redirect to "Thank You" slide
    final_slide_filename = "end_slide.html"
    append_overlay_to_final_slide(
        main_presentation_filename, final_slide_filename, output_folder
    )

def generate_html_presentation(
    title: str,
    sections: List[Dict[str, Any]],
    template_path: str,
    output_folder: str
) -> str:
    """
    Generates the main presentation HTML file using the core template.

    Args:
        title (str): The title of the presentation.
        sections (List[Dict[str, Any]]): A list of section dictionaries.
        template_path (str): Path to the core HTML template.
        output_folder (str): Path to the output directory.

    Returns:
        str: Filename of the generated main presentation HTML.
    """
    # Read the core HTML template as string
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Generate TOC and sections
    toc_html = generate_toc(sections)
    sections_html = generate_section_content(sections)

    # Replace placeholders
    html_content = html_content.replace("{{title}}", title)
    html_content = html_content.replace("{{toc}}", toc_html)
    html_content = html_content.replace("{{sections}}", sections_html)

    # Write the main presentation HTML to the output folder
    sanitized_title = sanitize_title(title)
    main_presentation_filename = f"{sanitized_title}.html"
    output_path = os.path.join(output_folder, main_presentation_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Main presentation saved to {output_path}")
    return main_presentation_filename

def generate_final_slide(
    template_path: str,
    main_presentation_filename: str,
    output_folder: str
) -> None:
    """
    Generates the final "Thank You" slide HTML file.

    Args:
        template_path (str): Path to the end_slide.html template.
        main_presentation_filename (str): Filename of the main presentation HTML.
        output_folder (str): Path to the output directory.

    Returns:
        None
    """
    # Read the end_slide.html template
    with open(template_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Replace the placeholder with the main presentation filename
    script_tag = soup.find("script")
    if script_tag and "{{main_presentation_filename}}" in script_tag.string:
        script_content = script_tag.string.replace("{{main_presentation_filename}}", main_presentation_filename)
        script_tag.string.replace_with(script_content)

    # Write the final slide HTML to the output folder
    final_slide_filename = "end_slide.html"
    output_path = os.path.join(output_folder, final_slide_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
    print(f"Final 'Thank You' slide saved to {output_path}")

def append_overlay_to_final_slide(
    main_presentation_filename: str,
    final_slide_filename: str,
    output_folder: str
) -> None:
    """
    Appends a fullscreen clickable overlay to the final section of the main presentation
    that redirects to the final "Thank You" slide.

    Args:
        main_presentation_filename (str): The filename of the main presentation HTML.
        final_slide_filename (str): The filename of the final "Thank You" slide HTML.
        output_folder (str): Path to the output directory.

    Returns:
        None
    """
    main_presentation_path = os.path.join(output_folder, main_presentation_filename)

    # Read the main presentation HTML
    with open(main_presentation_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Find all sections
    sections = soup.find_all("div", class_="section")
    if not sections:
        print("No sections found in the main presentation HTML.")
        return

    # Get the last section
    last_section = sections[-1]

    # Ensure the last section has position: relative for the overlay to position correctly
    existing_style = last_section.get('style', '')
    if 'position: relative;' not in existing_style:
        last_section['style'] = existing_style + ' position: relative;'

    # Create the overlay div
    overlay_div = soup.new_tag("div", attrs={
        "class": "overlay",
        "onclick": f"window.location.href='{final_slide_filename}'"
    })

    # Optional: Add some content or styles to make the overlay visible for testing
    # For production, keep it invisible by not adding background-color
    # overlay_div['style'] = "background-color: rgba(255, 0, 0, 0.2);"  # Uncomment for debugging

    # Append the overlay to the last section
    last_section.append(overlay_div)

    # Write back the modified HTML
    with open(main_presentation_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
    print(f"Overlay added to the final section in {main_presentation_path} to redirect to {final_slide_filename}")

def copy_static_files(css_path: str, output_folder: str) -> None:
    """
    Copies the CSS file to the output folder's static directory.

    Args:
        css_path (str): Path to the CSS file.
        output_folder (str): Path to the output directory.

    Returns:
        None
    """
    static_output_folder = os.path.join(output_folder, "static")
    os.makedirs(static_output_folder, exist_ok=True)
    shutil.copy(css_path, static_output_folder)
    print(f"Copied CSS to {static_output_folder}")

def copy_project_images(
    sections: List[Dict[str, Any]],
    images_source_dir: Optional[str],
    destination_images_folder: str
) -> None:
    """
    Copies images from the source folder to the destination folder.

    Args:
        sections (List[Dict[str, Any]]): List of section dictionaries.
        images_source_dir (Optional[str]): Path to the source images folder.
            If None, assumes images are in the output folder's "images/" directory.
        destination_images_folder (str): Path to the destination images folder.

    Returns:
        None
    """
    os.makedirs(destination_images_folder, exist_ok=True)
    copy_images(sections, images_source_dir, destination_images_folder)

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate an HTML presentation.")
    parser.add_argument('--output_dir', type=str, default=None,
                        help='Path to the output directory. Defaults to a folder named after the presentation title.')
    parser.add_argument('--images_dir', type=str, default=None,
                        help='Path to the images directory. If not specified, images are assumed to be in the output directory\'s "images/" folder.')
    args = parser.parse_args()

    # Presentation details
    title = "Example Presentation"
    author = "Marc Carnovale"
    date = "November 21, 2024"

    # Detailed sections with collapsible dropdowns for extra information
    sections = [
        {
            "title": "",  # Title slide
            "content": [
                f"<h1>{title}</h1>",
                f"<h3>by {author}</h3>",
                f"<p>{date}</p>"
            ],
            "dark": True
        },
        {
            "title": "Introduction",
            "content": [
                "Welcome to the presentation!",
                "This section introduces the topic and sets the context."
            ],
            "image": "Placeholder+Image.png"  # Relative to images_source_dir or output/images/
        },
        {
            "title": "Philosophy",
            "content": [
                "<h2>Guiding Principles</h2>",
                "<p>Ensure training code matches production pipelines, focusing on scalability and operational efficiency.</p>"
            ]
        },
        {
            "title": "Data Preparation",
            "content": [
                "Steps to clean the data and handle missing values.",
                "Techniques used for data preprocessing."
            ],
            "folds": [
                {
                    "title": "Handling Missing Values",
                    "content": [
                        "Imputation with mean.",
                        "Dropping incomplete records."
                    ]
                }
            ],
            "image": "Placeholder+Image.png"  # Relative to images_source_dir or output/images/
        },
        {
            "title": "Modeling",
            "content": [
                "Overview of the predictive models used.",
                "Evaluation metrics and results interpretation."
            ],
            "image": "Placeholder+Image.png"  # Relative to images_source_dir or output/images/
        },
        {
            "title": "Conclusion",
            "content": [
                "Summary of key findings.",
                "Next steps and future work."
            ]
            # No image in this section
        },
    ]

    # Call the generate_presentation function with the provided details
    generate_presentation(
        title=title,
        author=author,
        date=date,
        sections=sections,
        output_dir=args.output_dir,
        images_source_dir=args.images_dir
    )

if __name__ == "__main__":
    main()
