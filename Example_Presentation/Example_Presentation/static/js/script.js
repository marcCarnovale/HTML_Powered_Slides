// static/js/script.js

// Utility Functions
function log(message, type = "log") {
    console[type](message);
}

const slideManager = (() => {
    let currentIndex = 0; // Tracks the currently active slide
    const mainslides = document.querySelectorAll('.slide');
    const tocLinks = document.querySelectorAll('.sidebar a');

    function initialize() {
        if (mainslides.length > 0) {
            currentIndex = 0; // Start at the first slide
            mainslides[currentIndex].classList.add('active'); // Mark the first slide as active
            document.body.classList.add('dark-background'); // Add dark theme for the first slide
            log('Initialized with the first slide active.');
            BreadcrumbManager.updateBreadcrumb();
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

    function goToslide(index) {
        if (index < 0 || index >= mainslides.length) {
            log(`Invalid slide index: ${index}`, "error");
            return;
        }

        // Deactivate current slide and update TOC
        mainslides[currentIndex]?.classList.remove('active');
        if (currentIndex > 0) {
            tocLinks[currentIndex - 1]?.classList.remove('active');
        }

        // Update the global index and activate the new slide
        currentIndex = index;
        mainslides[currentIndex].classList.add('active');

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

        log(`Navigated to slide index: ${currentIndex}`);
        BreadcrumbManager.updateBreadcrumb();
    }

    function nextslide() {
        if (currentIndex < mainslides.length - 1) {
            goToslide(currentIndex + 1);
        } else {
            log('Already on the last slide. No further navigation.');
        }
    }

    function previousslide() {
        if (currentIndex > 0) {
            goToslide(currentIndex - 1);
        } else {
            log('Already on the first slide. No further navigation.');
        }
    }

    function setupKeyboardNavigation() {
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Backspace') {
                event.preventDefault(); // Prevent default back navigation in the browser
                previousslide();
            } else if (event.key === 'ArrowRight') {
                nextslide();
            } else if (event.key === 'ArrowLeft') {
                previousslide();
            }
        });
    }

    return { initialize, goToslide, nextslide, previousslide, setupKeyboardNavigation };
})();


// TOC Management
const TOCManager = (() => {
    function setupTOCNavigation() {
        const tocLinks = document.querySelectorAll('.sidebar a');
        tocLinks.forEach((link, index) => {
            link.addEventListener('click', (event) => {
                event.preventDefault();
                slideManager.goToslide(index + 1); // Adjust for TOC starting after title slide
            });
        });
    }

    return { setupTOCNavigation };
})();

// Chart Management
const ChartManager = (() => {
    function initializeCharts() {
        const charts = document.querySelectorAll('.chart-container');
        charts.forEach(chartEl => {
            if (chartEl.dataset.chartInitialized) {
                return; // Prevent multiple initializations
            }

            const ctx = chartEl.querySelector('canvas').getContext('2d');
            let chartData;
            try {
                chartData = JSON.parse(chartEl.getAttribute('data-chart-data'));
            } catch (e) {
                log(`Invalid chart data in panel: ${chartEl.id}`, "error");
                return;
            }

            new Chart(ctx, {
                type: chartData.type,
                data: chartData.data,
                options: chartData.options,
            });

            chartEl.dataset.chartInitialized = true;
            log(`Initialized chart in panel: ${chartEl.id}`);
        });
    }

    return { initializeCharts };
})();


// Collapsible Management (Refactored for Modularity and Accessibility)
const CollapsibleManager = (() => {
    // Initialize a single collapsible button
    function initializeCollapsible(button) {
        // Determine nesting level for styling
        let level = 1;
        let parent = button.parentElement;
        while (parent && parent.classList.contains('content-panel')) {
            level++;
            parent = parent.parentElement;
        }
        button.classList.add(`level-${level}`);

        // Ensure ARIA attributes are set
        button.setAttribute('role', 'button');
        button.setAttribute('aria-expanded', 'false');

        // Click event handler
        button.addEventListener('click', (event) => {
            event.stopPropagation(); // Prevent event bubbling to parent elements
            log(`Collapsible button clicked: ${button.textContent}`);
            const isActive = button.classList.toggle('active');
            const panelId = button.getAttribute('aria-controls');
            const panel = document.getElementById(panelId);

            if (panel) {
                panel.classList.toggle('active');
                log(`Toggled panel: ${panelId}, Now Active: ${panel.classList.contains('active')}`);

                // If panel becomes active, initialize any charts inside it
                if (panel.classList.contains('active')) {
                    ChartManager.initializeCharts();
                }

                // Update aria-expanded attribute for accessibility
                button.setAttribute('aria-expanded', isActive);
            } else {
                log(`Panel with id '${panelId}' not found.`, "error");
            }
        });

        // Enable keyboard accessibility
        button.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                button.click();
            }
        });
    }

    // Set up all collapsibles
    function setupCollapsibles() {
        const collapsibles = document.querySelectorAll('.collapsible');
        log(`Found ${collapsibles.length} collapsible buttons.`);
        collapsibles.forEach(initializeCollapsible); // Use the helper function
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

            // Navigate to the next slide
            slideManager.nextslide();
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


const BreadcrumbManager = (() => {
    function updateBreadcrumb() {
        const breadcrumbs = document.querySelector('.breadcrumb ol');
        const mainslides = document.querySelectorAll('.slide');
        const breadcrumbLinks = breadcrumbs.querySelectorAll('a');

        mainslides.forEach((slide, index) => {
            if (slide.classList.contains('active')) {
                breadcrumbLinks.forEach((link, i) => {
                    if (i === index) {
                        link.classList.add('active');
                    } else {
                        link.classList.remove('active');
                    }
                });
            }
        });
    }

    function setupBreadcrumbNavigation() {
        const breadcrumbLinks = document.querySelectorAll('.breadcrumb a');
        breadcrumbLinks.forEach((link, index) => {
            link.addEventListener('click', (event) => {
                event.preventDefault();
                slideManager.goToslide(index); // Navigate to the selected slide
            });
        });
    }

    return { updateBreadcrumb, setupBreadcrumbNavigation };
})();

// Content-First Mode Management
const ContentFirstManager = (() => {
    function setupContentFirstToggle() {
        const toggleButton = document.getElementById('toggle-content-first');
        if (!toggleButton) {
            log('Content-First toggle button not found.', 'error');
            return;
        }

        toggleButton.addEventListener('click', () => {
            document.body.classList.toggle('content-first');
            const isContentFirst = document.body.classList.contains('content-first');
            toggleButton.textContent = isContentFirst ? 'Show Sidebar' : 'Hide Sidebar';
            log(`Content-First mode toggled. Now content-first: ${isContentFirst}`);
        });
    }

    return { setupContentFirstToggle };
})();

// Initialize Everything
document.addEventListener('DOMContentLoaded', () => {
    slideManager.initialize();
    slideManager.setupKeyboardNavigation(); // Enable keyboard navigation
    TOCManager.setupTOCNavigation();
    BreadcrumbManager.setupBreadcrumbNavigation(); // Initialize breadcrumb navigation
    BreadcrumbManager.updateBreadcrumb(); // Initialize breadcrumb state
    CollapsibleManager.setupCollapsibles();
    ContentManager.setupContentClick();
    SidebarManager.setupSidebarToggle();
    ContentFirstManager.setupContentFirstToggle(); // Initialize Content-First toggle
});
