/* Hometown of NFL Players -- interactive map.
   Renders one marker per player at their hometown, colored by team.
   1st-round picks show as stars; everyone else as circles. */
(function () {
  "use strict";

  var DATA = window.NFL_DATA || { players: [], teams: {} };
  var PLAYERS = DATA.players.filter(function (p) { return p.lat != null && p.lng != null; });
  var TEAMS = DATA.teams;

  // ---- Map ---------------------------------------------------------------
  var map = L.map("map", { zoomControl: true, minZoom: 3, worldCopyJump: true })
    .setView([38.5, -96], 4);
  L.control.zoom({ position: "topright" });

  // Carto "dark matter" basemap -- the Tableau/Carto style you like.
  L.tileLayer(
    "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    {
      subdomains: "abcd", maxZoom: 19,
      attribution: 'Basemap &copy; <a href="https://carto.com/">CARTO</a> · ' +
        'Data: nflverse, ESPN, OverTheCap'
    }
  ).addTo(map);

  var layer = L.layerGroup().addTo(map);

  // ---- Helpers -----------------------------------------------------------
  function money(v) {
    if (v == null) return "—";
    if (v >= 1e6) return "$" + (v / 1e6).toFixed(1).replace(/\.0$/, "") + "M";
    if (v >= 1e3) return "$" + Math.round(v / 1e3) + "K";
    return "$" + Math.round(v);
  }
  function esc(s) {
    return (s == null ? "" : String(s)).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function ordinal(n) {
    if (n == null) return "—";
    var s = ["th", "st", "nd", "rd"], v = n % 100;
    return n + (s[(v - 20) % 10] || s[v] || s[0]);
  }
  function starSVG(color) {
    return '<svg width="20" height="20" viewBox="0 0 24 24">' +
      '<path d="M12 2l2.9 6.3 6.9.7-5.1 4.6 1.4 6.8L12 17.8 5.9 20.4l1.4-6.8L2.2 9l6.9-.7z" ' +
      'fill="' + color + '" stroke="#fff" stroke-width="1.2"/></svg>';
  }

  // ---- Marker rendering --------------------------------------------------
  function markerFor(p) {
    var m;
    if (p.first_round) {
      m = L.marker([p.lat, p.lng], {
        icon: L.divIcon({
          className: "star-icon", html: starSVG(p.color),
          iconSize: [20, 20], iconAnchor: [10, 10]
        })
      });
    } else {
      var r = p.starter ? 6 : 4.5;
      m = L.circleMarker([p.lat, p.lng], {
        radius: r, fillColor: p.color, color: "#fff",
        weight: p.starter ? 1.6 : 0.8, opacity: 0.9, fillOpacity: 0.85
      });
    }
    m.on("click", function () { openDetail(p); });
    m.bindTooltip(p.name + " · " + (p.position || ""), { direction: "top", opacity: 0.9 });
    return m;
  }

  // ---- Filtering ---------------------------------------------------------
  var F = {
    q: "", teams: [], conf: "", states: [], posgroups: [], round: "",
    startersOnly: false, firstOnly: false, topPaid: 0
  };

  function passes(p) {
    if (F.q && (p.name || "").toLowerCase().indexOf(F.q) === -1) return false;
    if (F.teams.length && F.teams.indexOf(p.team) === -1) return false;
    if (F.conf && p.conf !== F.conf) return false;
    if (F.states.length && F.states.indexOf(p.home_state) === -1) return false;
    if (F.posgroups.length && F.posgroups.indexOf(p.pos_group) === -1) return false;
    if (F.round === "UDFA" && !p.undrafted) return false;
    if (F.round && F.round !== "UDFA" && String(p.draft_round) !== F.round) return false;
    if (F.startersOnly && !p.starter) return false;
    if (F.firstOnly && !p.first_round) return false;
    return true;
  }

  var topPaidSet = null;
  function computeTopPaid(list) {
    if (!F.topPaid) { topPaidSet = null; return list; }
    var ranked = list.filter(function (p) { return p.apy != null; })
      .sort(function (a, b) { return b.apy - a.apy; }).slice(0, F.topPaid);
    topPaidSet = new Set(ranked.map(function (p) { return p.id; }));
    return list.filter(function (p) { return topPaidSet.has(p.id); });
  }

  function render() {
    layer.clearLayers();
    var shown = PLAYERS.filter(passes);
    shown = computeTopPaid(shown);
    var frag = [];
    shown.forEach(function (p) { frag.push(markerFor(p)); });
    frag.forEach(function (m) { layer.addLayer(m); });
    updateStats(shown);
  }

  // ---- Stats -------------------------------------------------------------
  function updateStats(list) {
    var n = list.length;
    var starters = 0, first = 0, apySum = 0, apyN = 0, ageSum = 0, ageN = 0;
    list.forEach(function (p) {
      if (p.starter) starters++;
      if (p.first_round) first++;
      if (p.apy != null) { apySum += p.apy; apyN++; }
      if (p.age != null) { ageSum += p.age; ageN++; }
    });
    setText("st-count", n.toLocaleString());
    setText("st-starters", starters.toLocaleString());
    setText("st-first", first.toLocaleString());
    setText("st-apy", apyN ? money(apySum / apyN) : "—");
    setText("st-age", ageN ? (ageSum / ageN).toFixed(1) : "—");
    setText("st-states", new Set(list.map(function (p) { return p.home_state; })
      .filter(Boolean)).size);
  }
  function setText(id, v) { var e = document.getElementById(id); if (e) e.textContent = v; }

  // ---- Detail panel ------------------------------------------------------
  var detail = document.getElementById("detail");
  function openDetail(p) {
    var contract = p.contract_value
      ? money(p.contract_value) + (p.contract_years ? " / " + p.contract_years + " yrs" : "")
      : "—";
    var draft = p.undrafted ? "Undrafted" :
      (p.draft_year ? p.draft_year + " · Rd " + p.draft_round + ", #" + p.draft_pick +
        (p.draft_team ? " (" + p.draft_team + ")" : "") : "—");

    var badges = [];
    if (p.first_round) badges.push('<span class="badge gold">' + starSVG('#ffb020') + ' 1st-Round Pick</span>');
    if (p.starter) badges.push('<span class="badge green">Projected Starter</span>');
    else if (p.depth_rank) badges.push('<span class="badge">Depth Rank ' + p.depth_rank + '</span>');
    if (p.undrafted) badges.push('<span class="badge">Undrafted Gem</span>');

    var img = p.headshot
      ? '<img src="' + esc(p.headshot) + '" alt="" onerror="this.style.visibility=\'hidden\'">'
      : '<img alt="">';

    detail.innerHTML =
      '<div class="detail-hero">' +
        '<div class="accent" style="background:radial-gradient(circle at 30% 20%,' +
          esc(p.color) + ',transparent 70%)"></div>' +
        '<button class="detail-close" aria-label="Close">×</button>' +
        '<div class="detail-top">' + img +
          '<div><div class="detail-name">' + esc(p.name) + '</div>' +
          '<div class="detail-sub">' + esc(p.position || "") +
            (p.jersey ? " · #" + p.jersey : "") + " · " + esc(p.team_name) + '</div>' +
          '<span class="pill" style="background:' + esc(p.color) + ';color:#fff">' +
            esc(p.div) + '</span></div>' +
        '</div>' +
        '<div class="badge-row">' + badges.join("") + '</div>' +
      '</div>' +
      '<div class="detail-body">' +
        '<div class="kv">' +
          cell("Hometown", p.hometown || "—") +
          cell("College", p.college || "—") +
          cell("Age", p.age != null ? p.age : "—") +
          cell("Experience", p.exp != null ? (p.exp + " yrs") : "—") +
          cell("Height", p.height || "—") +
          cell("Weight", p.weight ? p.weight + " lb" : "—") +
          cell("Draft", draft) +
          cell("Depth Pos", p.depth_pos || p.position || "—") +
          cell("Avg / Year (APY)", money(p.apy)) +
          cell("Guaranteed", money(p.guaranteed)) +
          cell("Contract", contract) +
          cell("Cap %", p.apy_cap_pct != null ? (p.apy_cap_pct * 100).toFixed(1) + "%" : "—") +
        '</div>' +
        (p.espn_url ? '<a class="detail-link" target="_blank" rel="noopener" href="' +
          esc(p.espn_url) + '">View full ESPN profile ↗</a>' : "") +
      '</div>';

    detail.querySelector(".detail-close").onclick = closeDetail;
    detail.classList.add("open");
    map.panTo([p.lat, p.lng], { animate: true });
  }
  function cell(l, v) {
    return '<div class="cell"><div class="l">' + esc(l) + '</div><div class="v">' + esc(v) + '</div></div>';
  }
  function closeDetail() { detail.classList.remove("open"); }

  // ---- Build controls ----------------------------------------------------
  function uniqueSorted(key) {
    return Array.from(new Set(PLAYERS.map(function (p) { return p[key]; })
      .filter(Boolean))).sort();
  }

  function fillSelect(id, values, labeler) {
    var sel = document.getElementById(id);
    values.forEach(function (v) {
      var o = document.createElement("option");
      o.value = v; o.textContent = labeler ? labeler(v) : v;
      sel.appendChild(o);
    });
  }
  function selectedValues(sel) {
    return Array.from(sel.selectedOptions).map(function (o) { return o.value; });
  }

  function initControls() {
    var teamCodes = Object.keys(TEAMS).sort();
    fillSelect("f-team", teamCodes, function (t) { return TEAMS[t].name; });
    fillSelect("f-state", uniqueSorted("home_state"));
    fillSelect("f-posgroup", uniqueSorted("pos_group"));

    document.getElementById("f-search").addEventListener("input", function (e) {
      F.q = e.target.value.trim().toLowerCase(); render();
    });
    document.getElementById("f-team").addEventListener("change", function (e) {
      F.teams = selectedValues(e.target); render();
    });
    document.getElementById("f-state").addEventListener("change", function (e) {
      F.states = selectedValues(e.target); render();
    });
    document.getElementById("f-posgroup").addEventListener("change", function (e) {
      F.posgroups = selectedValues(e.target); render();
    });
    document.getElementById("f-conf").addEventListener("change", function (e) {
      F.conf = e.target.value; render();
    });
    document.getElementById("f-round").addEventListener("change", function (e) {
      F.round = e.target.value; render();
    });
    document.getElementById("f-top").addEventListener("input", function (e) {
      F.topPaid = parseInt(e.target.value, 10);
      document.getElementById("f-top-val").textContent = F.topPaid ? "Top " + F.topPaid : "Off";
      render();
    });
    bindChip("f-starters", function (on) { F.startersOnly = on; render(); });
    bindChip("f-first", function (on) { F.firstOnly = on; render(); });

    document.getElementById("f-reset").addEventListener("click", resetFilters);
    document.getElementById("f-fit").addEventListener("click", function () {
      map.setView([38.5, -96], 4);
    });

    setText("meta-generated", "Updated " + (DATA.generated || "") +
      " · " + PLAYERS.length.toLocaleString() + " mapped players");
  }

  function bindChip(id, cb) {
    var el = document.getElementById(id);
    el.addEventListener("click", function () {
      var input = el.querySelector("input");
      input.checked = !input.checked;
      el.classList.toggle("on", input.checked);
      cb(input.checked);
    });
  }

  function resetFilters() {
    F = { q: "", teams: [], conf: "", states: [], posgroups: [], round: "",
          startersOnly: false, firstOnly: false, topPaid: 0 };
    ["f-team", "f-state", "f-posgroup"].forEach(function (id) {
      var s = document.getElementById(id);
      Array.from(s.options).forEach(function (o) { o.selected = false; });
    });
    document.getElementById("f-search").value = "";
    document.getElementById("f-conf").value = "";
    document.getElementById("f-round").value = "";
    document.getElementById("f-top").value = 0;
    document.getElementById("f-top-val").textContent = "Off";
    ["f-starters", "f-first"].forEach(function (id) {
      var el = document.getElementById(id);
      el.classList.remove("on"); el.querySelector("input").checked = false;
    });
    render();
  }

  // ---- Legend ------------------------------------------------------------
  function initLegend() {
    var legend = L.control({ position: "bottomright" });
    legend.onAdd = function () {
      var div = L.DomUtil.create("div", "map-legend");
      div.innerHTML =
        '<div class="row">' + starSVG('#ffb020') + ' 1st-round pick</div>' +
        '<div class="row"><span class="dot" style="background:#8b5cf6"></span> Starter (bigger)</div>' +
        '<div class="row"><span class="dot" style="width:8px;height:8px;background:#8b5cf6"></span> Rotational / depth</div>' +
        '<div class="row" style="margin-top:4px;color:#a89fce">Color = team · click for profile</div>';
      L.DomEvent.disableClickPropagation(div);
      return div;
    };
    legend.addTo(map);
  }

  // ---- Go ----------------------------------------------------------------
  initControls();
  initLegend();
  render();
  window._nflMap = map;
})();
