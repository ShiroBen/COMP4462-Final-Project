<template>
  <div id="map-container"></div>
</template>

<script>
import { defineComponent } from "vue";
import * as d3 from "d3";
import { geoPath, geoMercator } from "d3-geo";
import { List } from "@element-plus/icons-vue";

export default defineComponent({
  name: "Sankey",
  data() {
    return {
      selectedFeature: "tempo",
      tempoBuckets: null, // Initialize tempoBuckets as null to store the data later
    };
  },
  mounted() {
    this.drawCircle();
  },
  methods: {
    drawCircle() {
      const width = 800;
      const height = 500;

      // Create an SVG container
      const svg = d3
        .select("#map-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

      // Create a group element to hold the circle
      const g = svg.append("g");

      // Circle color and initial radius
      const circleColor = "#FF5733"; // Red-orange
      const initialRadius = 100;

      // Draw a circle
      g.append("circle")
        .attr("cx", width / 2) // Center horizontally
        .attr("cy", height / 2) // Center vertically
        .attr("r", initialRadius)
        .attr("fill", circleColor)
        .attr("stroke", "#444") // Add a stroke to the circle
        .attr("data-name", "example-circle"); // Set a unique data-name attribute
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
