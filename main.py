import argparse
import os
import json
import yaml
from typing import Dict, Any, List, Tuple
from helper import (
    sanitize_title,
    generate_toc,
    generate_section_content,
    copy_project_images
)

def load_configuration(config_path: str) -> Dict[str, Any]:
    """
    Loads presentation configuration from a JSON or YAML file.
    
    Args:
        config_path (str): Path to the configuration file.
    
    Returns:
        Dict[str, Any]: Parsed configuration data.
    """
    with open(config_path, 'r') as f:
        if config_path.endswith('.json'):
            return json.load(f)
        elif config_path.endswith(('.yaml', '.yml')):
            return yaml.safe_load(f)
        else:
            raise ValueError("Unsupported configuration file format. Use JSON or YAML.")

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

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate an HTML presentation.")
    parser.add_argument('--output_dir', type=str, default=None,
                        help='Path to the output directory. Defaults to a folder named after the presentation title.')
    parser.add_argument('--images_dir', type=str, default=None,
                        help='Path to the images directory. If not specified, images are assumed to be in the output directory\'s "images/" folder.')
    parser.add_argument('--config', type=str, default=None,
                        help='Path to the presentation configuration file (JSON or YAML).')
    args = parser.parse_args()

    if args.config:
        config = load_configuration(args.config)
        title = config.get("title", "Untitled Presentation")
        author = config.get("author", "Unknown Author")
        date = config.get("date", "Unknown Date")
        sections = config.get("sections", [])
    else:
        # Default presentation details
        title = "Example Presentation"
        author = "Marc Carnovale"
        date = "November 21, 2024"
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
                    "<p>Welcome to the presentation!</p>",
                    "<p>This section introduces the topic and sets the context.</p>"
                ],
                "folds": [
                    {
                        "title": "Background",
                        "content": [
                            "<p>Historical context and foundational information.</p>"
                        ],
                        "folds": [
                            {
                                "title": "Early Developments",
                                "content": [
                                    "<p>Key milestones in the early stages.</p>"
                                ],
                                "image": "Placeholder+Image.png"
                            },
                            {
                                "title": "Modern Advances",
                                "content": [
                                    "<p>Recent breakthroughs and current trends.</p>"
                                ]
                            }
                        ],
                        "image": "Placeholder+Image.png"
                    },
                    {
                        "title": "Objectives",
                        "content": [
                            "<p>Primary goals and expected outcomes.</p>"
                        ]
                    }
                ],
                "image": "Placeholder+Image.png"
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
        {
            "title": "Thank You",
            "content": [
                "<h2>Thank You!</h2>",
                "<p>Your questions?</p>",
                "<p>Feel free to reach out for further discussions.</p>"
            ],
        }
        ]


    # Determine output directory
    if args.output_dir:
        output_folder = args.output_dir
    else:
        sanitized_title = sanitize_title(title)
        output_folder = sanitized_title

    os.makedirs(output_folder, exist_ok=True)

    # Copy images to output folder
    destination_images_folder = os.path.join(output_folder, "images")
    copy_project_images(sections, args.images_dir, destination_images_folder)

    # Generate HTML presentation
    template_path = os.path.join("templates", "core.html")
    generate_html_presentation(title, sections, template_path, output_folder)

if __name__ == "__main__":
    main()
