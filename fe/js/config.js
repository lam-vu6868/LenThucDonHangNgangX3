// Tự động detect environment
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

const CONFIG = {
    API_URL: isLocalhost 
        ? 'http://localhost:8000'  // Local development
        : 'https://lenthucdonhangngangx3.onrender.com'  // Production (Render)
};
