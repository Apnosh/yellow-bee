module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ "photos": "photos" });
  eleventyConfig.addPassthroughCopy("src/assets");
  // Favicon at site root (/favicon.ico) so browsers auto-fetch it
  eleventyConfig.addPassthroughCopy({ "src/assets/icons/favicon.ico": "favicon.ico" });
  // Apnosh integration: schema declaring which copy is editable from the portal
  eleventyConfig.addPassthroughCopy({ "src/apnosh-content.json": "apnosh-content.json" });

  // Cache-busting hash that changes every build
  eleventyConfig.addGlobalData("buildHash", String(Date.now()));

  // Format a 24h "HH:MM" string as "8 AM" / "8:30 PM". Renders the
  // Apnosh-managed hours (apnosh.hours) in a friendly way.
  eleventyConfig.addFilter("time12", function (hhmm) {
    if (!hhmm || typeof hhmm !== "string") return hhmm;
    const [hStr, mStr] = hhmm.split(":");
    let h = parseInt(hStr, 10);
    const m = (mStr || "00").padStart(2, "0");
    if (isNaN(h)) return hhmm;
    const period = h >= 12 ? "PM" : "AM";
    h = h % 12;
    if (h === 0) h = 12;
    return m === "00" ? `${h} ${period}` : `${h}:${m} ${period}`;
  });

  // Fixed 2-decimal money so catalog prices never render as "$1.0/lb".
  eleventyConfig.addFilter("money", function (n) {
    const v = Number(n);
    return Number.isFinite(v) ? v.toFixed(2) : n;
  });

  // Full day name from a short key ("mon" -> "Monday").
  eleventyConfig.addFilter("dayLabel", function (key) {
    const map = { mon: "Monday", tue: "Tuesday", wed: "Wednesday", thu: "Thursday", fri: "Friday", sat: "Saturday", sun: "Sunday" };
    return map[key] || key;
  });

  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      data: "_data"
    },
    templateFormats: ["njk", "html", "md"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk"
  };
};
