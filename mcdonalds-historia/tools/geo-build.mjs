// Genera rutas SVG precalculadas para los mapas del video (sin red en tiempo de render).
import fs from "node:fs";
import * as d3 from "d3-geo";
import * as topojson from "topojson-client";

const out = process.argv[2];
const read = (p) => JSON.parse(fs.readFileSync(new URL(p, import.meta.url)));
const states = read("./node_modules/us-atlas/states-10m.json");
const nation = read("./node_modules/us-atlas/nation-10m.json");
const land = read("./node_modules/world-atlas/land-110m.json");
const r = (n) => Math.round(n * 10) / 10;
const pt = (proj, lon, lat) => proj([lon, lat]).map(r);
const round = (s) => s.replace(/(\d+\.\d{2,})/g, (m) => String(r(+m)));

// Determinista
let seed = 7;
const rnd = () => ((seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648);

/* ---------- California (escena 2) ---------- */
const stFeat = topojson.feature(states, states.objects.states);
const ca = stFeat.features.find((f) => f.properties.name === "California");
const caProj = d3.geoMercator().fitExtent([[40, 40], [720, 820]], ca);
const caPath = d3.geoPath(caProj);
const neighbors = stFeat.features.filter((f) => ["Nevada", "Arizona", "Oregon"].includes(f.properties.name));
const cal = {
  w: 760, h: 860,
  ca: round(caPath(ca)),
  others: neighbors.map((f) => round(caPath(f))),
  sanBernardino: pt(caProj, -117.2898, 34.1083),
  monrovia: pt(caProj, -117.999, 34.1442),
  losAngeles: pt(caProj, -118.2437, 34.0522),
  sanFrancisco: pt(caProj, -122.4194, 37.7749),
};

/* ---------- Estados Unidos (escena 5a) ---------- */
const usFeat = topojson.feature(nation, nation.objects.nation);
const usProj = d3.geoAlbersUsa().fitExtent([[20, 20], [1260, 760]], usFeat);
const usPath = d3.geoPath(usProj);
const usMesh = topojson.mesh(states, states.objects.states, (a, b) => a !== b);
const lower48 = stFeat.features.filter((f) => !["Alaska", "Hawaii", "Puerto Rico"].includes(f.properties.name) && +f.id < 60);
const usDots = [];
while (usDots.length < 260) {
  const lon = -124 + rnd() * 57, lat = 25 + rnd() * 24;
  if (lower48.some((f) => d3.geoContains(f, [lon, lat]))) {
    const p = usProj([lon, lat]);
    if (p) usDots.push(p.map(r));
  }
}
// Ordena desde el oeste/medio oeste (origen) hacia afuera
const origin = usProj([-87.88, 42.03]);
usDots.sort((a, b) => Math.hypot(a[0] - origin[0], a[1] - origin[1]) - Math.hypot(b[0] - origin[0], b[1] - origin[1]));
const us = {
  w: 1280, h: 780,
  nation: round(usPath(usFeat)),
  mesh: round(usPath(usMesh)),
  desPlaines: usProj([-87.8834, 42.0334]).map(r),
  sanBernardino: usProj([-117.2898, 34.1083]).map(r),
  dots: usDots,
};

/* ---------- Mundo (escena 5b) ---------- */
const landFeat = topojson.feature(land, land.objects.land);
const wProj = d3.geoNaturalEarth1().fitExtent([[10, 10], [1590, 820]], { type: "Sphere" });
const wPath = d3.geoPath(wProj);
const places = [
  ["Canadá", 1967, -123.13, 49.17],
  ["Puerto Rico", 1967, -66.1, 18.4],
  ["Japón", 1971, 139.77, 35.67],
  ["Países Bajos", 1971, 4.83, 52.44],
  ["Alemania", 1971, 11.58, 48.14],
  ["Australia", 1971, 151.0, -33.87],
  ["Reino Unido", 1974, 0.07, 51.49],
  ["México", 1985, -99.13, 19.43],
  ["Rusia", 1990, 37.6, 55.76],
  ["China", 1990, 114.06, 22.54],
  ["India", 1996, 77.2, 28.6],
].map(([name, year, lon, lat]) => ({ name, year, p: pt(wProj, lon, lat) }));
const wDots = [];
while (wDots.length < 420) {
  const lon = -170 + rnd() * 340, lat = -45 + rnd() * 115;
  if (d3.geoContains(landFeat, [lon, lat])) wDots.push(pt(wProj, lon, lat));
}
const world = {
  w: 1600, h: 830,
  land: round(wPath(landFeat)),
  sphere: round(wPath({ type: "Sphere" })),
  usa: pt(wProj, -95, 38),
  places,
  dots: wDots,
};

fs.writeFileSync(out, "window.GEO = " + JSON.stringify({ cal, us, world }) + ";\n");
console.log("ok", (fs.statSync(out).size / 1024).toFixed(0) + " KB");
