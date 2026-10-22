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
  // What the owner edits in Your restaurant (owner() above); empty, so the pages keep their own words
  owner: { phone: null, address: null, social: {}, handle: null, week: null, dates: [] },
  meta: { siteType: 'unknown', generatedAt: null, error: null },
}

// The slug and portal address go to every template, even when the fetch fails, so the tag and the
// forms (base.njk, assets/js/forms.js) keep working while the portal's data is unavailable.
const WIRING = { slug: SLUG || null, portalBase: PORTAL_BASE }


/* ── What the owner edits in Apnosh's Your restaurant, shaped for these pages (2026-10-22: "ensure ... the changes go
   where intended"). Each is null/empty when Apnosh has nothing, and the pages then keep their own words (site.json,
   locations.json), so a gap in Apnosh never blanks the site. ── */
const DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
const SHORT = { mon: 'Mon', tue: 'Tue', wed: 'Wed', thu: 'Thu', fri: 'Fri', sat: 'Sat', sun: 'Sun' }

/* "09:00" -> "9am", "20:30" -> "8:30pm", "24:00" -> "12am": the way locations.json writes times */
function clock(t) {
  const [h, m] = String(t === '24:00' ? '00:00' : t).split(':').map(Number)
  if (Number.isNaN(h)) return t
  return `${((h + 11) % 12) + 1}${m ? `:${String(m).padStart(2, '0')}` : ''}${h >= 12 ? 'pm' : 'am'}`
}
const span = (periods) => (periods && periods.length ? periods.map((p) => `${clock(p.open)} – ${clock(p.close)}`).join(', ') : 'Closed')

/* the week as rows of days that share hours: [{ days: 'Mon – Fri', time: '9am – 8pm' }, ...] */
function weekRows(hours) {
  if (!hours || !DAYS.some((d) => hours[d] && hours[d].length)) return null
  const rows = []
  for (const d of DAYS) {
    const time = span(hours[d])
    const last = rows[rows.length - 1]
    if (last && last.time === time) last.to = d
    else rows.push({ from: d, to: d, time })
  }
  return rows.map((r) => ({ days: r.from === r.to ? SHORT[r.from] : `${SHORT[r.from]} – ${SHORT[r.to]}`, time: r.time }))
}

/* "922 E Yesler Way, Seattle, WA 98122" -> { street, city, state, zip } (Apnosh saves the address as one line) */
function addressParts(line) {
  const m = /^(.+?),\s*([^,]+),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)?\s*$/.exec(String(line || '').trim())
  return m ? { street: m[1], city: m[2], state: m[3], zip: m[4] || '' } : null
}

/* holiday and one-off hours from today (Seattle) for the next 90 days */
function comingDates(list) {
  const today = new Date().toLocaleDateString('en-CA', { timeZone: 'America/Los_Angeles' })
  const until = new Date(Date.now() + 90 * 86400000).toLocaleDateString('en-CA', { timeZone: 'America/Los_Angeles' })
  return (list || [])
    .filter((s) => s && s.date >= today && s.date <= until)
    .sort((a, b) => a.date.localeCompare(b.date))
    .map((s) => ({
      date: new Date(`${s.date}T12:00:00`).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }),
      time: s.closed ? 'Closed' : `${clock(s.open || '')} – ${clock(s.close || '')}`,
      /* the raw times too, for a page that writes times its own way (contact: time12) */
      closed: !!s.closed, open: s.open || null, close: s.close || null,
    }))
}

/* "https://instagram.com/shopyellowbee" -> "@shopyellowbee" */
const handleOf = (url) => { const m = /\/(?:@)?([\w.-]+)\/?$/.exec(String(url || '')); return m ? `@${m[1]}` : null }

function owner(data) {
  const social = data.social || {}
  return {
    phone: (data.client && data.client.phone) || null,
    address: addressParts(data.location && data.location.address),
    social,
    handle: handleOf(social.instagram),
    week: weekRows(data.hours),
    dates: comingDates(data.specialHours),
  }
}

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
    data.owner = owner(data)
    const contentCount = Object.keys(data.content).length
    console.log(`[apnosh] fetched ok -- siteType=${data.meta?.siteType}, promo=${!!data.activePromo}, events=${data.upcomingEvents?.length ?? 0}, contentOverrides=${contentCount}`)
    return { ...data, ...WIRING }
  } catch (e) {
    console.warn('[apnosh] fetch failed:', e.message)
    return { ...EMPTY, ...WIRING, meta: { ...EMPTY.meta, error: e.message } }
  }
}
