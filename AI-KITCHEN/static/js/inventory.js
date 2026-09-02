// inventory.js - helper functions to call inventory API
async function fetchInventory(kitchenId) {
  const res = await fetch(`/api/inventory/${kitchenId}`);
  return await res.json();
}
