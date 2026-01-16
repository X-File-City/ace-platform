import { Check } from 'lucide-react';
import styles from './Pricing.module.css';

export interface PricingTier {
  id: string;
  name: string;
  price: number;
  period: string;
  description: string;
  features: string[];
  highlighted?: string[];
  isPopular?: boolean;
}

interface PricingCardProps {
  tier: PricingTier;
  isCurrentPlan: boolean;
  isLoading: boolean;
  onSubscribe: (tierId: string) => void;
}

export function PricingCard({ tier, isCurrentPlan, isLoading, onSubscribe }: PricingCardProps) {
  const getButtonText = () => {
    if (isLoading) return 'Processing...';
    if (isCurrentPlan) return 'Current Plan';
    return 'Subscribe';
  };

  const getButtonClass = () => {
    if (isCurrentPlan) return `${styles.ctaButton} ${styles.ctaCurrent}`;
    if (tier.isPopular) return `${styles.ctaButton} ${styles.ctaPrimary}`;
    return `${styles.ctaButton} ${styles.ctaSecondary}`;
  };

  return (
    <div className={`${styles.card} ${tier.isPopular ? styles.cardPopular : ''}`}>
      {tier.isPopular && <span className={styles.popularBadge}>Most Popular</span>}

      <div className={styles.cardHeader}>
        <h3 className={styles.tierName}>{tier.name}</h3>
        <div className={styles.price}>
          <span className={styles.priceAmount}>${tier.price}</span>
          <span className={styles.pricePeriod}>/{tier.period}</span>
        </div>
        <p className={styles.cardDescription}>{tier.description}</p>
        {isCurrentPlan && (
          <span className={styles.currentPlanBadge}>
            <Check size={12} />
            Active
          </span>
        )}
      </div>

      <div className={styles.features}>
        {tier.features.map((feature, index) => (
          <div key={index} className={styles.featureItem}>
            <Check size={18} className={styles.featureIcon} />
            <span
              className={`${styles.featureText} ${
                tier.highlighted?.includes(feature) ? styles.featureHighlight : ''
              }`}
            >
              {feature}
            </span>
          </div>
        ))}
      </div>

      <button
        className={getButtonClass()}
        onClick={() => onSubscribe(tier.id)}
        disabled={isCurrentPlan || isLoading}
      >
        {getButtonText()}
      </button>
    </div>
  );
}
