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

      // Set up a color scale for unique colors per country
      const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

      // Set up a projection and path generator
      const projection = geoMercator()
        .scale(150)
        .translate([width / 2, height / 1.5]);
      const pathGenerator = geoPath().projection(projection);

      // Draw each country with a unique color
      g.selectAll("path")
        .data(geojson.features)
        .enter()
        .append("path")
        .attr("d", pathGenerator)
        .attr("fill", (d) => colorScale(d.properties.name)) // Use color scale based on country name
        .attr("stroke", "#333")
        .each(function (d) {
          // Save the color in each feature for bubble coloring
          d.properties.color = colorScale(d.properties.name);
        });

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
      const centroids = geojson.features
        .filter((feature) => true)
        .map((feature) => ({
          centroid: pathGenerator.centroid(feature),
          color: feature.properties.color, // Use the assigned color for each country
        }));

      const thresholdDistance = 50 / zoomLevel;
      const mergedBubbles = [];

      // Merge bubbles if centroids are close
      for (let i = 0; i < centroids.length; i++) {
        let merged = false;

        for (let j = 0; j < mergedBubbles.length; j++) {
          const distance = this.calculateDistance(
            centroids[i].centroid,
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
          // Create a new bubble entry with color
          mergedBubbles.push({
            centroid: centroids[i].centroid,
            count: 1,
            color: centroids[i].color,
          });
        }
      }

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
