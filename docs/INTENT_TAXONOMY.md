# Intent Taxonomy (AppleSupport)

Based on exploratory analysis of the AppleSupport Twitter dataset, I defined a small, focused taxonomy of intents that represent the most common customer issues.

## 1. DEVICE_ISSUE
- **Definition**: The customer is experiencing a hardware or core software malfunction with their device (iPhone, Mac, iPad, etc.) such as battery drain, screen issues, or freezing.
- **Positive Examples**:
  - "My iPhone 12 battery is dying in 2 hours after the new update."
  - "The screen on my macbook is flickering."
- **Negative Examples**:
  - "I forgot my Apple ID password." (ACCOUNT_ISSUE)
  - "How do I cancel Apple Music?" (BILLING_ISSUE)
- **Boundary Cases**: Software bugs caused by an update. I map these to DEVICE_ISSUE if they describe the device malfunctioning.

## 2. ACCOUNT_ISSUE
- **Definition**: The customer cannot access their Apple ID, iCloud, or is having trouble with passwords and verification codes.
- **Positive Examples**:
  - "I'm locked out of my Apple ID and cannot reset the password."
  - "I didn't receive the two-factor authentication code."
- **Negative Examples**:
  - "I was charged $9.99 for an app I didn't buy." (BILLING_ISSUE)

## 3. BILLING_ISSUE
- **Definition**: The customer is asking about a charge, refund, subscription cancellation, or payment method issue.
- **Positive Examples**:
  - "I got charged twice for my Apple TV subscription."
  - "How do I get a refund for an accidental app purchase?"
- **Negative Examples**:
  - "I can't log in to see my subscriptions." (ACCOUNT_ISSUE)

## 4. HOW_TO_QUERY
- **Definition**: The customer is asking for instructions on how to use a feature or perform a specific action, not necessarily reporting a broken feature.
- **Positive Examples**:
  - "How do I turn off read receipts in Messages?"
  - "Is there a way to share my screen on FaceTime?"
- **Negative Examples**:
  - "My FaceTime is crashing." (DEVICE_ISSUE)

## 5. OTHER
- **Definition**: The request does not fit into the above categories, or is too vague to classify without further information.
- **Positive Examples**:
  - "Hey @AppleSupport, can you help me?"
  - "This new update is terrible."
