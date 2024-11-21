# Import necessary modules
import os
import re
from bs4 import BeautifulSoup


def sanitize_title(title):
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

def generate_toc(sections):
    """
    Generate the Table of Contents (TOC) HTML based on the provided sections.

    Each section is represented as a clickable link in the sidebar.

    Args:
        sections (list): A list of dictionaries where each dictionary represents a section 
                        with a "title" and optional "content" and "folds".

    Returns:
        str: HTML string for the TOC links.
    """
    return ''.join(
        f'<a href="#" onclick="navigateTo({i}); return false;">{section["title"]}</a>'
        for i, section in enumerate(sections)
    )

def generate_section_content(sections):
    """
    Generate the HTML content for all sections of the presentation.

    Each section is enclosed in a <div> with class "section". 
    Supports:
    - Text content on the left.
    - Optional single image on the right, scaled appropriately.
    - Optional collapsible elements for additional details.
    - Optional dark background styling via 'dark' flag.

    Args:
        sections (list): A list of dictionaries where each dictionary represents a section.

    Returns:
        str: HTML string for all sections.
    """
    return ''.join(
        f'''
        <div id="section-{i}" class="section{" dark" if section.get("dark") else ""}">
            <div class="content-wrapper">
                <div class="text-content">
                    {"".join(f"{text}" for text in section.get("content", []))}
                    {"".join(
                        f'''
                        <button class="collapsible">{fold["title"]}</button>
                        <div class="content-panel">
                            {"".join(f"<p>{line}</p>" for line in fold["content"])}
                        </div>
                        ''' for fold in section.get("folds", [])
                    )}
                </div>
                {generate_image(section.get("image"))}
            </div>
        </div>
        '''
        for i, section in enumerate(sections)
    )

def generate_image(image_url):
    """
    Generate the HTML for a single image on the right side of a section.

    Args:
        image_url (str or None): The file name of the image (assumed to be in the same directory as the HTML file).

    Returns:
        str: HTML string for the image, or an empty string if no image is provided.
    """
    if not image_url:
        return ""
    
    # Ensure the image path is treated as local
    return f'''
    <div class="image-content">
        <img src="{image_url}" alt="Section Image">
    </div>
    '''


def generate_html_presentation(title, sections):
    """
    Generate a complete HTML presentation with a sidebar, content sections, 
    and JavaScript for interactivity.

    The generated file includes:
    - A constant, toggleable sidebar with Table of Contents (TOC).
    - Two-column layout in each section with text on the left and optional image on the right.
    - Collapsible elements for additional details within sections.
    - JavaScript functions for navigating between sections and toggling the sidebar.

    Args:
        title (str): The title of the presentation.
        sections (list): A list of dictionaries representing the presentation content.

    Output:
        Writes the generated HTML to a file named after the sanitized title.
    """
    # Sanitize title to create a safe filename
    sanitized_title = sanitize_title(title)
    output_file = f"{sanitized_title}.html"

    # Generate the TOC and sections content
    toc_html = generate_toc(sections)
    sections_html = generate_section_content(sections)

    # HTML template with placeholders for TOC and content
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        /* General styles */
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            display: flex;
            overflow: hidden;
        }}
        /* Sidebar styles */
        .sidebar {{
            position: fixed;
            top: 0;
            left: 0;
            bottom: 0;
            width: 250px;
            background: #333;
            color: white;
            overflow: hidden;
            transition: width 0.3s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 20px;
            box-sizing: border-box;
        }}
        .sidebar.minimized {{
            width: 40px;
        }}
        .sidebar h3 {{
            margin: 0;
            padding: 10px 0;
            text-align: center;
            font-size: 18px;
        }}
        .sidebar.minimized h3 {{
            display: none;
        }}
        .sidebar a {{
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            width: 100%;
            box-sizing: border-box;
        }}
        .sidebar a:hover {{
            background: #444;
        }}
        .toggle-tab {{
            position: absolute;
            right: 0;
            top: 50%;
            transform: translateY(-50%);
            background: #333;
            color: white;
            border: none;
            width: 20px;
            height: 40px;
            cursor: pointer;
            font-size: 14px;
            line-height: 40px; /* Center text vertically */
            border-radius: 0 5px 5px 0;
        }}
        .sidebar.minimized .toggle-tab {{
            transform: translateY(-50%) rotate(180deg);
        }}
        /* Container styles */
        .container {{
            margin-left: 250px;
            width: calc(100% - 250px);
            transition: margin-left 0.3s ease;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }}
        .sidebar.minimized + .container {{
            margin-left: 40px;
            width: calc(100% - 40px);
        }}
        .header {{
            background: #333;
            color: white;
            padding: 10px;
            text-align: center;
        }}
        .content {{
            flex: 1;
            overflow: hidden;
            position: relative;
        }}
        /* Section styles */
        .section {{
            display: none;
            width: 100%;
            height: 100%;
            overflow-y: auto;
            position: relative;
        }}
        .section.active {{
            display: block;
        }}
        .content-wrapper {{
            padding: 20px;
            display: flex;
            gap: 20px;
            justify-content: flex-start; /* Changed from center to flex-start */
            align-items: flex-start; /* Changed from center to flex-start */
            height: 100%;
            box-sizing: border-box;
        }}
        .text-content {{
            flex: 1;
            text-align: left; /* Changed from center to left */
        }}
        .image-content {{
            flex: 1;
        }}
        .image-content img {{
            width: 100%;
            height: auto;
        }}
        /* Dark theme for title slide */
        .section.dark {{
            background-color: #2c3e50;
            color: white;
        }}
        /* Collapsible content styles */
        .collapsible {{
            background-color: #e7e7e7;
            padding: 10px;
            border: none;
            width: 100%;
            text-align: left;
            font-size: 16px;
            margin-top: 10px;
            cursor: pointer;
            border-radius: 5px;
        }}
        .collapsible.active {{
            background-color: #ccc;
        }}
        .content-panel {{
            display: none;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }}
        .content-panel.active {{
            display: block;
        }}
        /* Overlay styles */
        .overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            cursor: pointer;
            z-index: 10;
        }}
    </style>
