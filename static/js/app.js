// static/js/app.js
const socket = io();

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('menu_update', (data) => {
    updateMenuDisplay(data);
});

function updateMenuDisplay(menus) {
    const menuGrid = document.querySelector('.menu-grid');
    menuGrid.innerHTML = '';
    
    menus.forEach(restaurant => {
        const card = createMenuCard(restaurant);
        menuGrid.appendChild(card);
    });
}

function createMenuCard(restaurant) {
    const card = document.createElement('div');
    card.className = 'menu-card';
    
    // Handle weekly menus differently
    if (restaurant.name === 'Weekly Menu') {
        card.innerHTML = `
            <h2 class="restaurant-name">${restaurant.name}</h2>
            <div class="weekly-menu-tabs">
                ${createWeeklyMenuTabs(restaurant.items)}
            </div>
        `;
    } else {
        card.innerHTML = `
            <h2 class="restaurant-name">${restaurant.name}</h2>
            ${createMenuItems(restaurant.items)}
        `;
    }
    
    return card;
}

function createWeeklyMenuTabs(weeklyItems) {
    // Create tabbed interface for weekly menu
    const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
    let tabsHTML = '<div class="tabs">';
    
    days.forEach((day, index) => {
        tabsHTML += `
            <button class="tab-btn ${index === 0 ? 'active' : ''}" 
                    onclick="showDay('${day}')">${day.charAt(0).toUpperCase() + day.slice(1)}</button>
        `;
    });
    
    tabsHTML += '</div><div class="tab-content">';
    
    days.forEach((day, index) => {
        tabsHTML += `
            <div class="day-menu ${index === 0 ? 'active' : ''}" id="${day}-menu">
                ${createMenuItems(weeklyItems[day] || {})}
            </div>
        `;
    });
    
    return tabsHTML + '</div>';
}