from helper import generate_breadcrumbs, generate_slide_content, generate_toc, sanitize_title
from main import PROJECT_ROOT, generate_html_presentation, load_configuration


def test_sanitize_title_is_filesystem_friendly():
    assert sanitize_title("A Presentation: 2026!") == "A_Presentation_2026"


def test_minimal_config_generates_expected_sections(tmp_path):
    config = load_configuration(str(PROJECT_ROOT / "examples" / "minimal.yaml"))
    output_name = generate_html_presentation(
        title=config["title"],
        slides=config["slides"],
        template_path=str(PROJECT_ROOT / "templates" / "core.html"),
        output_folder=str(tmp_path),
        theme_css="style-dark.css",
    )
    rendered = (tmp_path / output_name).read_text(encoding="utf-8")
    assert "Minimal Example" in rendered
    assert "One idea" in rendered
    assert "More detail" in rendered
    assert "style-dark.css" in rendered


def test_navigation_helpers_are_deterministic():
    slides = [{"title": "First", "content": ["plain"]}, {"title": "Second"}]
    assert generate_toc(slides) == generate_toc(slides)
    assert generate_breadcrumbs(slides) == generate_breadcrumbs(slides)
    assert generate_slide_content(slides) == generate_slide_content(slides)
