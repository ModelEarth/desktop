// StudioCraft app list: the open-source Crafting Apps from ArtCraft (github.com/storytold), Apache-2.0.
// Shared by /desktop/ and /desktop/install/. Icons are in desktop/img/craft/.

var craftApps = [
  { slug: "photocraft", name: "PhotoCraft", cat: "Image editor", group: "Image", status: "Early alpha", desc: "Image editing with familiar tools and shortcuts." },
  { slug: "vectorcraft", name: "VectorCraft", cat: "Vector illustration", group: "Design", status: "In development", desc: "Fast vector illustration for logos, icons and print, reimagined in Rust." },
  { slug: "filmcraft", name: "FilmCraft", cat: "Video editor", group: "Video", status: "In development", desc: "Nonlinear video editing rebuilt from scratch for speed and stability." },
  { slug: "lightcraft", name: "LightCraft", cat: "Photo library", group: "Image", status: "In development", desc: "A local photo library and non-destructive raw developer." },
  { slug: "pdfcraft", name: "PdfCraft", cat: "PDF workbench", group: "Documents", status: "Early alpha", desc: "Read, organize, combine, split and secure PDFs." },
  { slug: "effectcraft", name: "EffectCraft", cat: "Motion graphics", group: "Video", status: "In development", desc: "Motion graphics, compositing and visual effects." },
  { slug: "anicraft", name: "AniCraft", cat: "2D animation", group: "Video", status: "Early alpha", desc: "2D vector animation with timelines, tweens and onion skins." },
  { slug: "designcraft", name: "DesignCraft", cat: "Page layout", group: "Design", status: "In development", desc: "Page layout and publishing for magazines, books and brochures." },
  { slug: "figcraft", name: "FigCraft", cat: "Interface design", group: "Design", status: "Early alpha", desc: "UI design and prototyping for apps and websites." },
  { slug: "texturecraft", name: "TextureCraft", cat: "Texture painting", group: "3D", status: "In development", desc: "Paint directly onto 3D models with layered materials." },
  { slug: "materialcraft", name: "MaterialCraft", cat: "Procedural materials", group: "3D", status: "In development", desc: "Node-based procedural materials for games and film." },
  { slug: "soundcraft", name: "SoundCraft", cat: "Audio workstation", group: "Audio", status: "In development", desc: "Record, edit and mix audio in a digital audio workstation." },
  { slug: "wordcraft", name: "WordCraft", cat: "Word processing", group: "Documents", status: "In development", desc: "Fast word processing for reports, letters and long documents." },
  { slug: "deckcraft", name: "DeckCraft", cat: "Presentations", group: "Documents", status: "In development", desc: "Dynamic slide presentations and slide shows." },
  { slug: "cadcraft", name: "CADCraft", cat: "CAD and drafting", group: "3D", status: "In development", desc: "Computer-aided design and drafting for plans and parts." },
  { slug: "gridcraft", name: "GridCraft", cat: "Spreadsheets", group: "Documents", status: "In development", desc: "Spreadsheets and data analysis with formulas and charts." },
  { slug: "craft-anything", name: "Craft Anything", cat: "Software creation", group: "Explore", status: "Early alpha", desc: "Learn how any software works, then craft your own version with AI agents." }
];

var craftLinks = {
  site: "https://getartcraft.com/apps",
  app: function(slug) { return "https://getartcraft.com/apps/" + slug; },
  repo: function(slug) { return "https://github.com/storytold/" + slug; },
  launcher: "https://github.com/storytold/craft-launcher/releases/latest",
  github: "https://github.com/storytold"
};

// ArtCraft Launcher download for this visitor's OS, matching the "Download for Mac" logic on getartcraft.com/download:
// detect the platform from the user agent, then link straight to that platform's recommended installer.
// Release files come from, newest source first:
//   1. The GitHub API's latest release, checked in the browser by refreshCraftLauncherLinks() every
//      craftLauncherCacheMinutes, so links stay current when the script hasn't been run since a new launcher came out.
//   2. The last successful GitHub check saved in this browser, kept for as long as later checks fail.
//   3. js/craft-launcher-release.js, written by install/refresh-launcher.sh, for a browser that has never reached GitHub.
var craftLauncherRepo = "storytold/craft-launcher";
var craftLauncherLatest = null; // set from the GitHub API by refreshCraftLauncherLinks()
var craftLauncherCacheKey = "craftLauncherLatest";
var craftLauncherCacheMinutes = 15; // How often to check GitHub. It allows 60 unauthenticated API calls an hour per IP address.

