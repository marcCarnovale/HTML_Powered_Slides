# Theming Guide

This documentation explains how to use, create, and apply custom themes for your presentation.

---

## **Overview**
Themes allow you to customize the visual appearance of your presentation by using separate CSS files. Each theme is stored in the `static/css/themes/` directory and can be dynamically applied.

---

## **Available Themes**
### **Default Themes**
1. **Dark Theme**:
   - A minimalist, professional dark-grey theme.
   - File: `style-dark.css`

2. **Blue Theme**:
   - A clean, light-blue theme for modern presentations.
   - File: `style-blue.css`

---

## **How to Apply a Theme**
1. **Modify the HTML**:
   - In your `core.html` file, locate the following line:
     ```html
     <link id="theme-stylesheet" rel="stylesheet" href="static/css/themes/{{theme_css}}">
     ```
   - Set the `theme_css` variable to the desired theme file, e.g., `"style-dark.css"` or `"style-blue.css"`.
   
2. **Set the Theme Programmatically**:
   - If you're using a generator script, ensure that the `theme_css` variable is included in your configuration.

---

## **How to Create a Custom Theme**
You can create custom themes by following these steps:

### 1. **Create a New CSS File**
- Navigate to the `static/css/themes/` directory.
- Create a new file, e.g., `style-yourtheme.css`. Replace `yourtheme` with your preferred name.

### 2. **Define CSS Variables**
Use CSS variables to manage the primary colors and reusable styles of your theme. Below is an example:
```css
:root {
    --sidebar-bg: #ffcc00;           /* Sidebar background color */
    --sidebar-hover-bg: #ff9900;    /* Sidebar hover and active link color */
    --toggle-bg: #ffcc00;           /* Sidebar toggle button color */
    --header-bg: #ffcc00;           /* Header background color */
    --collapsible-bg: #fff2cc;      /* Collapsible button background color */
    --collapsible-active-bg: #ffe680; /* Active collapsible button background color */
    --content-panel-bg: #fff;       /* Collapsible panel background color */
    --end-slide-bg: #00274d;        /* Thank-you slide background color */
    --text-color: #000;             /* Default text color */
}

### 3. Customize Styles

Override or extend additional styles to match your theme. Use the existing `core.css` as a reference for the structure.

Example:

body { font-family: 'Arial', sans-serif; background-color: var(--end-slide-bg); color: var(--text-color); }


### 4. Test Your Theme

Set your custom theme in the `theme_css` variable.

Open the presentation in a browser to verify the appearance.

### Optional: Add a Theme Switcher

For advanced usage, you can enable runtime theme switching:

#### Add a Theme Selector to Your HTML:

<select id="theme-selector"> <option value="style-dark.css">Dark Theme</option> <option value="style-blue.css">Blue Theme</option> <option value="style-yourtheme.css">Your Theme</option> </select> ```

### Update the Theme Dynamically

Include the following JavaScript snippet in your script.js file:

document.getElementById('theme-selector').addEventListener('change', function(event) {
    const themeLink = document.getElementById('theme-stylesheet');
    themeLink.href = `static/css/themes/${event.target.value}`;
});
