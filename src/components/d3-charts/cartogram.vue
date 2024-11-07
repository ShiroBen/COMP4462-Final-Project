<template>
  <h1>World Map with Bubbles</h1>
  <div id="map-container"></div>
</template>

<script>
import { defineComponent } from "vue";
import * as d3 from "d3";
import { geoPath, geoMercator } from "d3-geo";

class UnionFind {
  constructor(elements) {
    this.parent = {};
    elements.forEach((e) => (this.parent[e] = e));
  }

  find(e) {
    if (this.parent[e] === e) return e;
    return (this.parent[e] = this.find(this.parent[e]));
  }

  union(e1, e2) {
    const root1 = this.find(e1);
    const root2 = this.find(e2);
    if (root1 !== root2) this.parent[root1] = root2;
  }

  getGroups() {
    const groups = {};
    for (let e in this.parent) {
      const root = this.find(e);
      if (!groups[root]) groups[root] = [];
      groups[root].push(e);
    }
    return Object.values(groups);
  }
}

export default defineComponent({
  mounted() {
    this.loadMapData();
  },
  methods: {
    drawMap(geojson) {
      const width = 800;
      const height = 500;

      // Create an SVG container
      const svg = d3
        .select("#map-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

      // Create a group element to hold the map and bubbles
      const g = svg.append("g");

      // Set up a color scale for unique colors per country
      const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

      // Set up a projection and path generator
      const projection = d3
        .geoMercator()
        .scale(150)
        .translate([width / 2, height / 1.5]);
      const pathGenerator = d3.geoPath().projection(projection);

      // Draw each country with a unique color and a data-name attribute
      g.selectAll("path")
        .data(geojson.features)
        .enter()
        .append("path")
        .attr("d", pathGenerator)
        .attr("fill", (d) => colorScale(d.properties.name)) // Initial color based on country name
        .attr("stroke", "#333")
        .attr("data-name", (d) => d.properties.name) // Set a unique data-name attribute
        .each(function (d) {
          // Save the initial color in each feature for bubble coloring
          d.properties.color = colorScale(d.properties.name);
        });

      // Set up zoom behavior
      const zoom = d3
        .zoom()
        .scaleExtent([1, 8]) // Optional: set min and max zoom levels
        .on("zoom", (event) => {
          g.attr("transform", event.transform); // Apply zoom transformation to the group

          // Update bubbles based on zoom level
          const mergedCountries = this.updateBubbles(
            geojson,
            svg,
            pathGenerator,
            event.transform.k
          );

          // Recolor the map based on merged countries after bubble update
          this.recolourMap(g, mergedCountries);
        });

      svg.call(zoom);

      // Initial bubble and map color setup without zoom
      const mergedCountries = this.updateBubbles(
        geojson,
        svg,
        pathGenerator,
        1
      );
      this.recolourMap(g, mergedCountries);
    },

    updateBubbles(geojson, svg, pathGenerator, zoomLevel) {
      const centroids = geojson.features.map((feature) => ({
        name: feature.properties.name,
        centroid: pathGenerator.centroid(feature),
        color: feature.properties.color, // Use the assigned color for each country
      }));

      const thresholdDistance = 50 / zoomLevel;
      const mergedBubbles = [];

      // Initialize Union-Find structure for countries
      const countryNames = centroids.map((c) => c.name);
      const uf = new UnionFind(countryNames);

      // Merge bubbles if centroids are close
      for (let i = 0; i < centroids.length; i++) {
        let merged = false;

        for (let j = 0; j < mergedBubbles.length; j++) {
          const distance = this.calculateDistance(
            centroids[i].centroid,
            mergedBubbles[j].centroid
          );
          if (distance < thresholdDistance) {
            // Merge into existing bubble and update Union-Find structure
            uf.union(centroids[i].name, mergedBubbles[j].name);
            mergedBubbles[j].count += 1;
            merged = true;
            break;
          }
        }

        if (!merged) {
          // Create a new bubble entry with color and name
          mergedBubbles.push({
            centroid: centroids[i].centroid,
            count: 1,
            color: centroids[i].color,
            name: centroids[i].name,
          });
        }
      }

      // Get merged country groups and assign a final color to each group
      const mergedCountries = uf.getGroups().map((group) => {
        // Get the color of the first country in each merged group for simplicity
        const finalColor = centroids.find((c) => c.name === group[0]).color;
        return { countries: group, color: finalColor };
      });

      // Clear existing bubbles before drawing new ones
      svg.selectAll("circle").remove();
      svg.selectAll("path.bell").remove();

      // Draw bubbles and bell curves
      mergedBubbles.forEach((bubble) => {
        let [x, y] = bubble.centroid;
        const color = bubble.color;

        // Adjust x, y coordinates by the current zoom transformation
        const transform = d3.zoomTransform(svg.node());
        x = transform.applyX(x);
        y = transform.applyY(y);

        // Check if the bubble is within the visible bounds of the SVG
        if (x < 0 || x > svg.attr("width") || y < 0 || y > svg.attr("height")) {
          return; // Skip drawing this bubble if it's outside the viewport
        }

        // Append the bubble with the adjusted coordinates
        svg
          .append("circle")
          .attr("cx", x)
          .attr("cy", y)
          .attr("r", 20) // Adjust radius based on zoom level
          .attr("fill", color);

        // Generate points for the bell curve
        const bellPoints = [];
        const numPoints = 100;
        const A = bubble.count;
        const mu = 0;
        const sigma = 10;

        for (let i = -15; i <= 15; i++) {
          const xPos = x + i;
          const yPos = y - A * Math.exp(-((i - mu) ** 2) / (2 * sigma ** 2));
          bellPoints.push([xPos, yPos]);
        }

        // Create a path for the bell curve
        const bellPath = d3
          .line()
          .x((d) => d[0])
          .y((d) => d[1]);

        svg
          .append("path")
          .attr("class", "bell")
          .attr("d", bellPath(bellPoints))
          .attr("fill", "none")
          .attr("stroke", color);
      });

      // Log or return the list of merged country groups with final colors
      return mergedCountries;
    },

    loadMapData() {
      // Load GeoJSON data
      d3.json("src/datasets/countries.geo.json")
        .then((geojson) => {
          this.drawMap(geojson);
        })
        .catch((error) => {
          console.error("Error loading GeoJSON data:", error);
        });
    },
    recolourMap(g, mergedCountries) {
      mergedCountries.forEach(({ countries, color }) => {
        countries.forEach((countryName) => {
          g.selectAll("path")
            .filter(function () {
              // Match the country by its data-name attribute
              return d3.select(this).attr("data-name") === countryName;
            })
            .attr("fill", color); // Apply the merged color
        });
      });
    },

    calculateDistance(point1, point2) {
      const dx = point1[0] - point2[0];
      const dy = point1[1] - point2[1];
      return Math.sqrt(dx * dx + dy * dy);
    },
  },
});
</script>

<style scoped>
#map-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
