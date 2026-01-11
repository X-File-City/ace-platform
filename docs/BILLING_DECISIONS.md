# ACE Platform Billing Decisions

*Documented: January 9, 2026*

## Business Context

- **Target customers:** Developers, small teams/startups, AI-savvy individuals
- **Core value proposition:** Self-improving AI context/playbooks - the more you use it, the smarter it gets
- **Distribution channel:** X (Twitter) audience of ~17K followers in AI/dev space
- **Revenue goal:** Replace $225K/year salary (~$18.75K/month)
- **Solo founder:** Plan to use AI tools to help with support

## Pricing Structure

### Subscription Tiers

| Tier | Monthly | Annual | Included Evolution Runs | Margin |
|------|---------|--------|------------------------|--------|
| Starter | $9 | $90/year | 100/month | ~89% |
| Pro | $29 | $290/year | 500/month | ~83% |
| Ultra | $79 | $790/year | 2,000/month | ~75% |

### Annual Discount
- **"2 months free"** framing (~17% discount)
- Annual prices: $90 / $290 / $790

### Overage Pricing
- **$0.05 per additional evolution run** (5x cost, still cheap for users)
- **Behavior:** Block users at limit, show notice offering to buy more credits
- Credit purchasing to be implemented post-launch if needed

## Unit Economics

- Cost per evolution run: ~$0.01 (tested with GPT 5.2 thinking, 11,700 tokens for 5 outcomes)
- Hosting: Fly.io (costs TBD based on scale)

## Launch Strategy

### Founding Member Program
- **First 100 customers** get 50% off for life
- Pro tier becomes $15/month (or $145/year) for founding members
- Display counter showing remaining spots on pricing page
- Creates urgency and rewards early believers

### Launch Plan
- Target launch: Before end of January 2026
- Primary channel: X announcement
- No free tier - lowest entry point is $9/month Starter

## Revenue Projections

To reach $18.75K/month goal:

| Scenario | Customers Needed |
|----------|-----------------|
| 100% at Pro ($29) | 655 customers |
| 70% Pro, 20% Starter, 10% Ultra | ~550 customers |
| With 5% annual churn | ~600-700 active |

With 17K X followers, 4% conversion = 680 potential customers.

## Technical Implementation

### What Already Exists
- Stripe integration core (`ace_platform/core/stripe_config.py`)
- User subscription fields in database
- Billing service with checkout and portal (`ace_platform/core/billing.py`)
- Webhook handler (`ace_platform/core/webhooks.py`)
- Billing API routes (`ace_platform/api/routes/billing.py`)
- Tier limits framework (`ace_platform/core/limits.py`)
- Usage tracking/metering (`ace_platform/core/metering.py`)

### Code Changes Needed
1. Update tier names: FREE/STARTER/PROFESSIONAL/ENTERPRISE → STARTER/PRO/ULTRA
2. Update prices to $9/$29/$79 (monthly) and $90/$290/$790 (annual)
3. Update limits from requests/tokens to evolution runs (100/500/2000)
4. Add founding member coupon support
5. Implement "block at limit + offer credits" flow
6. Fix `_get_user_tier()` function (currently has TODO)
7. Add usage limit enforcement middleware

### Stripe Setup Required

#### Products to Create
1. **ACE Starter** - 100 evolution runs/month
2. **ACE Pro** - 500 evolution runs/month
3. **ACE Ultra** - 2,000 evolution runs/month

#### Prices per Product
- Monthly recurring
- Annual recurring (2 months free)

#### Coupon
- Name: `Founding Member`
- Type: 50% off forever
- Max redemptions: 100

#### Webhook Events
- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_failed`
- `invoice.payment_succeeded`

### Environment Variables Needed
```bash
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_STARTER_PRODUCT_ID=prod_...
STRIPE_PRO_PRODUCT_ID=prod_...
STRIPE_ULTRA_PRODUCT_ID=prod_...
STRIPE_STARTER_MONTHLY_PRICE_ID=price_...
STRIPE_STARTER_YEARLY_PRICE_ID=price_...
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
STRIPE_PRO_YEARLY_PRICE_ID=price_...
STRIPE_ULTRA_MONTHLY_PRICE_ID=price_...
STRIPE_ULTRA_YEARLY_PRICE_ID=price_...
STRIPE_FOUNDING_MEMBER_COUPON_ID=...
```

## Launch Checklist

### Must-Have for Launch
- [ ] Deploy to Fly.io (aceagent.io)
- [ ] Set up Stripe products/prices
- [ ] Create founding member coupon
- [ ] Update code with new tier structure
- [ ] Usage tracking for evolution runs
- [ ] Block at limit with upgrade prompt
- [ ] Founding member counter on pricing page
- [ ] Basic account/billing page

### Post-Launch
- [ ] Credit purchasing for overage
- [ ] Plan upgrades/downgrades mid-cycle
- [ ] Invoices and billing history
- [ ] Enterprise tier (custom pricing)

## Domain
- Primary domain: aceagent.io
