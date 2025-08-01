// app/static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    // Establish a connection with the server
    const socket = io();

    socket.on('connect', () => {
        console.log('Connected to server via WebSocket.');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server.');
    });

    // Listen for the initial data load
    socket.on('initial_menu_load', (payload) => {
        console.log('Received initial menu data:', payload);
        renderMenus(payload.data);
    });

    // Listen for real-time updates (for when scraping finishes)
    socket.on('menu_update', (payload) => {
        console.log('Received real-time menu update:', payload);
        renderMenus(payload.data);
    });

    function getCategoryDataAttr(category) {
        // Map common category names to data attributes for CSS styling
        const categoryMap = {
            'soup': 'soup',
            'suppe': 'suppe',
            'salat': 'salat',
            'salad': 'salad',
            'main': 'main',
            'main dish': 'main',
            'hauptspeise': 'hauptspeise',
            'dessert': 'dessert',
            'vegetarisch': 'vegetarisch',
            'vegetarian': 'vegetarian',
            'vegan': 'vegetarian',
            'süßspeise': 'dessert',
            'beilage': 'main',
            'side': 'main',
            'pizza': 'pizza',
            'salat / suppe': 'salat',
            'suppe / salat': 'soup'
        };
        
        const mappedCategory = categoryMap[category] || 'main';
        return `data-category="${mappedCategory}"`;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function renderMenus(restaurants) {
        const container = document.getElementById('menu-container');
        container.innerHTML = ''; // Clear previous content (like the "Loading..." message)

        if (!restaurants || restaurants.length === 0) {
            container.innerHTML = `
                <div class="error-placeholder">
                    <h2>No Menus Found</h2>
                    <p>We couldn't find any menus for today. Please check back later or the scrapers might need an update.</p>
                </div>`;
            return;
        }

        restaurants.forEach(restaurant => {
            const card = document.createElement('div');
            card.className = 'restaurant-card';

            let itemsHtml = '<p class="no-menu">No menu available for today.</p>';
            if (restaurant.items && restaurant.items.length > 0) {
                itemsHtml = '<ul>';
                restaurant.items.forEach(item => {
                    const price = item.price ? `<span class="menu-item-price">${escapeHtml(item.price)}</span>` : '';
                    const categoryLower = item.category.toLowerCase();
                    const categoryData = getCategoryDataAttr(categoryLower);
                    itemsHtml += `
                        <li>
                            ${price}
                            <strong class="menu-item-category" ${categoryData}>${escapeHtml(item.category)}</strong>
                            <span class="menu-item-description">${escapeHtml(item.description)}</span>
                        </li>
                    `;
                });
                itemsHtml += '</ul>';
            }

            card.innerHTML = `
                <div class="card-header">
                    <h2>${escapeHtml(restaurant.name)}</h2>
                </div>
                <div class="card-body">
                    ${itemsHtml}
                </div>
            `;
            container.appendChild(card);
        });
    }
});
