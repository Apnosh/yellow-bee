/* ============================================================
   Yellow Bee — form delivery
   The contact and franchise forms post to Yellow Bee's inbox in the
   Apnosh portal, which also emails the team a copy. base.njk sets
   window.YB_FORMS_ENDPOINT when the site is built with APNOSH_SLUG;
   without it YBForms.ready is false and the pages fall back to
   opening an email.

   Each form gets two hidden fields the portal uses to catch bots:
     _gotcha  must stay empty (people never see it, bots fill it in)
     _ts      when the page opened; instant submits are treated as bots
   ============================================================ */
(function () {
  var ENDPOINT = window.YB_FORMS_ENDPOINT || null;
  var openedAt = Date.now();

  /* Add the hidden bot-check field to a form. Safe to call more than once. */
  function prepare(form) {
    if (!form || form.querySelector('input[name="_gotcha"]')) return;
    var trap = document.createElement('input');
    trap.type = 'text';
    trap.name = '_gotcha';
    trap.tabIndex = -1;
    trap.autocomplete = 'off';
    trap.setAttribute('aria-hidden', 'true');
    trap.style.cssText = 'position:absolute;left:-9999px;width:1px;height:1px;opacity:0;';
    form.appendChild(trap);
  }

  /* Send fields (an object of name -> text). kind: contact | catering | feedback | franchise.
     Resolves to { ok: true } or { ok: false, error: 'message to show' }. */
  function send(form, kind, fields) {
    var data = new URLSearchParams();
    Object.keys(fields).forEach(function (key) {
      var value = fields[key];
      /* skip blanks (optional fields left empty) */
      if (typeof value === 'string' && value.trim()) data.append(key, value.trim());
    });
    var trap = form.querySelector('input[name="_gotcha"]');
    data.set('_gotcha', trap ? trap.value : '');
    data.set('_ts', String(openedAt));
    data.set('_source', window.location.href);

    return fetch(ENDPOINT + '?kind=' + encodeURIComponent(kind), { method: 'POST', body: data })
      .then(function (res) {
        return res.json().catch(function () { return {}; }).then(function (body) {
          if (res.ok) return { ok: true };
          return { ok: false, error: body.error || 'Something went wrong. Please try again.' };
        });
      })
      .catch(function () {
        return { ok: false, error: 'We couldn’t send that. Check your connection and try again.' };
      });
  }

  window.YBForms = { ready: !!ENDPOINT, prepare: prepare, send: send };
  if (ENDPOINT) document.querySelectorAll('form[data-yb-form]').forEach(prepare);
})();
