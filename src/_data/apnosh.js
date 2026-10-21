/**
 * Apnosh portal integration -- fetches canonical site data at build time.
 *
 * What this does:
 *   When this site builds (locally or on Vercel), this file calls the Apnosh
 *   portal's public API to get fresh hours, promotions, events, brand data,
 *   and social links. The returned object is available in every template
 *   as `apnosh.hours`, `apnosh.activePromo`, etc.
 *
 * Round-trip:
 *   1. Apnosh manager publishes an update in portal.apnosh.com
 *   2. Apnosh POSTs to this site's Vercel deploy hook
 *   3. Vercel rebuilds the site -> this file re-fetches -> templates render
 *      with fresh data within ~30 seconds.
 *
 * Env vars (set in Vercel project settings):
 *   APNOSH_SLUG     -- this restaurant's slug on the portal (required). It also turns on the
 *                      Apnosh tag on every page and sends the forms to the portal inbox
 *   APNOSH_API_KEY  -- only required if the portal has a key configured
 *
 * Failure mode:
 *   If the portal is unreachable or returns an error, this file logs the
 *   error and returns null/empty data. Templates check for null before
 *   rendering, so the site stays up even if Apnosh is down.
 */

const PORTAL_BASE = process.env.APNOSH_PORTAL_BASE || 'https://portal.apnosh.com'
const SLUG = process.env.APNOSH_SLUG
const API_KEY = process.env.APNOSH_API_KEY

const EMPTY = {
  client: null,
  brand: null,
  location: null,
  hours: null,
  specialHours: null,
  activePromo: null,
  upcomingEvents: [],
  social: {},
  heroPhotoUrl: null,
  // Content overrides keyed by field key (e.g. 'hero.lede') from
  // apnosh-content.json. Empty until clients edit copy in the portal.
  content: {},
  // Daily specials managed in the portal. Empty array hides the section.
  specials: [],
  meta: { siteType: 'unknown', generatedAt: null, error: null },
}

// The slug and portal address go to every template, even when the fetch fails, so the tag and the
// forms (base.njk, assets/js/forms.js) keep working while the portal's data is unavailable.
const WIRING = { slug: SLUG || null, portalBase: PORTAL_BASE }

module.exports = async function () {
  if (!SLUG) {
    console.warn('[apnosh] APNOSH_SLUG not set, skipping data fetch')
    return { ...EMPTY, ...WIRING, meta: { ...EMPTY.meta, error: 'APNOSH_SLUG env var not set' } }
  }

  const url = `${PORTAL_BASE}/api/public/sites/${SLUG}`
  const headers = API_KEY ? { 'X-Apnosh-Key': API_KEY } : {}

  try {
    const res = await fetch(url, { headers })
    if (!res.ok) {
      const body = await res.text().catch(() => '')
      console.warn(`[apnosh] ${res.status} ${res.statusText}: ${body.slice(0, 200)}`)
      return { ...EMPTY, ...WIRING, meta: { ...EMPTY.meta, error: `${res.status}: ${body.slice(0, 100)}` } }
    }
    const data = await res.json()
    // Ensure content is always an object so templates can use the `or` fallback safely
    data.content = data.content || {}
    data.specials = data.specials || []
    const contentCount = Object.keys(data.content).length
    console.log(`[apnosh] fetched ok -- siteType=${data.meta?.siteType}, promo=${!!data.activePromo}, events=${data.upcomingEvents?.length ?? 0}, contentOverrides=${contentCount}`)
    return { ...data, ...WIRING }
  } catch (e) {
    console.warn('[apnosh] fetch failed:', e.message)
    return { ...EMPTY, ...WIRING, meta: { ...EMPTY.meta, error: e.message } }
  }
}
