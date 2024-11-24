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
            tocLinks[currentIndex - 1]?.blur(); // Ensure focus is cleared
        }
    
        // Update the global index and activate the new slide
        currentIndex = index;
        mainslides[currentIndex].classList.add('active');
    
        // Update TOC highlight
        if (currentIndex > 0) {
            updateTOCHighlight();
        } else {
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
    
        // Dispatch a custom event for slide changes
        const slideChangeEvent = new CustomEvent('slideChange', { detail: currentIndex });
        document.dispatchEvent(slideChangeEvent);
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
            event.preventDefault();      // Prevent default action
            event.stopPropagation();     // Stop event from bubbling up
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
            // Ignore clicks that originate from resizers
            if (event.target.classList.contains('column-resizer')) {
                log('Click ignored on resizer.');
                return; // Do not navigate if the click is on a resizer
            }

            // Ignore the next click if it was triggered by a resize action
            if (window.ignoreNextClick) {
                log('Click ignored due to resizing.');
                window.ignoreNextClick = false; // Reset the flag
                return;
            }

            // Ignore if any text is selected
            const selection = window.getSelection();
            if (selection && selection.toString().length > 0) {
                log('Click ignored due to text selection.');
                return;
            }

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
                navigateTo(index); // Navigate to the selected slide
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


// Global flag to track if an interactive action is in progress
window.ignoreNextClick = false;

// Global flag to track resizing state
window.isResizing = false;

const Resizer = (() => {
    function initializeResizers() {
        const columns = document.querySelectorAll('.column');

        columns.forEach(column => {
            const resizer = document.createElement('div');
            resizer.classList.add('column-resizer'); // Ensure the correct class is added
            column.appendChild(resizer);

            resizer.addEventListener('mousedown', initResize);

            // Prevent click events on resizer from propagating
            resizer.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        function initResize(e) {
            e.preventDefault(); // Prevent default browser behavior
            e.stopPropagation(); // Stop event from propagating
            window.isResizing = true; // Set the resizing flag to true
            window.ignoreNextClick = true; // Set the global flag to ignore the next click
            window.addEventListener('mousemove', startResizing);
            window.addEventListener('mouseup', stopResizing);
        }

        function startResizing(e) {
            const resizer = e.target;
            const column = resizer.parentElement;
            const prevColumn = column.previousElementSibling;
            const nextColumn = column.nextElementSibling;

            if (!prevColumn || !nextColumn) return;

            const containerWidth = prevColumn.parentElement.getBoundingClientRect().width;

            const mouseX = e.clientX;

            const newPrevWidth = mouseX - prevColumn.getBoundingClientRect().left;
            const newNextWidth = containerWidth - newPrevWidth - column.getBoundingClientRect().width - resizer.offsetWidth;

            // Optional: Set minimum widths
            if (newPrevWidth < 100 || newNextWidth < 100) return;

            // Calculate percentage widths
            const newPrevWidthPercent = (newPrevWidth / containerWidth) * 100;
            const newNextWidthPercent = (newNextWidth / containerWidth) * 100;

            prevColumn.style.flex = `0 0 ${newPrevWidthPercent}%`;
            nextColumn.style.flex = `0 0 ${newNextWidthPercent}%`;
        }

        function stopResizing(e) {
            window.removeEventListener('mousemove', startResizing);
            window.removeEventListener('mouseup', stopResizing);
            window.isResizing = false; // Unset the resizing flag

            // Reset the global flag after a short delay to allow any synthetic clicks to be ignored
            setTimeout(() => {
                window.ignoreNextClick = false;
            }, 200);
        }

        function saveColumnWidths() {
            const columns = document.querySelectorAll('.column');
            const widths = [];
            columns.forEach(column => {
                widths.push(column.style.flexBasis);
            });
            localStorage.setItem('columnWidths', JSON.stringify(widths));
        }
    }

    function loadColumnWidths() {
        const widths = JSON.parse(localStorage.getItem('columnWidths'));
        if (widths) {
            const columns = document.querySelectorAll('.column');
            columns.forEach((column, idx) => {
                if (widths[idx]) {
                    column.style.flex = `0 0 ${widths[idx]}`;
                }
            });
        }
    }

    return { initializeResizers, loadColumnWidths };
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
    Resizer.initializeResizers();
    Resizer.loadColumnWidths();
});

// Deactivate nextslide for resizableElements
document.addEventListener('DOMContentLoaded', function() {
    const resizableElements = document.querySelectorAll('.resizable');
    resizableElements.forEach(function(element) {
        element.addEventListener('click', function(event) {
            // Stop the click event from bubbling up to parent elements
            event.stopPropagation();
        });
    });
});


// Theme Switching

const themes = [
    "static/css/themes/style-dark.css",
    "static/css/themes/style-blue.css",
    "static/css/themes/style-seafoam.css"
];

let currentThemeIndex = 0;

// Function to switch themes
function switchTheme() {
    currentThemeIndex = (currentThemeIndex + 1) % themes.length; // Rotate to the next theme
    document.getElementById("theme-stylesheet").href = themes[currentThemeIndex];
}

// Add event listener for key combination
document.addEventListener("keydown", (event) => {
    if (event.ctrlKey && event.key === "ArrowUp") {
        // Ctrl + Up Arrow: Switch to the next theme
        switchTheme();
    } else if (event.ctrlKey && event.shiftKey && event.key === "ArrowUp") {
        // Ctrl + Shift + Up Arrow: Switch to the previous theme
        currentThemeIndex = (currentThemeIndex - 1 + themes.length) % themes.length;
        document.getElementById("theme-stylesheet").href = themes[currentThemeIndex];
    } else if (event.ctrlKey && event.shiftKey && event.key === "ArrowDown") {
        // Ctrl + Shift + Down Arrow: Switch to the next theme
        switchTheme();
    } else if (event.ctrlKey && event.key === "ArrowDown") {
        // Ctrl + Down Arrow: Switch to the previous theme
        currentThemeIndex = (currentThemeIndex - 1 + themes.length) % themes.length;
        document.getElementById("theme-stylesheet").href = themes[currentThemeIndex];
    }

    // Save the current theme index in localStorage
    localStorage.setItem("themeIndex", currentThemeIndex);
});

// Load the saved theme on page load
const savedThemeIndex = localStorage.getItem("themeIndex");
if (savedThemeIndex !== null) {
    currentThemeIndex = parseInt(savedThemeIndex, 0);
    document.getElementById("theme-stylesheet").href = themes[currentThemeIndex];
}


// Utility to center the active breadcrumb
function centerActiveBreadcrumb(index) {
    const breadcrumb = document.querySelector('.breadcrumb ol');
    const activeLink = breadcrumb.querySelectorAll('a')[index];

    if (activeLink) {
        // Smooth scroll to center the active breadcrumb
        activeLink.scrollIntoView({
            behavior: 'smooth',
            inline: 'center'
        });

        // Update active breadcrumb styling
        breadcrumb.querySelectorAll('a').forEach((link, i) => {
            if (i === index) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }
}

// Extend navigateTo to include breadcrumb centering
function navigateTo(index) {
    centerActiveBreadcrumb(index); // Center the breadcrumb
    slideManager.goToslide(index); // Trigger navigation to the slide
}

// Monitor slide changes for other navigation actions (e.g., clicks)
document.addEventListener('slideChange', (event) => {
    const { detail: slideIndex } = event;
    centerActiveBreadcrumb(slideIndex);
});


document.addEventListener('DOMContentLoaded', () => {
    const breadcrumbList = document.querySelector('.breadcrumb ol');

    if (breadcrumbList) {
        // Debounce function for smoother scrolling
        let scrollTimeout = null;

        breadcrumbList.addEventListener('wheel', (event) => {
            event.preventDefault();
            const delta = event.deltaY || event.deltaX; // Support for different scrolling inputs
            
            // Smooth horizontal scrolling
            breadcrumbList.scrollLeft += delta;

            // Debounce active updates
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            scrollTimeout = setTimeout(() => {
                // Optionally, update visible breadcrumb indicators here
            }, 50);
        });
    }
});
