import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, LayoutDashboard, Compass, Moon, Sun } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const Sidebar = () => {
  const { theme, toggleTheme } = useTheme();

  const navItems = [
    { name: 'Home', path: '/', icon: <Home size={20} /> },
    { name: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard size={20} /> },
    { name: 'Test', path: '/test', icon: <Compass size={20} /> },
  ];

  return (
    <aside style={{
      width: '240px',
      backgroundColor: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      padding: '1.5rem',
      height: '100vh',
      position: 'sticky',
      top: 0
    }}>
      <div style={{ marginBottom: '3rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{
          width: '32px', height: '32px', borderRadius: '8px', 
          background: 'var(--accent-1)', display: 'flex', 
          alignItems: 'center', justifyContent: 'center', color: 'white'
        }}>
          A
        </div>
        <h2 style={{ fontSize: '1.25rem', margin: 0, fontWeight: 700 }}>ARGUS - AI</h2>
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
        <div className="micro-label" style={{ marginBottom: '0.5rem' }}>Menu</div>
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              borderRadius: '0.75rem',
              textDecoration: 'none',
              color: isActive && item.path !== '#' ? 'var(--text-primary)' : 'var(--text-secondary)',
              backgroundColor: isActive && item.path !== '#' ? 'var(--bg-card)' : 'transparent',
              fontWeight: isActive && item.path !== '#' ? 600 : 500,
              border: isActive && item.path !== '#' ? '1px solid var(--border-color)' : '1px solid transparent',
              transition: 'all 0.2s ease'
            })}
          >
            {item.icon}
            {item.name}
          </NavLink>
        ))}
      </nav>

      <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
        <button 
          onClick={toggleTheme}
          style={{
            display: 'flex', alignItems: 'center', gap: '0.75rem', width: '100%',
            padding: '0.75rem 1rem', borderRadius: '0.75rem',
            backgroundColor: 'var(--bg-card)', color: 'var(--text-primary)',
            border: '1px solid var(--border-color)', cursor: 'pointer'
          }}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