// Returns { platform, arch } for desktop systems, or null for phones, tablets, ChromeOS and unknown systems
function craftLauncherPlatform() {
  var ua = navigator.userAgent;
  if (/Android|iPhone|iPad|iPod|Mobile|CrOS/i.test(ua)) return null;
  if (/FreeBSD|GhostBSD/i.test(ua)) return { platform: "FreeBSD", arch: "x86_64" };
  if (/Windows/i.test(ua)) return { platform: "Windows", arch: /ARM64|aarch64/i.test(ua) ? "arm64" : "x64" };
  if (/Macintosh|Mac OS X/i.test(ua)) return navigator.maxTouchPoints > 1 ? null : { platform: "Mac" }; // iPads report as Macs
  if (/Linux/i.test(ua)) return { platform: "Linux", arch: /riscv64/i.test(ua) ? "riscv64" : /aarch64|arm64|armv8/i.test(ua) ? "aarch64" : "x86_64" };
  return null;
}

// Returns { href, label, direct, version }. direct is false when linking to the GitHub releases page instead of a file.
function craftLauncherDownload() {
  var p = craftLauncherPlatform();
  if (!p) return { href: craftLinks.launcher, label: "Download Launcher", direct: false };
  var label = "Launcher for " + p.platform;

  // Recommended file first, then alternatives (riscv64 Linux has no Flatpak)
  var suffixes = {
    Mac: ["-macos-universal.dmg"],
    Windows: ["-windows-" + p.arch + ".msi", "-windows-x64.msi"],
    Linux: ["-linux-" + p.arch + ".flatpak", "-linux-" + p.arch + ".AppImage", "-linux-" + p.arch + ".deb"],
    FreeBSD: ["-freebsd-" + p.arch + ".tar.gz"]
  }[p.platform];

  var rel = craftLauncherLatest || (typeof craftLauncherRelease !== "undefined" ? craftLauncherRelease : null);
  if (rel && rel.assets) {
    for (var i = 0; i < suffixes.length; i++) {
      // Match the file name pattern rather than rel.version, in case a tag and its file names differ.
      // The version must start with a digit, which skips artcraft-launcher-cli-* and artcraft-launcher-web-*.
      var pattern = new RegExp("^artcraft-launcher-\\d[\\w.]*" + suffixes[i].replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "$");
      for (var j = 0; j < rel.assets.length; j++) {
        if (pattern.test(rel.assets[j])) {
          return { href: "https://github.com/" + rel.repo + "/releases/download/" + rel.tag + "/" + rel.assets[j], label: label, direct: true, version: rel.version };
        }
      }
    }
  }
  return { href: craftLinks.launcher, label: label, direct: false };
}

// Point every [data-craft-launcher] link at this OS's launcher download, and set its label in [data-craft-launcher-label]
function applyCraftLauncherLinks(root) {
  var dl = craftLauncherDownload();
  (root || document).querySelectorAll("[data-craft-launcher]").forEach(function(a) {
    a.href = dl.href;
    if (dl.direct) a.removeAttribute("target");
    if (dl.version) a.title = "ArtCraft Launcher " + dl.version;
    var label = a.querySelector("[data-craft-launcher-label]");
    if (label) label.textContent = dl.label;
  });
  return dl;
}

// The last release fetched from GitHub in this browser, as { fetched, release }, or null
function craftLauncherCached() {
  try {
    var cached = JSON.parse(localStorage.getItem(craftLauncherCacheKey));
    return cached && cached.release && cached.release.assets ? cached : null;
  } catch (e) {
    return null;
  }
}

