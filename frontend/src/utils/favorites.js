const STORAGE_KEY = 'favorite_products';

export function loadFavorites() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveFavorites(items) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  window.dispatchEvent(new Event('favorites-updated'));
}

export function isFavorite(productId, productType) {
  const items = loadFavorites();
  return items.some(item => item.id === productId && item.type === productType);
}

export function toggleFavorite(item) {
  const items = loadFavorites();
  const exists = items.some(f => f.id === item.id && f.type === item.type);
  const next = exists
    ? items.filter(f => !(f.id === item.id && f.type === item.type))
    : [item, ...items];
  saveFavorites(next);
  return !exists;
}

export function getFavorites() {
  return loadFavorites();
}
