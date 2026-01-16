import { type ReactNode } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  BookOpen,
  Key,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  X,
  CreditCard,
} from 'lucide-react';
import { useState } from 'react';
import { Logo } from '../Logo';
import styles from './Layout.module.css';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { to: '/dashboard', icon: BookOpen, label: 'Playbooks' },
    { to: '/api-keys', icon: Key, label: 'API Keys' },
    { to: '/usage', icon: BarChart3, label: 'Usage' },
    { to: '/pricing', icon: CreditCard, label: 'Pricing' },
    { to: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className={styles.layout}>
      {/* Mobile header */}
      <header className={styles.mobileHeader}>
        <button
          className={styles.menuButton}
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        >
          {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        <div className={styles.mobileLogo}>
          <Logo variant="full" size="sm" />
        </div>
      </header>

      {/* Sidebar */}
      <aside className={`${styles.sidebar} ${isSidebarOpen ? styles.open : ''}`}>
        <div className={styles.sidebarContent}>
          {/* Logo */}
          <div className={styles.logo}>
            <Logo variant="full" size="md" />
          </div>

          {/* Navigation */}
          <nav className={styles.nav}>
            {navItems.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `${styles.navLink} ${isActive ? styles.active : ''}`
                }
                onClick={() => setIsSidebarOpen(false)}
              >
                <Icon size={20} />
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>

          {/* User section */}
          <div className={styles.userSection}>
            <div className={styles.userInfo}>
              <div className={styles.avatar}>
                {user?.email?.charAt(0).toUpperCase()}
              </div>
              <div className={styles.userDetails}>
                <span className={styles.userEmail}>{user?.email}</span>
                <span className={styles.userTier}>{user?.subscription_tier || 'Free'}</span>
              </div>
            </div>
            <button className={styles.logoutButton} onClick={handleLogout}>
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {isSidebarOpen && (
        <div
          className={styles.overlay}
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <main className={styles.main}>
        {children}
      </main>
    </div>
  );
}
