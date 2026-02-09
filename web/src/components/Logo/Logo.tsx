import styles from './Logo.module.css';

interface LogoProps {
  variant?: 'icon' | 'card' | 'full';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

/**
 * ACE Platform Logo - Premium Ace of Spades design
 *
 * Variants:
 * - icon: Just the spade symbol (for favicons, small icons)
 * - card: Mini playing card with spade (for sidebar, headers)
 * - full: Card with "ACE" text (for auth pages, marketing)
 */
export function Logo({ variant = 'card', size = 'md', className = '' }: LogoProps) {
  const sizeClass = styles[size];

  if (variant === 'icon') {
    return (
      <div className={`${styles.logoWrapper} ${sizeClass} ${className}`}>
        <SpadeIcon />
      </div>
    );
  }

  if (variant === 'card') {
    return (
      <div className={`${styles.logoWrapper} ${sizeClass} ${className}`}>
        <AceCard />
      </div>
    );
  }

  // Full variant with text
  return (
    <div className={`${styles.logoWrapper} ${styles.fullLogo} ${sizeClass} ${className}`}>
      <AceCard />
      <span className={styles.logoText}>ACE</span>
    </div>
  );
}

/**
 * Standalone spade icon - elegant, ornate design
 */
function SpadeIcon() {
  return (
    <svg
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={styles.spadeIcon}
    >
      {/* Main spade shape */}
      <path
        d="M16 3C16 3 6 12 6 18C6 21.5 8.5 24 12 24C13.5 24 14.8 23.4 15.7 22.5C15.3 24.5 14 27 12 29H20C18 27 16.7 24.5 16.3 22.5C17.2 23.4 18.5 24 20 24C23.5 24 26 21.5 26 18C26 12 16 3 16 3Z"
        fill="currentColor"
      />
      {/* Decorative inner highlight */}
      <path
        d="M16 7C16 7 10 13 10 17C10 19.2 11.8 21 14 21C15 21 15.8 20.6 16 20C16.2 20.6 17 21 18 21C20.2 21 22 19.2 22 17C22 13 16 7 16 7Z"
        fill="var(--bg-card)"
        opacity="0.15"
      />
    </svg>
  );
}

/**
 * Ace card - mini playing card with ornate spade and corner details
 */
function AceCard() {
  return (
    <svg
      viewBox="0 0 40 56"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={styles.aceCard}
    >
      {/* Card background */}
      <rect
        x="1"
        y="1"
        width="38"
        height="54"
        rx="4"
        fill="var(--bg-card)"
        stroke="var(--border-gold)"
        strokeWidth="1.5"
      />

      {/* Inner border decoration */}
      <rect
        x="4"
        y="4"
        width="32"
        height="48"
        rx="2"
        fill="none"
        stroke="var(--gold-primary)"
        strokeWidth="0.5"
        opacity="0.3"
      />

      {/* Top-left corner "A" */}
      <text
        x="7"
        y="14"
        fill="var(--ink-primary)"
        fontSize="9"
        fontFamily="Palatino Linotype, Palatino, Book Antiqua, Cambria, Georgia, Times New Roman, serif"
        fontWeight="700"
      >
        A
      </text>

      {/* Top-left mini spade */}
      <path
        d="M9 16.5C9 16.5 7 18.5 7 20C7 20.8 7.6 21.5 8.5 21.5C8.9 21.5 9.2 21.3 9 21C9.2 21.3 9.5 21.5 9.9 21.5C10.8 21.5 11.4 20.8 11.4 20C11.4 18.5 9 16.5 9 16.5Z"
        fill="var(--ink-primary)"
        transform="scale(0.8) translate(1, 1)"
      />

      {/* Bottom-right corner "A" (rotated) */}
      <text
        x="33"
        y="50"
        fill="var(--ink-primary)"
        fontSize="9"
        fontFamily="Palatino Linotype, Palatino, Book Antiqua, Cambria, Georgia, Times New Roman, serif"
        fontWeight="700"
        transform="rotate(180, 33, 47)"
      >
        A
      </text>

      {/* Bottom-right mini spade (rotated) */}
      <g transform="rotate(180, 32, 40)">
        <path
          d="M32 34C32 34 30 36 30 37.5C30 38.3 30.6 39 31.5 39C31.9 39 32.2 38.8 32 38.5C32.2 38.8 32.5 39 32.9 39C33.8 39 34.4 38.3 34.4 37.5C34.4 36 32 34 32 34Z"
          fill="var(--ink-primary)"
          transform="scale(0.8) translate(8, 8)"
        />
      </g>

      {/* Center ornate spade */}
      <g transform="translate(20, 28)">
        {/* Outer spade */}
        <path
          d="M0 -12C0 -12 -8 -3 -8 3C-8 6 -6 8.5 -3 8.5C-1.5 8.5 -0.5 7.8 0 7C0.5 7.8 1.5 8.5 3 8.5C6 8.5 8 6 8 3C8 -3 0 -12 0 -12Z"
          fill="var(--ink-primary)"
        />
        {/* Spade stem */}
        <path
          d="M-2.5 7L-3.5 12H3.5L2.5 7"
          fill="var(--ink-primary)"
        />
        {/* Inner highlight */}
        <path
          d="M0 -8C0 -8 -5 -1 -5 3C-5 4.5 -4 5.5 -2.5 5.5C-1.5 5.5 -0.7 5 0 4.2C0.7 5 1.5 5.5 2.5 5.5C4 5.5 5 4.5 5 3C5 -1 0 -8 0 -8Z"
          fill="var(--bg-card)"
          opacity="0.1"
        />
      </g>

      {/* Gold corner accents */}
      <path
        d="M4 8L4 4L8 4"
        stroke="var(--gold-primary)"
        strokeWidth="1"
        fill="none"
        opacity="0.6"
      />
      <path
        d="M36 8L36 4L32 4"
        stroke="var(--gold-primary)"
        strokeWidth="1"
        fill="none"
        opacity="0.6"
      />
      <path
        d="M4 48L4 52L8 52"
        stroke="var(--gold-primary)"
        strokeWidth="1"
        fill="none"
        opacity="0.6"
      />
      <path
        d="M36 48L36 52L32 52"
        stroke="var(--gold-primary)"
        strokeWidth="1"
        fill="none"
        opacity="0.6"
      />
    </svg>
  );
}

/**
 * Export individual components for flexible use
 */
export { SpadeIcon, AceCard };