// Resolves to the latest launcher release { repo, tag, version, assets } from the GitHub API.
// A copy saved in this browser is reused for craftLauncherCacheMinutes. After that GitHub is checked again,
// and if the check fails, the saved copy is kept, however old, until a check succeeds.
function fetchCraftLauncherLatest() {
  var cached = craftLauncherCached();
  if (cached && Date.now() - cached.fetched < craftLauncherCacheMinutes * 60000) {
    return Promise.resolve(cached.release);
  }
  return fetch("https://api.github.com/repos/" + craftLauncherRepo + "/releases/latest", { headers: { Accept: "application/vnd.github+json" } })
    .then(function(res) {
      if (!res.ok) throw new Error("GitHub API " + res.status);
      return res.json();
    })
    .then(function(json) {
      var release = {
        repo: craftLauncherRepo,
        tag: json.tag_name,
        version: String(json.tag_name).replace(/^v/, ""),
        assets: (json.assets || []).map(function(a) { return a.name; })
      };
      if (!release.tag || !release.assets.length) throw new Error("GitHub API: no release files");
      try { localStorage.setItem(craftLauncherCacheKey, JSON.stringify({ fetched: Date.now(), release: release })); } catch (e) {}
      return release;
    })
    .catch(function(err) {
      if (!cached) throw err;
      console.warn("ArtCraft Launcher: GitHub check failed, keeping the " + cached.release.tag + " release found " + new Date(cached.fetched).toLocaleString() + " | " + err.message);
      return cached.release;
    });
}

// Set the launcher links now from the last GitHub check saved in this browser, or else from js/craft-launcher-release.js,
// then update them from the latest GitHub release. If GitHub can't be reached or is rate limited, the links stay as they are.
function refreshCraftLauncherLinks(root) {
  var cached = craftLauncherCached();
  if (cached) craftLauncherLatest = cached.release;
  applyCraftLauncherLinks(root);
  if (!window.fetch || !window.Promise) return;
  fetchCraftLauncherLatest().then(function(release) {
    craftLauncherLatest = release;
    applyCraftLauncherLinks(root);
  }).catch(function(err) {
    console.warn("ArtCraft Launcher: GitHub check failed, using js/craft-launcher-release.js | " + err.message);
  });
}

function craftIconHTML(app, iconBase, extraClass) {
  return '<img class="craft-icon ' + (extraClass || '') + '" src="' + iconBase + app.slug + '.webp" alt="' + app.name + ' icon" loading="lazy">';
}

function renderCraftDock(el, iconBase, slugs) {
  if (!el) return;
  var apps = slugs ? craftApps.filter(function(a) { return slugs.indexOf(a.slug) >= 0; }) : craftApps;
  el.innerHTML = apps.map(function(app) {
    return '<a href="' + craftLinks.app(app.slug) + '" title="' + app.name + ' - ' + app.cat + '">' + craftIconHTML(app, iconBase, 'craft-icon-sm') + '</a>';
  }).join('');
}

// Three tilted elliptical orbits, like electrons around a nucleus: tilt in degrees,
// seconds per lap and direction. Icons on the near half of an orbit pass in front of the center word.
var craftOrbits = [
  { tilt: 0, seconds: 90, dir: 1 },
  { tilt: 60, seconds: 110, dir: -1 },
  { tilt: -60, seconds: 100, dir: 1 }
];

