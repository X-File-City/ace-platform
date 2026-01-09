import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { setTokens } from '../../utils/api';
import { useAuth } from '../../contexts/AuthContext';
import styles from './OAuthCallback.module.css';

/**
 * Parse URL fragment parameters (after #).
 * Using fragments instead of query params prevents token leakage via
 * browser history, server logs, and referrer headers.
 */
function parseFragmentParams(): URLSearchParams {
  const hash = window.location.hash.slice(1); // Remove leading #
  return new URLSearchParams(hash);
}

export function OAuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [hasProcessed, setHasProcessed] = useState(false);

  useEffect(() => {
    const handleCallback = async () => {
      // Prevent re-processing (can happen with React StrictMode or re-renders)
      if (isProcessing || hasProcessed) {
        return;
      }

      // Check query params for errors (errors can use query params since they're not sensitive)
      const errorParam = searchParams.get('error');
      if (errorParam) {
        setError(errorParam);
        setHasProcessed(true);
        return;
      }

      // Parse tokens from URL fragment (more secure than query params)
      const fragmentParams = parseFragmentParams();
      const accessToken = fragmentParams.get('access_token');
      const refreshToken = fragmentParams.get('refresh_token');

      if (!accessToken || !refreshToken) {
        // Only show error if we haven't processed yet and there's no fragment
        // This prevents false errors during re-renders after fragment is cleared
        if (window.location.hash === '' && !hasProcessed) {
          // Check if we already have valid tokens (callback was already processed)
          const existingToken = localStorage.getItem('access_token');
          if (existingToken) {
            // Tokens exist, just navigate to dashboard
            navigate('/dashboard', { replace: true });
            return;
          }
          setError('Invalid OAuth response');
          setHasProcessed(true);
        }
        return;
      }

      setIsProcessing(true);

      // Clear fragment from URL immediately after reading (extra security measure)
      window.history.replaceState(null, '', window.location.pathname);

      // Store tokens
      setTokens({
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: 'bearer',
      });

      // Refresh user data
      try {
        await refreshUser();
        setHasProcessed(true);
        // Redirect to dashboard
        navigate('/dashboard', { replace: true });
      } catch {
        setError('Failed to load user data');
        setHasProcessed(true);
      } finally {
        setIsProcessing(false);
      }
    };

    handleCallback();
  }, [searchParams, navigate, refreshUser, isProcessing, hasProcessed]);

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.card}>
          <div className={styles.iconError}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="15" y1="9" x2="9" y2="15" />
              <line x1="9" y1="9" x2="15" y2="15" />
            </svg>
          </div>
          <h2>Authentication Failed</h2>
          <p className={styles.errorMessage}>{error}</p>
          <button className={styles.button} onClick={() => navigate('/login')}>
            Back to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.spinner} />
        <p>Completing authentication...</p>
      </div>
    </div>
  );
}
