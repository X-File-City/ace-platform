import { useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../utils/api';
import { PricingCard, type PricingTier } from './PricingCard';
import styles from './Pricing.module.css';

const PRICING_TIERS: PricingTier[] = [
  {
    id: 'starter',
    name: 'Starter',
    price: 9,
    period: 'month',
    description: 'Perfect for individuals getting started',
    features: [
      '100 evolution runs/month',
      '5 playbooks',
      'Premium AI models',
      'Data export',
    ],
    highlighted: ['100 evolution runs/month', '5 playbooks'],
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 29,
    period: 'month',
    description: 'For professionals who need more power',
    features: [
      '500 evolution runs/month',
      '20 playbooks',
      'Premium AI models',
      'Data export',
    ],
    highlighted: ['500 evolution runs/month', '20 playbooks'],
    isPopular: true,
  },
  {
    id: 'ultra',
    name: 'Ultra',
    price: 79,
    period: 'month',
    description: 'Maximum power for demanding workflows',
    features: [
      '2,000 evolution runs/month',
      '100 playbooks',
      'Premium AI models',
      'Data export',
    ],
    highlighted: ['2,000 evolution runs/month', '100 playbooks'],
  },
];

interface SubscribeResponse {
  success: boolean;
  message: string;
  checkout_url: string | null;
  subscription: unknown | null;
}

export function Pricing() {
  const { user } = useAuth();
  const [loadingTier, setLoadingTier] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const currentTier = user?.subscription_tier?.toLowerCase() || 'free';
  const canUseTrial = !user?.has_used_trial;

  const handleSubscribe = async (tierId: string) => {
    setError(null);
    setLoadingTier(tierId);

    try {
      const response = await api.post<SubscribeResponse>('/billing/subscribe', {
        tier: tierId,
      });

      if (response.data.checkout_url) {
        // Redirect to Stripe checkout
        window.location.href = response.data.checkout_url;
      } else if (response.data.success) {
        // Free tier or immediate subscription succeeded
        window.location.reload();
      } else {
        // Checkout creation failed - show error
        setError(response.data.message || 'Failed to create checkout session');
      }
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
            'Failed to process subscription. Please try again.';
      setError(errorMessage);
    } finally {
      setLoadingTier(null);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Choose Your Plan</h1>
        <p>Scale your playbook evolution with the right plan for your needs</p>
      </div>

      {error && (
        <div className={styles.error}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className={styles.grid}>
        {PRICING_TIERS.map((tier) => (
          <PricingCard
            key={tier.id}
            tier={tier}
            isCurrentPlan={currentTier === tier.id}
            isLoading={loadingTier === tier.id}
            onSubscribe={handleSubscribe}
            showTrialCTA={canUseTrial}
          />
        ))}
      </div>

    </div>
  );
}
