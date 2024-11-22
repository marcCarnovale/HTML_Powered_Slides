// static/js/script.js

// Utility Functions
function log(message, type = "log") {
    console[type](message);
}

// Section Management
const SectionManager = (() => {
    let currentIndex = 0; // Tracks the currently active section
    const mainSections = document.querySelectorAll('.section');
    const tocLinks = document.querySelectorAll('.sidebar a');

    function initialize() {
        if (mainSections.length > 0) {
            currentIndex = 0; // Start at the first section
            mainSections[currentIndex].classList.add('active'); // Mark the first slide as active
            document.body.classList.add('dark-background'); // Add dark theme for the first slide
            log('Initialized with the first slide active.');
        }
    }

    function updateTOCHighlight() {
        tocLinks.forEach((link, index) => {
            if (index === currentIndex - 1) { // Adjust for TOC starting after title slide
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    function goToSection(index) {
        if (index < 0 || index >= mainSections.length) {
            log(`Invalid section index: ${index}`, "error");
            return;
        }

        // Deactivate current section and update TOC
        mainSections[currentIndex]?.classList.remove('active');
        if (currentIndex > 0) {
            tocLinks[currentIndex - 1]?.classList.remove('active');
        }

        // Update the global index and activate the new section
        currentIndex = index;
        mainSections[currentIndex].classList.add('active');

        // Update TOC highlight
        if (currentIndex > 0) {
            updateTOCHighlight();
        } else {
            // If navigating to the first slide, ensure no TOC links are active
            tocLinks.forEach(link => link.classList.remove('active'));
        }

        // Update body background for the first slide
        if (currentIndex === 0) {
            document.body.classList.add('dark-background');
        } else {
            document.body.classList.remove('dark-background');
        }

        log(`Navigated to section index: ${currentIndex}`);
    }

    function nextSection() {
        if (currentIndex < mainSections.length - 1) {
            goToSection(currentIndex + 1);
        } else {
            log('Already on the last section. No further navigation.');
        }
    }

    return { initialize, goToSection, nextSection };
})();

// TOC Management
const TOCManager = (() => {
    function setupTOCNavigation() {
        const tocLinks = document.querySelectorAll('.sidebar a');
        tocLinks.forEach((link, index) => {
            link.addEventListener('click', (event) => {
                event.preventDefault();
                SectionManager.goToSection(index + 1); // Adjust for TOC starting after title slide
            });
        });
    }

    return { setupTOCNavigation };
})();

// Collapsible Management
const CollapsibleManager = (() => {
    function setupCollapsibles() {
        const collapsibles = document.querySelectorAll('.collapsible');
        log(`Found ${collapsibles.length} collapsible buttons.`);
        collapsibles.forEach(button => {
            button.addEventListener('click', (event) => {
                event.stopPropagation(); // Prevent event bubbling to parent elements
                log(`Collapsible button clicked: ${button.textContent}`);
                button.classList.toggle('active');
                const panelId = button.getAttribute('aria-controls');
                const panel = document.getElementById(panelId);

                if (panel) {
                    panel.classList.toggle('active');
                    log(`Toggled panel: ${panelId}, Now Active: ${panel.classList.contains('active')}`);

                    // No need to manipulate maxHeight in JS; CSS handles transitions
                    // Remove any inline styles to rely solely on CSS for transitions
                    panel.style.maxHeight = null;

                    // Update aria-expanded attribute for accessibility
                    button.setAttribute('aria-expanded', button.classList.contains('active'));
                } else {
                    log(`Panel with id '${panelId}' not found.`, "error");
                }
            });
        });
    }

    return { setupCollapsibles };
})();

// Content Click Handling
const ContentManager = (() => {
    function setupContentClick() {
        const content = document.getElementById('content');
        if (!content) {
            log('Content container not found.', 'error');
            return;
        }

        content.addEventListener('click', function (event) {
            const tagName = event.target.tagName.toLowerCase();
            const collapsible = event.target.closest('.collapsible');
            const panel = event.target.closest('.content-panel');

            // Ignore clicks on collapsibles, panels, or interactive elements
            if (collapsible || panel || ['button', 'a', 'img', 'input', 'textarea'].includes(tagName)) {
                log('Click ignored on collapsible, panel, or interactive element.');
                return;
            }

            // Navigate to the next section
            SectionManager.nextSection();
        });
    }

    return { setupContentClick };
})();

// Sidebar Management
const SidebarManager = (() => {
    function setupSidebarToggle() {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) {
            log('Sidebar not found.', 'error');
            return;
        }

        window.toggleSidebar = function () {
            sidebar.classList.toggle('minimized');
            log(`Sidebar toggled. Now minimized: ${sidebar.classList.contains('minimized')}`);
        };
    }

    return { setupSidebarToggle };
})();

// Initialize Everything
document.addEventListener('DOMContentLoaded', () => {
    SectionManager.initialize();
    TOCManager.setupTOCNavigation();
    CollapsibleManager.setupCollapsibles();
    ContentManager.setupContentClick();
    SidebarManager.setupSidebarToggle();
});