</head>
<body>
    <div class="sidebar" id="sidebar">
        <h3>Table of Contents</h3>
        <button class="toggle-tab" onclick="toggleSidebar()">&#10095;</button>
        {toc_html}
    </div>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
        </div>
        <div class="content" id="content">
            {sections_html}
        </div>
    </div>
    <script>
        let currentIndex = 0;
        const sections = document.querySelectorAll('.section');

        function toggleBackground(index) {{
            const body = document.body;
            if (index === 0) {{
                body.classList.add('dark-background');
            }} else {{
                body.classList.remove('dark-background');
            }}
        }}

        function navigateTo(index) {{
            if (index < 0 || index >= sections.length) return;
            sections[currentIndex].classList.remove('active');
            currentIndex = index;
            sections[currentIndex].classList.add('active');
            toggleBackground(index);
        }}

        function next() {{
            if (currentIndex < sections.length - 1) {{
                navigateTo(currentIndex + 1);
            }}
        }}

        function toggleSidebar() {{
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('minimized');
        }}

        document.getElementById('content').addEventListener('click', function(event) {{
            const tagName = event.target.tagName.toLowerCase();
            if (!['button', 'a', 'img', 'input', 'textarea'].includes(tagName)) {{
                next();
            }}
        }});

        document.querySelectorAll('.collapsible').forEach(button => {{
            button.addEventListener('click', () => {{
                button.classList.toggle('active');
                const panel = button.nextElementSibling;
                panel.classList.toggle('active');
            }});
        }});

        window.onload = function() {{
            if (sections.length > 0) {{
                sections[0].classList.add('active');
                toggleBackground(0);
            }}
        }};
    </script>
</body>
</html>
    """

    # Write the main presentation HTML to the specified file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"Presentation saved to {os.path.abspath(output_file)}")

def generate_final_slide():
    """
    Generate a standalone HTML final slide that displays "Thank you."
    """
    final_slide_filename = "thank_you.html"

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Thank You</title>
    <style>
        body, html {{
            margin: 0;
            width: 100%;
            height: 100%;
            font-family: Arial, sans-serif;
            background-color: #2c3e50;
            color: white;
            display: flex;
            justify-content: flex-start; /* Changed from center to flex-start */
            align-items: flex-start; /* Changed from center to flex-start */
            padding: 20px; /* Added padding */
            box-sizing: border-box;
        }}
        .final-content {{
            /* text-align: left; */ /* Already left-aligned by default */
        }}
        .final-content h1 {{
            font-size: 48px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="final-content">
        <h1>Thank You.</h1>
    </div>
</body>
</html>
    """

    with open(final_slide_filename, "w", encoding="utf-8") as f:
        f.write(html_template)
    print("Final slide saved as thank_you.html")

def append_overlay_to_final_slide(main_presentation_filename, final_slide_filename):
    """
    Append a fullscreen clickable overlay to the final section of the main presentation 
    that redirects to the final slide.

    Args:
        main_presentation_filename (str): The filename of the main presentation HTML.
        final_slide_filename (str): The filename of the final "Thank You" slide HTML.
    """
    # Read the main presentation HTML
    with open(main_presentation_filename, "r", encoding="utf-8") as f:
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
    with open(main_presentation_filename, "w", encoding="utf-8") as f:
        f.write(str(soup.prettify()))
    
    print(f"Overlay added to the final slide in {main_presentation_filename} to redirect to {final_slide_filename}")

    
#########

def main():
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
            "image": "https://via.placeholder.com/800x450.png?text=Introduction+Image"
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
            "image": "https://via.placeholder.com/800x450.png?text=Data+Preparation+Image"
        },
        {
            "title": "Modeling",
            "content": [
                "Overview of the predictive models used.",
                "Evaluation metrics and results interpretation."
            ],
            "image": "https://via.placeholder.com/800x450.png?text=Modeling+Image"
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

    # Generate the main presentation HTML
    generate_html_presentation(title, sections)
    main_presentation_filename = f"{sanitize_title(title)}.html"

    # Generate the final "Thank You" slide
    generate_final_slide()

    # Append the overlay to the final section of the main presentation
    final_slide_filename = "thank_you.html"
    append_overlay_to_final_slide(main_presentation_filename, final_slide_filename)

if __name__ == "__main__":
    main()
