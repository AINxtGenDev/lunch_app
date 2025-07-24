// Basic Socket.IO setup - replace with the full version from the plan
const socket = io();

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('menu_update', (data) => {
    console.log('Menu update received:', data);
    // TODO: Update menu display
});

document.getElementById('refresh-btn').addEventListener('click', () => {
    socket.emit('request_update');
});