function renderCraftOrbits(stage, iconBase) {
  if (!stage) return;
  var svgNS = "http://www.w3.org/2000/svg";
  var svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("class", "craft-orbit-lines");
  svg.setAttribute("aria-hidden", "true");
  var paths = craftOrbits.map(function() {
    var path = document.createElementNS(svgNS, "path");
    svg.appendChild(path);
    return path;
  });
  var layer = document.createElement("div");
  layer.className = "craft-orbit-icons";
  stage.appendChild(svg);
  stage.appendChild(layer);

  var perOrbit = craftOrbits.map(function(o, k) {
    return craftApps.filter(function(a, i) { return i % craftOrbits.length === k; }).length;
  });
  var items = craftApps.map(function(app, i) {
    var a = document.createElement("a");
    a.className = "craft-float-item craft-" + app.slug;
    a.href = craftLinks.app(app.slug);
    a.title = app.name;
    a.innerHTML = craftIconHTML(app, iconBase);
    layer.appendChild(a);
    var k = i % craftOrbits.length;
    var j = Math.floor(i / craftOrbits.length);
    return { el: a, orbit: k, angle: (j / perOrbit[k]) * Math.PI * 2 + k * 0.6 };
  });

  var geo = {};
  function measure() {
    var w = stage.clientWidth, h = stage.clientHeight;
    var ratio = 0.34;
    // Size the ellipses so the 60 degree orbits fit the stage height, then stretch them across the width.
    var a = (h / 2 - 44) / Math.sqrt(0.75 + 0.25 * ratio * ratio);
    geo = { cx: w / 2, cy: h / 2, a: a, b: a * ratio, sx: Math.min(1.8, Math.max(0.6, (w / 2 - 50) / a)) };
    paths.forEach(function(path, k) {
      var d = "";
      for (var s = 0; s <= 120; s++) {
        var p = orbitPoint(k, (s / 120) * Math.PI * 2);
        d += (s ? "L" : "M") + p.x.toFixed(1) + " " + p.y.toFixed(1);
      }
      path.setAttribute("d", d + "Z");
    });
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
  }
  function orbitPoint(k, t) {
    var tilt = craftOrbits[k].tilt * Math.PI / 180;
    var x = geo.a * Math.cos(t), y = geo.b * Math.sin(t);
    return {
      x: geo.cx + (x * Math.cos(tilt) - y * Math.sin(tilt)) * geo.sx,
      y: geo.cy + x * Math.sin(tilt) + y * Math.cos(tilt),
      near: Math.sin(t)
    };
  }
  function place() {
    items.forEach(function(item) {
      var p = orbitPoint(item.orbit, item.angle);
      var scale = 0.82 + 0.26 * (p.near + 1) / 2;
      item.el.style.transform = "translate(" + p.x.toFixed(1) + "px, " + p.y.toFixed(1) + "px) translate(-50%, -50%) scale(" + scale.toFixed(3) + ")";
      item.el.style.zIndex = p.near > 0 ? 3 : 1;
      item.el.style.opacity = (0.7 + 0.3 * (p.near + 1) / 2).toFixed(2);
    });
  }

  var paused = false, running = false, last = 0;
  layer.addEventListener("mouseover", function(e) { paused = !!e.target.closest(".craft-float-item"); });
  layer.addEventListener("mouseleave", function() { paused = false; });
  function frame(now) {
    if (!running) return;
    var dt = last ? Math.min(now - last, 100) / 1000 : 0;
    last = now;
    if (!paused) {
      items.forEach(function(item) {
        var o = craftOrbits[item.orbit];
        item.angle += o.dir * dt * Math.PI * 2 / o.seconds;
      });
      place();
    }
    requestAnimationFrame(frame);
  }
  measure();
  place();
  window.addEventListener("resize", function() { measure(); place(); });
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  // Only animate while the stage is on screen.
  new IntersectionObserver(function(entries) {
    var visible = entries[0].isIntersecting;
    if (visible && !running) { running = true; last = 0; requestAnimationFrame(frame); }
    if (!visible) running = false;
  }).observe(stage);
}

function renderCraftGrid(el, iconBase, group) {
  if (!el) return;
  el.innerHTML = craftApps.map(function(app, i) {
    if (group && group !== "All" && app.group !== group) return '';
    var num = String(i + 1).padStart(2, '0');
    return '<a class="craft-card craft-' + app.slug + '" href="' + craftLinks.app(app.slug) + '">'
      + '<div class="craft-card-head">' + craftIconHTML(app, iconBase)
      + '<div><div class="craft-card-cat">' + app.cat + '</div><div class="craft-card-name">' + app.name + '</div></div>'
      + '<span class="craft-card-num">' + num + '</span></div>'
      + '<div class="craft-card-desc">' + app.desc + '</div>'
      + '</a>';
  }).join('');
}

function renderCraftChips(el, gridEl, iconBase) {
  if (!el) return;
  var groups = ["All"];
  craftApps.forEach(function(a) { if (groups.indexOf(a.group) < 0) groups.push(a.group); });
  el.innerHTML = groups.map(function(g) {
    return '<button type="button" class="craft-chip' + (g === "All" ? ' active' : '') + '" data-group="' + g + '">' + g + '</button>';
  }).join('');
  el.addEventListener('click', function(e) {
    var chip = e.target.closest('.craft-chip');
    if (!chip) return;
    el.querySelectorAll('.craft-chip').forEach(function(c) { c.classList.toggle('active', c === chip); });
    renderCraftGrid(gridEl, iconBase, chip.getAttribute('data-group'));
  });
}
