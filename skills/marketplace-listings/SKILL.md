---
name: marketplace-listings
description: Automates the posting of Facebook Marketplace listings, including specialized photo upload logic to bypass OS dialogs.
---

# Facebook Marketplace Browser Automation

## Browser Posting

Use the create-item page: <https://www.facebook.com/marketplace/create/item>

1. **Navigation**: Navigate to the URL. If login is required, stop and ask the user.
2. **Field Entry**: Fill in the title, price, category, condition, and description from the approved draft.
3. **Photo Upload**: Use the DataTransfer injection method described below.
4. **Drafting**: Save as a draft first.
5. **Approval**: Present the draft listing URL to the user. Only submit after explicit approval.

## Photo Upload Implementation

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
  zone.dispatchEvent(
    new DragEvent("drop", { bubbles: true, dataTransfer: dt }),
  );
})();
```
