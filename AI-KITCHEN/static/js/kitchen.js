// kitchen.js - kitchen setup helpers
document.addEventListener('DOMContentLoaded', () => console.log('Kitchen JS loaded'));
// kitchen.js - kitchen setup & state helpers

async function ensureKitchenId() {
    let id = localStorage.getItem("kitchen_id");
    if (id) return id;

    try {
        const res = await fetch('/api/kitchen/');
        const data = await res.json();
        if (data.success && data.kitchens && data.kitchens.length > 0) {
            id = String(data.kitchens[0].id);
            localStorage.setItem('kitchen_id', id);
            return id;
        }
    } catch (e) {
        console.error('Failed to resolve active kitchen:', e);
    }
    return null;
}

window.ensureKitchenId = ensureKitchenId;

document.addEventListener('DOMContentLoaded', () => {
    console.log('Kitchen JS loaded');
});
