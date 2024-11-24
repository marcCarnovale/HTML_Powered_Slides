# main.py
import argparse
import os
import json
import yaml
import shutil
from typing import Dict, Any, List, Tuple
from helper import (
    sanitize_title,
    generate_toc,
    generate_slide_content,
    copy_project_images,
    generate_breadcrumbs
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
    slides: List[Dict[str, Any]],
    template_path: str,
    output_folder: str,
    theme_css: str
) -> str:
    """
    Generates the main presentation HTML file using the core template.
    
    Args:
        title (str): The title of the presentation.
        slides (List[Dict[str, Any]]): A list of slide dictionaries.
        template_path (str): Path to the core HTML template.
        output_folder (str): Path to the output directory.
        theme_css (str): The CSS file name for the selected theme.
    
    Returns:
        str: Filename of the generated main presentation HTML.
    """
    # Read the core HTML template as string
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Generate TOC and slides
    toc_html = generate_toc(slides)
    # Generate Breadcrumbs HTML
    breadcrumbs_html = generate_breadcrumbs(slides)
    # Generate slides
    slides_html = generate_slide_content(slides)

    # Replace placeholders
    html_content = html_content.replace("{{title}}", title)
    html_content = html_content.replace("{{toc}}", toc_html)
    html_content = html_content.replace("{{slides}}", slides_html)
    html_content = html_content.replace("{{breadcrumbs}}", breadcrumbs_html)
    html_content = html_content.replace("{{theme_css}}", theme_css)

    # Write the main presentation HTML to the output folder
    sanitized_title = sanitize_title(title)
    main_presentation_filename = f"{sanitized_title}.html"
    output_path = os.path.join(output_folder, main_presentation_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Main presentation saved to {output_path}")
    return main_presentation_filename

def copy_static_files(output_folder: str):
    """
    Copies static files (CSS and JS) to the output directory.
    
    Args:
        output_folder (str): Path to the output directory.
    
    Returns:
        None
    """
    # Define source and destination paths
    source_css_folder = "static/css"
    source_js_folder = "static/js"

    # Destination paths
    dest_css_folder = os.path.join(output_folder, "static", "css")
    dest_js_folder = os.path.join(output_folder, "static", "js")

    # Create destination directories
    os.makedirs(dest_css_folder, exist_ok=True)
    os.makedirs(dest_js_folder, exist_ok=True)

    # Copy core.css
    core_css_source = os.path.join(source_css_folder, "core.css")
    core_css_dest = os.path.join(dest_css_folder, "core.css")
    if os.path.isfile(core_css_source):
        shutil.copy(core_css_source, core_css_dest)
        print(f"Copied core CSS to {core_css_dest}")
    else:
        print(f"Core CSS file not found at {core_css_source}.")
        exit(1)

    # Copy script.js
    script_js_source = os.path.join(source_js_folder, "script.js")
    script_js_dest = os.path.join(dest_js_folder, "script.js")
    if os.path.isfile(script_js_source):
        shutil.copy(script_js_source, script_js_dest)
        print(f"Copied JavaScript file to {script_js_dest}")
    else:
        print(f"JavaScript file not found at {script_js_source}.")
        exit(1)


#######################################################################

sample_title = "Presentation System Overview"
sample_author = "Marc Carnovale"
sample_date = "November 21, 2024"
sample_slides = [
    {
        "title": "",  # Title slide
        "html-content": [
            f"<h1>{sample_title}</h1>",
            f"<h3>by {sample_author}</h3>",
            f"<p>{sample_date}</p>"
        ],
        "dark": True
    },
    {
        "title": "Introduction",
        "content": [
            "<p>Welcome to our advanced Presentation System.</p>",
            "<p>Designed for maximum flexibility and efficiency, leveraging the power of HTML and modern web technologies.</p>"
        ],
        "folds": [
            {
                "title": "Core Principles",
                "content": [
                    "<p>Emphasis on information density and clarity.</p>",
                    "<p>Minimalist design inspired by Tufte's philosophy.</p>"
                ],
                "folds": [
                    {
                        "title": "Information Density",
                        "content": [
                            "<p>Maximizing data presentation without clutter.</p>"
                        ]
                    },
                    {
                        "title": "Clarity",
                        "content": [
                            "<p>Ensuring information is easily understandable.</p>"
                        ]
                    }
                ]
            },
            {
                "title": "System Highlights",
                "content": [
                    "<p>Robust HTML-based architecture.</p>",
                    "<p>Seamless integration with LLMs for dynamic slide creation.</p>"
                ]
            }
        ],
        "image": "introduction_image.png"
    },
    {
        "title": "Features",
        "content": [
            "<h2>Key Features</h2>",
            "<ul>",
            "<li>Dynamic Resizing and Reflow</li>",
            "<li>Nested Folds for Hierarchical Information</li>",
            "<li>Flexible Column and Row Layouts</li>",
            "<li>Rich Multimedia Support</li>",
            "<li>Interactive Elements and Charts</li>",
            "<li>Accessibility Compliance</li>",
            "</ul>"
        ],
        "folds": [
            {
                "title": "Dynamic Resizing",
                "content": [
                    "<p>Elegant resizing and reflow capabilities ensure content adapts to various screen sizes.</p>"
                ]
            },
            {
                "title": "Nested Folds",
                "content": [
                    "<p>Organize information hierarchically with collapsible sections.</p>"
                ]
            }
        ],
        "image": "features_image.png"
    },
    {
        "title": "Flexibility of HTML",
        "content": [
            "<h2>Leveraging HTML's Flexibility</h2>",
            "<p>Our system harnesses the mature and versatile nature of HTML to provide a robust framework for presentations.</p>",
            "<p>Benefits include:</p>",
            "<ul>",
            "<li>Wide compatibility across devices and browsers.</li>",
            "<li>Extensive multimedia integration.</li>",
            "<li>Ease of customization and styling.</li>",
            "</ul>"
        ],
        "folds": [
            {
                "title": "Responsive Design",
                "content": [
                    "<p>Slides automatically adjust layout for optimal viewing on any device.</p>"
                ]
            },
            {
                "title": "Multimedia Support",
                "content": [
                    "<p>Embed videos, images, charts, and interactive content seamlessly.</p>"
                ]
            }
        ],
        "image": "html_flexibility.png"
    },
    {
        "title": "Information Density",
        "content": [
            "<h2>Maximizing Information Density</h2>",
            "<p>Inspired by Tufte, our system prioritizes the presentation of rich information without unnecessary distractions.</p>",
            "<p>Strategies include:</p>",
            "<ul>",
            "<li>Minimalist design with ample white space.</li>",
            "<li>Clear hierarchies through typography and layout.</li>",
            "<li>Focus on data-driven content.</li>",
            "</ul>"
        ],
        "folds": [
            {
                "title": "Minimalist Design",
                "content": [
                    "<p>Clean layouts that emphasize content over decoration.</p>"
                ]
            },
            {
                "title": "Clear Hierarchies",
                "content": [
                    "<p>Use of headings, bullet points, and indentation to organize information.</p>"
                ]
            }
        ],
        "image": "information_density.png"
    },
    {
        "title": "Current Features",
        "content": [
            "<h2>What We've Enabled So Far</h2>",
            "<ul>",
            "<li>Nested Folds with Varying Backgrounds</li>",
            "<li>Flexible Column and Row Configurations</li>",
            "<li>Interactive Charts and Multimedia Embeds</li>",
            "<li>Responsive and Accessible Design</li>",
            "<li>Easy Slide Creation via Dictionary-Based Configuration</li>",
            "</ul>"
        ],
        "folds": [
            {
                "title": "Nested Folds",
                "content": [
                    "<p>Create hierarchical content structures with ease.</p>"
                ]
            },
            {
                "title": "Interactive Charts",
                "content": [
                    "<p>Embed dynamic charts to visualize data effectively.</p>"
                ]
            }
        ],
        "image": "current_features.png"
    },
    {
        "title": "Future Features",
        "content": [
            "<h2>Planned Enhancements</h2>",
            "<ul>",
            "<li>Real-Time Collaboration Tools</li>",
            "<li>Advanced Animation and Transition Effects</li>",
            "<li>Integration with External Data Sources</li>",
            "<li>Customizable Templates and Themes</li>",
            "<li>Enhanced Accessibility Features</li>",
            "</ul>"
        ],
        "folds": [
            {
                "title": "Real-Time Collaboration",
                "content": [
                    "<p>Enable multiple users to edit and interact with presentations simultaneously.</p>"
                ]
            },
            {
                "title": "Advanced Animations",
                "content": [
                    "<p>Incorporate smooth animations and transitions for engaging presentations.</p>"
                ]
            },
            {
                "title": "Data Integration",
                "content": [
                    "<p>Connect to APIs and databases for dynamic data-driven slides.</p>"
                ]
            }
        ],
        "image": "future_features.png"
    },
    {
        "title": "Building Slides with LLMs",
        "content": [
            "<h2>Seamless Slide Creation via LLMs</h2>",
            "<p>Our system is designed to work hand-in-hand with powerful Language Models like ChatGPT, enabling effortless slide generation and customization.</p>",
            "<p>Advantages include:</p>",
            "<ul>",
            "<li>Rapid creation from conversational inputs.</li>",
            "<li>Easy updates and modifications through dialogue.</li>",
            "<li>Incorporation of complex data and multimedia with simple instructions.</li>",
            "</ul>"
        ],
        "folds": [
            {
                "title": "Conversational Slide Generation",
                "content": [
                    "<p>Generate detailed slides through natural language prompts.</p>"
                ]
            },
            {
                "title": "Dynamic Content Updates",
                "content": [
                    "<p>Modify existing slides by requesting changes in an interactive manner.</p>"
                ]
            }
        ],
        "image": "llm_integration.png"
    },
    {
        "title": "How It Works",
        "content": [
            "<h2>System Architecture</h2>",
            "<p>Our presentation system leverages a dictionary-based configuration approach, allowing for structured and scalable slide creation.</p>",
            "<p>Key Components:</p>",
            "<ul>",
            "<li>Dictionary Definitions for Slides and Content</li>",
            "<li>Helper Functions for HTML and CSS Generation</li>",
            "<li>CSS Framework for Styling and Responsiveness</li>",
            "<li>JavaScript for Interactivity and Dynamic Features</li>",
            "</ul>"
        ],
        "folds": [
            {
                "title": "Dictionary-Based Configuration",
                "content": [
                    "<p>Define slides, content, and layouts using simple Python dictionaries.</p>"
                ]
            },
            {
                "title": "Helper Functions",
                "content": [
                    "<p>Automate the generation of HTML and CSS based on configurations.</p>"
                ]
            }
        ],
        "image": "system_architecture.png"
    },
    {
        "title": "Use Cases",
        "content": [
            "<h2>Applications of Our Presentation System</h2>",
            "<ul>",
            "<li>Educational Lectures and Tutorials</li>",
            "<li>Business Presentations and Reports</li>",
            "<li>Technical Documentation and Demos</li>",
            "<li>Interactive Workshops and Webinars</li>",
            "</ul>"
        ],
        "folds": [
            {
                "title": "Educational Use",
                "content": [
                    "<p>Create detailed, information-dense slides for effective teaching.</p>"
                ]
            },
            {
                "title": "Business Applications",
                "content": [
                    "<p>Develop professional presentations with dynamic data visualizations.</p>"
                ]
            }
        ],
        "image": "use_cases.png"
    },
    {
        "title": "Technical Overview",
        "content": [
            "<h2>Under the Hood</h2>",
            "<p>The system is built using modern web technologies to ensure performance, scalability, and ease of use.</p>",
            "<p>Technologies Used:</p>",
            "<ul>",
            "<li>HTML5 and CSS3 for structure and styling.</li>",
            "<li>JavaScript for interactivity.</li>",
            "<li>Python for configuration and helper scripts.</li>",
            "<li>Chart.js for data visualization.</li>",
            "</ul>"
        ],
        "folds": [
            {
                "title": "Front-End Technologies",
                "content": [
                    "<p>HTML and CSS provide a robust foundation for responsive design.</p>"
                ]
            },
            {
                "title": "Back-End Integration",
                "content": [
                    "<p>Python scripts automate the generation of slide content and structure.</p>"
                ]
            }
        ],
        "image": "technical_overview.png"
    },
    {
        "title": "Extensibility",
        "content": [
            "<h2>Highly Extensible and Customizable</h2>",
            "<p>Our system is designed to be easily extended to meet diverse presentation needs.</p>",
            "<p>Customization Options:</p>",
            "<ul>",
            "<li>Custom CSS Themes and Styles</li>",
            "<li>Integration with Third-Party APIs</li>",
            "<li>Adding New Content Types and Components</li>",
            "<li>Localization and Internationalization Support</li>",
            "</ul>"
        ],
        "folds": [
            {
                "title": "Custom Themes",
                "content": [
                    "<p>Apply different color schemes and layouts to match branding.</p>"
                ]
            },
            {
                "title": "API Integrations",
                "content": [
                    "<p>Connect to external data sources for real-time content updates.</p>"
                ]
            }
        ],
        "image": "extensibility.png"
    },
    {
        "title": "Accessibility",
        "content": [
            "<h2>Commitment to Accessibility</h2>",
            "<p>Ensuring that our presentation system is usable by everyone, including those with disabilities.</p>",
            "<p>Accessibility Features:</p>",
            "<ul>",
            "<li>Keyboard Navigable Interfaces</li>",
            "<li>Screen Reader Compatibility</li>",
            "<li>High Contrast Modes</li>",
            "<li>ARIA Attributes for Enhanced Semantics</li>",
            "</ul>"
        ],
        "folds": [
            {
                "title": "Keyboard Navigation",
                "content": [
                    "<p>All interactive elements are accessible via keyboard controls.</p>"
                ]
            },
            {
                "title": "Screen Reader Support",
                "content": [
                    "<p>Semantic HTML and ARIA attributes improve compatibility with assistive technologies.</p>"
                ]
            }
        ],
        "image": "accessibility.png"
    },
    {
        "title": "Multimedia Support",
        "content": [
            "<h2>Rich Multimedia Integration</h2>",
            "<p>Enhance your presentations with a variety of multimedia elements.</p>",
            "<p>Supported Multimedia Types:</p>",
            "<ul>",
            "<li>Images and Galleries</li>",
            "<li>Embedded Videos and Audio</li>",
            "<li>Interactive Charts and Graphs</li>",
            "<li>Animations and Transitions</li>",
            "</ul>"
        ],
        "folds": [
            {
                "title": "Embedded Media",
                "content": [
                    "<p>Seamlessly incorporate videos and audio clips for dynamic content delivery.</p>"
                ]
            },
            {
                "title": "Interactive Visuals",
                "content": [
                    "<p>Use tools like Chart.js to create engaging data visualizations.</p>"
                ]
            }
        ],
        "image": "multimedia_support.png"
    },
    {
        "title": "Performance Metrics",
        "content": [
            "<h2>System Performance</h2>",
            "<p>Optimized for fast load times and smooth interactions.</p>",
            "<p>Key Metrics:</p>",
            "<ul>",
            "<li>Average Slide Load Time: <strong>200ms</strong></li>",
            "<li>Responsive Design Efficiency: <strong>High</strong></li>",
            "<li>Scalability: Supports presentations with up to <strong>100 slides</strong></li>",
            "<li>Resource Utilization: Minimal CPU and Memory usage</li>",
            "</ul>"
        ],
        "folds": [
            {
                "title": "Load Times",
                "content": [
                    "<p>Slides load almost instantaneously, ensuring a seamless viewing experience.</p>"
                ]
            },
            {
                "title": "Scalability",
                "content": [
                    "<p>Efficiently handles large presentations without performance degradation.</p>"
                ]
            }
        ],
        "image": "performance_metrics.png"
    },
    {
        "title": "Conclusion",
        "content": [
            "<h2>Why Choose Our Presentation System?</h2>",
            "<ul>",
            "<li>Unparalleled Flexibility and Customization</li>",
            "<li>High Information Density with Clarity</li>",
            "<li>Seamless Integration with Modern Technologies</li>",
            "<li>Accessible and Inclusive Design</li>",
            "<li>Future-Proof and Extensible Architecture</li>",
            "</ul>",
            "<p>Empower your presentations with a system built for clarity, efficiency, and scalability.</p>"
        ],
        "image": "conclusion_image.png"
    },
    {
        "title": "Thank You",
        "html-content": [
            "<h2>Thank You!</h2>",
            "<p>Your questions?</p>",
            "<p>Feel free to reach out for further discussions.</p>"
        ],
    }
]



def main(): 
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate an HTML presentation with theming support.")
    parser.add_argument('--output_dir', type=str, default=None,
                        help='Path to the output directory. Defaults to a folder named after the presentation title.')
    parser.add_argument('--images_dir', type=str, default=None,
                        help='Path to the images directory. If not specified, images are assumed to be in the output directory\'s "images/" folder.')
    parser.add_argument('--config', type=str, default=None,
                        help='Path to the presentation configuration file (JSON or YAML).')
    parser.add_argument('--theme', type=str, default='dark',
                        choices=['dark', 'blue', 'forest', 'seafoam'],
                        help='Theme of the presentation. Options: "dark" (default), "blue", "forest", "seafoam".')
    args = parser.parse_args()

    # Load presentation configuration
    if args.config:
        config = load_configuration(args.config)
        title = config.get("title", "Untitled Presentation")
        author = config.get("author", "Unknown Author")
        date = config.get("date", "Unknown Date")
        slides = config.get("slides", sample_slides)
    else:
        # Default presentation details
        title = sample_title
        author = sample_author
        date = sample_date
        slides = sample_slides

    # Determine output directory
    if args.output_dir:
        output_folder = args.output_dir
    else:
        sanitized_title = sanitize_title(title)
        output_folder = os.path.join("output", sanitized_title)

    os.makedirs(output_folder, exist_ok=True)

    # Copy images to output folder
    destination_images_folder = os.path.join(output_folder, "images")
    copy_project_images(slides, args.images_dir, destination_images_folder)

    # Copy static files (JS)
    copy_static_files(output_folder)

    # Determine the theme CSS file
    theme_mapping = {
        'dark': 'style-dark.css',
        'blue': 'style-blue.css',
        'seafoam': 'style-seafoam.css',
        'forest': 'style-forest.css',
    }

    selected_theme = args.theme.lower()
    theme_css = theme_mapping.get(selected_theme)

    if not theme_css:
        print(f"Theme '{selected_theme}' is not recognized. Falling back to 'dark' theme.")
        theme_css = 'style-dark.css'

    # Verify that the selected theme CSS file exists
    theme_source_path = os.path.join("static", "css", "themes", theme_css)
    if not os.path.isfile(theme_source_path):
        print(f"Theme CSS file '{theme_css}' not found in 'static/css/themes/' directory.")
        print("Available themes:", ', '.join(theme_mapping.values()))
        exit(1)

    # Copy the selected theme CSS to the output directory's 'static/css/themes/' folder
    destination_themes_folder = os.path.join(output_folder, "static", "css", "themes")
    os.makedirs(destination_themes_folder, exist_ok=True)
    shutil.copy(theme_source_path, destination_themes_folder)
    print(f"Copied theme CSS '{theme_css}' to '{destination_themes_folder}'.")

    # Copy alt themes
    for theme in ["style-dark.css", "style-blue.css", "style-seafoam.css"]:
        if theme not in os.listdir(destination_images_folder) :
            theme_source_path = os.path.join("static", "css", "themes", theme)
            shutil.copy(theme_source_path, destination_themes_folder)
            print(f"Copied theme CSS '{theme}' to '{destination_themes_folder}'.")

    # Generate HTML presentation
    template_path = os.path.join("templates", "core.html")
    generate_html_presentation(title, slides, template_path, output_folder, theme_css)

if __name__ == "__main__":
    main()
