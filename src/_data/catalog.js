/**
 * Grocery catalog -- resolved at build time.
 *
 * WHERE THE DATA COMES FROM
 *   Today: data/catalog-mock.json, a stand-in shaped like a real Star-Plus
 *   item-file export. The page is built against it so the design is finished
 *   before the POS connection exists.
 *
 *   Later: Yellow Bee runs Auto-Star (Star-Plus). Auto-Star self-reports a
 *   "Star-Plus API" on its Capterra/GetApp listing but publishes no developer
 *   docs, so access has to come through the reseller. Star-Plus is also
 *   on-premise software, so the store's copy may not be reachable from Vercel
 *   at all -- in which case the shape is a scheduled PUSH out of the store
 *   (file drop, FTP, or the Octopus Bridge agent) rather than a pull from here.
 *
 *   Either way this file is the only thing that changes. Point CATALOG_URL at
 *   whatever endpoint or JSON drop ends up existing and the templates are
 *   untouched.
 *
 * ENV VARS (set in Vercel project settings)
 *   CATALOG_URL      -- endpoint or static JSON drop serving the item file
 *   CATALOG_API_KEY  -- sent as X-Api-Key when present
 *
 * FAILURE MODE
 *   Any failure -- unset URL, network error, bad status, malformed body, or a
 *   suspiciously short item list -- falls back to the local file and logs why.
 *   A half-empty catalog is worse than a slightly stale one, so the length
 *   check below deliberately prefers local data over a partial fetch. Same
 *   defensive pattern the menu sections use against the Apnosh portal.
 */

const local = require('../../data/catalog-mock.json')

// A live fetch has to beat this share of the local item count to be trusted.
// Guards against the POS returning a truncated or mid-sync item file.
const MIN_TRUST_RATIO = 0.5

const CATALOG_URL = process.env.CATALOG_URL
const CATALOG_API_KEY = process.env.CATALOG_API_KEY

function withSource(data, source, note) {
  return { ...data, source, sourceNote: note }
}

module.exports = async function () {
  if (!CATALOG_URL) {
    console.log(`[catalog] CATALOG_URL not set, using local file (${local.items.length} items)`)
    return withSource(local, 'mock', 'Sample data. Not yet connected to the register.')
  }

  try {
    const headers = CATALOG_API_KEY ? { 'X-Api-Key': CATALOG_API_KEY } : {}
    const res = await fetch(CATALOG_URL, { headers })

    if (!res.ok) {
      console.warn(`[catalog] ${res.status} ${res.statusText}, falling back to local`)
      return withSource(local, 'mock', 'Sample data. Register was unreachable at build time.')
    }

    const data = await res.json()

    if (!data || !Array.isArray(data.items)) {
      console.warn('[catalog] response had no items array, falling back to local')
      return withSource(local, 'mock', 'Sample data. Register returned an unexpected shape.')
    }

    // Prefer local over a partial sync -- see MIN_TRUST_RATIO above.
    if (data.items.length < local.items.length * MIN_TRUST_RATIO) {
      console.warn(
        `[catalog] only ${data.items.length} items (local has ${local.items.length}), ` +
        'looks partial -- falling back to local'
      )
      return withSource(local, 'mock', 'Sample data. Register sync looked incomplete.')
    }

    // Derive category counts if the feed didn't supply them.
    if (!Array.isArray(data.categories) || data.categories.length === 0) {
      const seen = new Map()
      for (const item of data.items) {
        const entry = seen.get(item.category) || { name: item.category, aisle: item.aisle, count: 0 }
        entry.count += 1
        seen.set(item.category, entry)
      }
      data.categories = [...seen.values()]
    }

    console.log(`[catalog] fetched ok -- ${data.items.length} items, ${data.categories.length} categories`)
    return withSource(data, 'pos', null)
  } catch (e) {
    console.warn('[catalog] fetch failed:', e.message)
    return withSource(local, 'mock', 'Sample data. Register was unreachable at build time.')
  }
}
