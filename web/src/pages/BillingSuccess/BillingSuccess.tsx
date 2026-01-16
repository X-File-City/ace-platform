import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/Button';
import styles from './BillingSuccess.module.css';

export function BillingSuccess() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { refreshUser } = useAuth();
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    // Refresh user data to get updated subscription
    refreshUser();
  }, [refreshUser]);

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.iconWrapper}>
          <CheckCircle size={64} className={styles.icon} />
        </div>
        <h1>Payment Successful</h1>
        <p>Your subscription has been activated. Thank you for your purchase!</p>
        {sessionId && (
          <p className={styles.sessionId}>Session ID: {sessionId.slice(0, 20)}...</p>
        )}
        <Button onClick={() => navigate('/dashboard')}>Go to Dashboard</Button>
      </div>
    </div>
  );
}
