# HeavenScent Roadmap

## Current State
The app is live and usable. It recommends a single fragrance based on the user's city, daily activities, and gender preference. No user accounts or ownership data exists — every recommendation assumes the user is shopping for something new.

---

## In Progress
- Fragrance collection feature (design phase) — allow users to save fragrances they own and receive recommendations from their collection

---

## Near-Term Improvements

### Image Quality
- Investigate more reliable sources for consistent, high-quality transparent fragrance images
- Design the result card UI more prescriptively once image consistency is confirmed

### Prompt Refinement
- Iterate on the Gemini prompt to produce more consistent, structured recommendation outputs
- Evaluate switching to a higher-performance model (e.g. Gemini 2.5 Pro) once prompt is stable — measure quality improvement vs. cost/latency

### Try Again
- Add a "Try Again" button to the result card that re-runs the recommendation with the same inputs, for users who want a different suggestion without starting over

---

## Major Features

### User Accounts + Fragrance Collection
- User login/authentication
- Each user can build a collection of fragrances they own
- Recommendation engine prioritizes owned fragrances; falls back to a new purchase suggestion if nothing in the collection fits
- Collection management UI (add, remove, browse owned fragrances)

---

## Polish

### Mobile-First UI Refinement
- Audit and improve the experience on small screens
- Benchmark against clean, modern web apps for design quality
- Ensure typography, spacing, and interactions feel native on mobile

---

## Long-Term

### iOS App
- Native iOS app (or PWA-to-App Store path)
- Monetization strategy TBD

### Android App
- Native Android app (or cross-platform via React Native / Flutter)
- Monetization strategy TBD
