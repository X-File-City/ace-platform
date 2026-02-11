import { useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../utils/api';
import { PricingCard, type PricingTier } from './PricingCard';
import styles from './Pricing.module.css';

type BillingInterval = 'month' | 'year';

const YEARLY_DISCOUNT = 0.1;

interface PricingTierTemplate extends Omit<PricingTier, 'price' | 'period'> {
  monthlyPrice: number;
}

const PRICING_TIERS: PricingTierTemplate[] = [
  {
    id: 'starter',
    name: 'Starter',
    monthlyPrice: 9,
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
    monthlyPrice: 29,
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
    monthlyPrice: 79,
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

const getDisplayTiers = (interval: BillingInterval): PricingTier[] => {
  return PRICING_TIERS.map((tier) => {
    if (interval === 'month') {
      return {
        ...tier,
        price: tier.monthlyPrice,
        period: 'month',
        buttonPeriodLabel: 'mo',
      };
    }

    const yearlyPrice = Number((tier.monthlyPrice * 12 * (1 - YEARLY_DISCOUNT)).toFixed(2));

    return {
      ...tier,
      price: yearlyPrice,
      period: 'year',
      buttonPeriodLabel: 'yr',
      discountLabel: '10% off',
      monthlyEquivalent: Number((yearlyPrice / 12).toFixed(2)),
    };
  });
};

interface SubscribeResponse {
  success: boolean;
  message: string;
  checkout_url: string | null;
  subscription: unknown | null;
}

export function Pricing() {
  const { user } = useAuth();
  const [billingInterval, setBillingInterval] = useState<BillingInterval>('month');
  const [loadingTier, setLoadingTier] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const currentTier = user?.subscription_tier?.toLowerCase() || 'free';
  const canUseTrial = !user?.has_used_trial;
  const displayedTiers = getDisplayTiers(billingInterval);

  const handleSubscribe = async (tierId: string) => {
    setError(null);
    setLoadingTier(tierId);

    try {
      const response = await api.post<SubscribeResponse>('/billing/subscribe', {
        tier: tierId,
        interval: billingInterval,
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

      <div className={styles.billingToggle} role="group" aria-label="Billing interval">
        <button
          type="button"
          className={`${styles.toggleOption} ${
            billingInterval === 'month' ? styles.toggleOptionActive : ''
          }`}
          onClick={() => setBillingInterval('month')}
        >
          Monthly
        </button>
        <button
          type="button"
          className={`${styles.toggleOption} ${
            billingInterval === 'year' ? styles.toggleOptionActive : ''
          }`}
          onClick={() => setBillingInterval('year')}
        >
          Yearly
          <span className={styles.toggleDiscount}>Save 10%</span>
        </button>
      </div>

      {error && (
        <div className={styles.error}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className={styles.grid}>
        {displayedTiers.map((tier) => (
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
