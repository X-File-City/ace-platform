import { useNavigate } from 'react-router-dom';
import { XCircle } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import styles from './BillingCancel.module.css';

export function BillingCancel() {
  const navigate = useNavigate();

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.iconWrapper}>
          <XCircle size={64} className={styles.icon} />
        </div>
        <h1>Payment Cancelled</h1>
        <p>Your payment was cancelled. No charges were made to your account.</p>
        <div className={styles.buttons}>
          <Button onClick={() => navigate('/pricing')}>Try Again</Button>
          <Button variant="ghost" onClick={() => navigate('/dashboard')}>
            Go to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}
