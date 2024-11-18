<template>
  <div id="map-container"></div>
</template>

<script>
import { defineComponent } from "vue";
import * as d3 from "d3";
import { geoPath, geoMercator } from "d3-geo";
import { sankey, sankeyLinkHorizontal } from "d3-sankey";

export default defineComponent({
  name: "SankeyMap",
  mounted() {
    this.drawMap();
  },
  methods: {
    async drawMap() {
      const width = 800;
      const height = 500;

      // Load GeoJSON data
      const geojson = await d3.json("src/datasets/countries.geo.json");

      // Set up SVG container
      const svg = d3
        .select("#map-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

      // Create a group for the map and Sankey diagram
      const g = svg.append("g");

      // Set up map projection and path generator
      const projection = geoMercator()
        .scale(150)
        .translate([width / 2, height / 1.5]);
      const path = geoPath().projection(projection);

      // Draw the map
      g.selectAll("path")
        .data(geojson.features)
        .enter()
        .append("path")
        .attr("d", path)
        .attr("fill", "#dcdcdc") // Light grey for countries
        .attr("stroke", "#888");
    }
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
