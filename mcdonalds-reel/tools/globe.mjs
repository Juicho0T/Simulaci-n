// Puntos de tierra (lat/lon) para el globo 3D del reel.
import fs from "node:fs";
import * as d3 from "d3-geo";
import * as topojson from "topojson-client";
const land = JSON.parse(fs.readFileSync(new URL("./node_modules/world-atlas/land-110m.json", import.meta.url)));
const f = topojson.feature(land, land.objects.land);
const pts = [];
for (let lat = -58; lat <= 80; lat += 2.4) {
  const step = 2.4 / Math.max(0.25, Math.cos((lat * Math.PI) / 180));
  for (let lon = -180; lon < 180; lon += step) if (d3.geoContains(f, [lon, lat])) pts.push([Math.round(lat * 10) / 10, Math.round(lon * 10) / 10]);
}
fs.writeFileSync(process.argv[2], "window.GLOBE = " + JSON.stringify(pts) + ";\n");
console.log(pts.length, "puntos");
