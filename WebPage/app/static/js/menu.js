// Switch between menu visibility
function toggleSubMenu(menuId) {
    const submenu = document.getElementById(menuId);
    const allSubmenus = document.querySelectorAll('.submenu');

    // Close all menus but not the recently opened
    allSubmenus.forEach(sub => {
        if (sub.id !== menuId) {
            sub.style.display = "none";
            localStorage.setItem(sub.id, "closed"); // save sub menu state
        }
    });

    // Switch between submenus states
    if (submenu.style.display === "block") {
        submenu.style.display = "none";
        localStorage.setItem(menuId, "closed"); // Save closed state
    } else {
        submenu.style.display = "block";
        localStorage.setItem(menuId, "open"); // Save opened state
    }
}

// Save sub menu state once the view is refreshed
function restoreSubMenuState() {
    const submenus = document.querySelectorAll('.submenu');
    submenus.forEach(submenu => {
        const menuId = submenu.id;
        const state = localStorage.getItem(menuId);
        if (state === "open") {
            submenu.style.display = "block";
        } else {
            submenu.style.display = "none";
        }
    });
}

// // Save sub menu state once the view is loaded
document.addEventListener("DOMContentLoaded", restoreSubMenuState);

// Makes the menus not to close when switching between sub menus
document.querySelectorAll('.submenu a').forEach(link => {
    link.addEventListener('click', (event) => {
        event.stopPropagation();
    });
});