<template>
  <div id="map-container"></div>
</template>

<script>
import { defineComponent } from "vue";
import * as d3 from "d3";
import { geoPath, geoMercator, geoCentroid } from "d3-geo";
import { sankey, sankeyLinkHorizontal } from "d3-sankey";

export default defineComponent({
  name: "SankeyMap",
  data() {
    return {
      streamData: {}, // Store loaded data here
    };
  },
  mounted() {
    console.log("HELLO WORLD");
    this.loadStreamingData()
      .then(() => this.drawMap())
      .then(() => this.plotCountries());
  },
  methods: {
    async loadStreamingData() {
      try {
        const data = await d3.json("src/datasets/origin-to-dest-streams.txt");
        this.streamData = data;
        console.log("Streaming data loaded:", this.streamData);
      } catch (error) {
        console.error("Error loading streaming data:", error);
      }
    },
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

      // Set up map projection and path generator
      const projection = geoMercator()
        .scale(150)
        .translate([width / 2, height / 1.5]);
      const path = geoPath().projection(projection);

      // Draw the map
      svg
        .selectAll("path")
        .data(geojson.features)
        .enter()
        .append("path")
        .attr("d", path)
        .attr("fill", "#dcdcdc")
        .attr("stroke", "#888");

      // Save projection and path for later use in plotCountries
      this.projection = projection;
      this.geojson = geojson;
      this.svg = svg;
    },

    plotCountries() {
      if (!this.projection || !this.geojson) return;

      // Select only countries listed as keys in streamData
      const countryNames = Object.keys(this.streamData);

      // Draw a red dot on each country's centroid
      this.svg
        .selectAll("circle")
        .data(
          this.geojson.features.filter((d) =>
            countryNames.includes(d.properties.name)
          )
        )
        .enter()
        .append("circle")
        .attr("cx", (d) => this.projection(geoCentroid(d))[0])
        .attr("cy", (d) => this.projection(geoCentroid(d))[1])
        .attr("r", 3)
        .attr("fill", "red")
        .attr("stroke", "black")
        .attr("stroke-width", 0.5);
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
