<template>
  <h1>World Map with Bubbles</h1>
  <div id="map-container"></div>
</template>

<script>
import { defineComponent } from "vue";
import * as d3 from "d3";
import { geoPath, geoMercator } from "d3-geo";

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

      // Set up a projection and path generator
      const projection = geoMercator()
        .scale(150)
        .translate([width / 2, height / 1.5]);
      const pathGenerator = geoPath().projection(projection);

      // Draw each country
      g.selectAll("path")
        .data(geojson.features)
        .enter()
        .append("path")
        .attr("d", pathGenerator)
        .attr("fill", "#cccccc")
        .attr("stroke", "#333");

      // Set up zoom behavior
      const zoom = d3
        .zoom()
        .scaleExtent([1, 8]) // Optional: set min and max zoom levels
        .on("zoom", (event) => {
          g.attr("transform", event.transform); // Apply zoom transformation to the group
          this.updateBubbles(geojson, svg, pathGenerator, event.transform.k); // Update bubbles based on zoom level
        });

      svg.call(zoom);

      // Draw initial bubbles
      this.updateBubbles(geojson, svg, pathGenerator, 1); // Initial zoom level
    },

    updateBubbles(geojson, svg, pathGenerator, zoomLevel) {
      // Calculate centroids for each country
      const centroids = geojson.features
        .filter((feature) => {
          const countryName = feature.properties.name; // TODO: REMOVE
          return true;
        })
        .map((feature) => pathGenerator.centroid(feature));

      // Merging logic
      const thresholdDistance = 50 / zoomLevel; // Adjust threshold based on zoom level
      const mergedBubbles = [];

      for (let i = 0; i < centroids.length; i++) {
        let merged = false;

        for (let j = 0; j < mergedBubbles.length; j++) {
          const distance = this.calculateDistance(
            centroids[i],
            mergedBubbles[j].centroid
          );
          if (distance < thresholdDistance) {
            // Merge into existing bubble
            mergedBubbles[j].count += 1;
            merged = true;
            break;
          }
        }

        if (!merged) {
          // Create a new bubble entry
          mergedBubbles.push({
            centroid: centroids[i],
            count: 1,
          });
        }
      }

      // Clear existing bubbles before drawing new ones
      svg.selectAll("circle").remove();
      svg.selectAll("path.bell").remove();

      // Draw bubbles and bell curves
      mergedBubbles.forEach((bubble) => {
        const [x, y] = bubble.centroid;
        const counter = bubble.count;

        // Append the bubble
        svg
          .append("circle")
          .attr("cx", x)
          .attr("cy", y)
          .attr("r", 20) // Fixed radius for the bubble
          .attr("fill", "lightblue");

        // Generate points for the bell curve
        const bellPoints = [];
        const numPoints = 100; // Number of points to generate for the bell curve
        const A = counter; // Scale height by counter
        const mu = 0; // Mean (center of the bell curve)
        const sigma = 10; // Standard deviation (width of the bell curve)

        for (let i = -15; i <= 15; i++) {
          const xPos = x + i; // Position X of the bell curve
          const yPos =
            y -
            A * Math.exp(-((i - mu) ** 2) / (2 * sigma ** 2)) +
            Math.cos(x * x); // Bell curve equation
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
          .attr("stroke", "blue");
      });
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
