---
name: marketplace-listings
description: Drafts Facebook Marketplace listings (with price/firm/OBO checks, OneDrive photo subfolders, and custom style guidelines) and automates posting via browser injection.
---

# Facebook Marketplace Listing Drafting & Posting

## Overview

This skill guides the agent in drafting high-quality Facebook Marketplace listings on behalf of a seller and subsequently automating their posting. Your listings are concise, honest, and direct - written to attract genuine buyers and filter out time-wasters.

---

## Part 1: Listing Drafting Guidelines

### Required Inputs

Before drafting any listing, you must have the following. **If price or firm/OBO status is missing from the user's input, prompt for them before proceeding.**

- **Item details**: Description, condition, specs, what's included, reason for selling.
- **Price** (always prompt if not provided): Asking price in CAD.
- **Firm or OBO** (always prompt if not provided): Whether the seller will negotiate.

Do not write a listing until both price and firm/OBO are confirmed.

### Market Research and Pricing

Before creating a draft, perform deep market research to suggest a competitive price for the item. The default stance on pricing is OBO (Or Best Offer) unless otherwise specified by the user. Consider pricing slightly higher than your target to leave room for negotiation.

### Photos and Media

- Store every photo path, URL, or reference the user provides.
- **OneDrive Integration**: By default, prioritize using `%OneDrive%\Shared\Marketplace` for photo management.
- Automatically create product-specific subfolders for direct chat uploads.

### Mandatory Footer

Every listing must end with this exact block (substitute `firm` or `OBO`):

```text
Price is (firm|OBO). Pick up in [Location].

Cash or prepaid e-transfer only. No lowballs, tire kickers, trades, long-distance buyers, out-of-town shipping, gift card hucksters, etc.
```

### Listing Structure

1. Opening line
2. Key specs
3. What's included
4. Condition and provenance
5. Reason for selling
6. Footer

### Marketplace Fields

Suggest values for Title, Category, Condition, Brand, Availability, and Meetup Preferences in a table.

### Style Guidelines

- **Plain text only**: No Markdown in the final description.
- **Concise & Specific**: Use model numbers and specs.
- **Honest**: Disclose flaws upfront.
- **No Price Justification**: State the price and move on.

### Patterns by Item Type

Includes specific rules for Electronics, Clothing, Vehicles (Bank Draft only), and Furniture.

### Edge Cases

Handles "Make an Offer", Multi-item lots, Bundles, and Free items ().

---

## Part 2: Browser Posting Automation

### Browser Posting

Use the create-item page: <https://www.facebook.com/marketplace/create/item>

1. **Navigation**: Navigate to the URL. If login is required, stop and ask the user.
2. **Field Entry**: Fill in the title, price, category, condition, and description from the approved draft.
3. **Photo Upload**: Use the DataTransfer injection method described below.
4. **Drafting**: Save as a draft first. Retrieve the URL for the saved draft listing and remember it.
5. **Approval**: Present the draft listing URL to the user for review. Wait for the user to submit any required edits. If edits are requested, use the remembered draft listing URL to navigate back to the draft and apply the updates before finalizing or requesting approval again. This prevents accidentally creating duplicate listings. Only publish the listing after explicit approval from the user.

### Photo Upload Implementation

To safely upload local photos without triggering OS file picker dialogs:

1. **Host**: Start a temporary node server (e.g., npx http-server) in the directory containing the images.
2. **Inject**: Execute a JavaScript script that fetches image blobs from the local server and fires DragEvents (dragenter, dragover, drop) onto the Marketplace 'Add photos' zone.
3. **Clean Up**: Verify the thumbnails appear, then shut down the local server.

```javascript
// DataTransfer injection logic for browser agents
(async () => {
  const dt = new DataTransfer();
  for (const imgName of images) {
    const res = await fetch("http://127.0.0.1:8124/" + imgName);
    const blob = await res.blob();
    const file = new File([blob], imgName, { type: "image/jpeg" });
    dt.items.add(file);
  }
  const zone = document.querySelector('[aria-label="Add photos"]');
  zone.dispatchEvent(new DragEvent("drop", { bubbles: true, dataTransfer: dt }));
})();
```
