# Design System Strategy: The Botanical Archivist

## 1. Overview & Creative North Star
The core philosophy of this design system is **"The Botanical Archivist."** 

Standard CRMs often feel clinical and cold. For a floral management environment, we must balance professional data-integrity with the organic, sensory nature of the product. This system rejects the "bootstrap" look of rigid grids and heavy borders. Instead, we utilize an editorial layout—characterized by dramatic typographic scales, intentional white space, and **Tonal Layering**. We move away from "boxes on a screen" toward a digital canvas that feels like a high-end botanical catalog: structured, premium, and breathable.

---

## 2. Colors & Surface Architecture

The palette centers on deep, sophisticated teals and airy neutrals. We use color not just for branding, but to define the physical architecture of the interface.

### The Color Palette (Material Tokens)
*   **Primary (Brand Core):** `#004f54` (Deep Teal) – Used for high-emphasis actions and navigation.
*   **Primary Container (Vibrant Teal):** `#01696f` – Used for signature elements and hero states.
*   **Surface:** `#f8f9fb` – The base canvas.
*   **Surface Container Low:** `#f3f4f6` – The secondary background level.
*   **Surface Container Lowest:** `#ffffff` – The highest point of elevation (cards/KPIs).

### The "No-Line" Rule
**Explicit Instruction:** Do not use 1px solid borders to separate sections or table rows. Boundaries must be defined through background shifts. 
*   *Example:* A `surface_container_lowest` card sitting on a `surface_container_low` dashboard background provides all the separation needed.

### The "Glass & Gradient" Rule
To add "soul" to the interface, use a subtle linear gradient on primary buttons and sidebar backgrounds: 
*   `linear-gradient(135deg, #01696f 0%, #004f54 100%)`.
*   For floating alerts or overlays, apply **Glassmorphism**: `surface_variant` at 70% opacity with a `24px` backdrop blur.

---

## 3. Typography: Editorial Authority
We utilize a dual-typeface system to achieve a "High-End Editorial" feel. **Manrope** provides the stylistic character for headlines, while **Inter** ensures maximum legibility for dense CRM data.

| Level | Token | Font | Size | Weight | Intent |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Display** | `display-lg` | Manrope | 3.5rem | 700 | Monthly Revenue/Hero Stats |
| **Headline** | `headline-md` | Manrope | 1.75rem | 600 | Page Titles (e.g., "Inventory") |
| **Title** | `title-lg` | Inter | 1.375rem | 600 | Card Titles |
| **Body** | `body-md` | Inter | 0.875rem | 400 | General Data & Labels |
| **Label** | `label-sm` | Inter | 0.6875rem | 600 | Status Badges (All Caps) |

---

## 4. Elevation & Depth
Depth in this system is achieved through **Tonal Layering** rather than structural lines.

*   **The Layering Principle:** Stack surfaces to create focus. 
    1.  `surface` (Level 0: Background)
    2.  `surface_container_low` (Level 1: Content Area)
    3.  `surface_container_lowest` (Level 2: Individual Cards)
*   **Ambient Shadows:** For "floating" elements like modals or active KPI cards, use an extra-diffused shadow: `box-shadow: 0 12px 40px rgba(0, 79, 84, 0.06)`. Note the tint—the shadow uses a hint of the `primary` color, not pure black, to mimic natural light.
*   **The "Ghost Border" Fallback:** If a border is required for accessibility in input fields, use `outline_variant` at **20% opacity**. It should be felt, not seen.

---

## 5. Components

### KPI Cards
*   **Structure:** No borders. Background: `surface_container_lowest`. 
*   **Style:** `xl` (1.5rem) rounded corners. 
*   **Typography:** Use `display-sm` for the metric and `label-md` for the trend indicator.
*   **Visual Soul:** Add a subtle, low-opacity SVG floral motif in the corner of the card using the `primary_fixed_dim` color.

### Data Tables & Status Badges
*   **Forbid dividers:** Use a `8px` vertical gap between rows. Each row should sit on a very subtle `surface_container_high` hover state.
*   **Status Badges:** Use "Pill" shapes (`full` roundedness). 
    *   *Warning:* `tertiary_container` text on `tertiary_fixed` background.
    *   *Success:* Soft Green (Custom) - `#E8F5E9` background with `#2E7D32` text.
*   **Padding:** Use `spacing-4` for horizontal cell padding to give the data "room to breathe."

### Alert Panels
*   **Style:** Use the **Glassmorphism** rule. 
*   **Border:** Use a 2px left-accent bar in `error` or `tertiary` instead of a full border box. This maintains the "No-Line" editorial philosophy.

### Input Fields
*   **Background:** `surface_container_highest`. 
*   **Corners:** `md` (0.75rem).
*   **State:** On focus, transition the background to `surface_container_lowest` and add a 2px `primary` ghost-border (20% opacity).

---

## 6. Do’s and Don’ts

### Do
*   **Do** use asymmetrical spacing. If a headline has `spacing-10` above it, use `spacing-4` below it to create an editorial "grouping" effect.
*   **Do** lean into `surface_container` shifts. If the sidebar is `primary` (Dark Teal), the main content area should be `surface`.
*   **Do** use the `xl` (1.5rem) corner radius for large containers to keep the "soft" brand personality.

### Don’t
*   **Don’t** use black (`#000000`) for text. Use `on_surface` or `on_surface_variant` for a more expensive, softer contrast.
*   **Don’t** use standard "Drop Shadows." If a card doesn't need to float, keep it flat and use tonal shifts.
*   **Don’t** use 1px dividers in lists. Use `spacing-2` of empty space or a background color change.