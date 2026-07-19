# React State Management Overview (Video Script)

[SCENE: INTRO - 0:00 to 0:45]
Welcome back, developers! In this video script, we are exploring modern React state management in 2026. 
State management is the backbone of dynamic web applications.

## 1. Local State with useState Hook

[SCENE: CODE DEMO - 0:45 to 2:15]
Let's start with local component state using the `useState` hook. Here is a simple counter component:

```tsx
import React, { useState } from 'react';

export const Counter: React.FC = () => {
  const [count, setCount] = useState<number>(0);

  return (
    <div className="counter-card">
      <h3>Count: {count}</h3>
      <button onClick={() => setCount(prev => prev + 1)}>
        Increment Count
      </button>
    </div>
  );
};
```

## 2. Global State with Zustand

[SCENE: ARCHITECTURE & CODE - 2:15 to 4:30]
When local state gets complex across multiple components, we use lightweight global stores like Zustand.

```typescript
import { create } from 'zustand';

interface UserStore {
  username: string;
  isLoggedIn: boolean;
  setUser: (name: string) => void;
  logout: () => void;
}

export const useUserStore = create<UserStore>((set) => ({
  username: 'Guest',
  isLoggedIn: false,
  setUser: (name) => set({ username: name, isLoggedIn: true }),
  logout: () => set({ username: 'Guest', isLoggedIn: false }),
}));
```

## 3. Consuming Store in Components

[SCENE: DEMO - 4:30 to 5:00]
Now consume the state slice cleanly without triggering unnecessary rerenders:

```tsx
import React from 'react';
import { useUserStore } from './userStore';

export const UserProfile: React.FC = () => {
  const username = useUserStore((state) => state.username);
  const logout = useUserStore((state) => state.logout);

  return (
    <div className="profile">
      <p>Welcome, {username}!</p>
      <button onClick={logout}>Sign Out</button>
    </div>
  );
};
```

[SCENE: OUTRO - 5:00]
That wraps up our React state management overview! Check out the repository link below.
