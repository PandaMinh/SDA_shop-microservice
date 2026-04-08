import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../api';
import { useAuth } from './AuthContext';

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { user } = useAuth();
  const [cart, setCart] = useState({ items: [], id: null });
  const [count, setCount] = useState(0);

  const fetchCart = useCallback(async () => {
    if (!user || !user.customer_id) {
      setCart({ items: [], id: null });
      setCount(0);
      return;
    }
    try {
      const res = await api.get('/api/cart');
      const cartData = res.data;
      setCart(cartData);
      setCount(cartData.items ? cartData.items.reduce((acc, item) => acc + item.quantity, 0) : 0);
    } catch (e) {
      setCart({ items: [], id: null });
      setCount(0);
    }
  }, [user]);

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const addToCart = async (productId, productType, quantity = 1) => {
    if (!user || !user.customer_id) throw new Error('Vui lòng đăng nhập');
    const res = await api.post('/api/cart/items', {
      product_id: productId,
      product_type: productType,
      quantity,
      customer_id: user.customer_id,
    });
    await fetchCart();
    return res.data;
  };

  const updateItem = async (itemId, quantity) => {
    await api.put(`/api/cart/items/${itemId}`, { quantity });
    await fetchCart();
  };

  const removeItem = async (itemId) => {
    await api.delete(`/api/cart/items/${itemId}/delete`);
    await fetchCart();
  };

  const clearCart = async () => {
    await api.delete('/api/cart/clear');
    await fetchCart();
  };

  const total = cart.items
    ? cart.items.reduce((acc, item) => acc + parseFloat(item.price) * item.quantity, 0)
    : 0;

  return (
    <CartContext.Provider value={{ cart, count, total, addToCart, updateItem, removeItem, clearCart, fetchCart }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
export default CartContext;
