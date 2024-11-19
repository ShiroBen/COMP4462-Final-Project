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
  computed: {
    countryColours() {
      return {
        Lithuania: "#FF5733", // Red-orange
        Latvia: "#33FF57", // Green
        Germany: "#3357FF", // Blue
        France: "#F1C40F", // Yellow
        Ireland: "#FF6347", // Tomato
        Japan: "#8A2BE2", // Blue violet
        Philippines: "#FFD700", // Gold
        India: "#FF1493", // Deep pink
        Guatemala: "#00FA9A", // Medium spring green
        Canada: "#00BFFF", // Deep sky blue
        "Costa Rica": "#FF4500", // Orange red
        "United Kingdom": "#DA70D6", // Orchid
        "United States of America": "#ADFF2F", // Green yellow
        Malaysia: "#20B2AA", // Light sea green
        Bolivia: "#D2691E", // Chocolate
        Italy: "#FF4500", // Orange red
        Mexico: "#32CD32", // Lime green
        Colombia: "#C71585", // Medium violet red
        Netherlands: "#DC143C", // Crimson
        Brazil: "#228B22", // Forest green
        Norway: "#8B0000", // Dark red
        Ecuador: "#FFFF00", // Yellow
        Iceland: "#00CED1", // Dark turquoise
        Greece: "#4682B4", // Steel blue
        Estonia: "#FF8C00", // Dark orange
        Sweden: "#C71585", // Medium violet red
        Australia: "#32CD32", // Lime green
        Taiwan: "#FFD700", // Gold
        Denmark: "#B22222", // Firebrick
        "Dominican Republic": "#F0E68C", // Khaki
        Turkey: "#FF6347", // Tomato
        Hungary: "#FF69B4", // Hot pink
        "El Salvador": "#6A5ACD", // Slate blue
        Honduras: "#FF8C00", // Dark orange
        Belgium: "#800080", // Purple
        "South Korea": "#3CB371", // Medium sea green
        Austria: "#B0C4DE", // Light steel blue
        Uruguay: "#FFD700", // Gold
        Panama: "#C0C0C0", // Silver
        Spain: "#FF6347", // Tomato
        Finland: "#00008B", // Dark blue
        Paraguay: "#8B4513", // Saddle brown
        Peru: "#D2691E", // Chocolate
        Luxembourg: "#A52A2A", // Brown
        Chile: "#D3D3D3", // Light grey
        "New Zealand": "#FF1493", // Deep pink
        Portugal: "#8A2BE2", // Blue violet
        "Czech Republic": "#4682B4", // Steel blue
        China: "#DC143C", // Crimson
        Poland: "#FF4500", // Orange red
        Argentina: "#2E8B57", // Sea green
      };
    },
  },
  data() {
    return {
      streamData: {}, // Store loaded data here
    };
  },
  mounted() {
    console.log("HELLO WORLD");
    console.log(this.countryColours);
    this.loadStreamingData()
      .then(() => this.drawMap())
      .then(() => {
        this.plotCountries();
        this.plotArrows();
      });
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

      // Dictionary to store country centroids
      this.countryCentroids = {};

      // Draw the map and calculate centroids for each country
      svg
        .selectAll("path")
        .data(geojson.features)
        .enter()
        .append("path")
        .attr("d", path)
        .attr("fill", "#dcdcdc")
        .attr("stroke", "#888")
        .each((d) => {
          // Calculate the centroid for each country and store it in the dictionary
          const centroid = path.centroid(d);
          this.countryCentroids[d.properties.name] = centroid; // Store centroid by country name
        });

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
    async plotArrows() {
      const width = 800;
      const height = 500;

      // Access the data and country colors
      const data = this.streamData;
      const countryColors = this.countryColours;

      // Set up the SVG container if it doesn't exist yet
      const svg = this.svg;
      console.log("svg is ", svg);

      console.log("data is ", data);

      // Iterate over each pair of countries in the data
      for (let origin in data) {
        for (let destination in data[origin]) {
          // Get the number of streams, assume 0 if missing
          const streams = data[origin][destination] || 0;

          // Skip if there are no streams
          if (streams === 0) continue;

          // Get the centroid of the origin and destination countries (simplified approach)
          const originCountry = this.getCountryCentroid(origin);
          const destinationCountry = this.getCountryCentroid(destination);

          // Skip if centroids are missing
          if (!originCountry || !destinationCountry) continue;

          // Define the arrow size based on the number of streams
          //const arrowSize = Math.sqrt(streams) * 2; // Arbitrary scaling factor
          const arrowSize = 10;

          // Draw the arrow
          svg
            .append("line")
            .attr("x1", originCountry[0])
            .attr("y1", originCountry[1])
            .attr("x2", destinationCountry[0])
            .attr("y2", destinationCountry[1])
            .attr("stroke", countryColors[origin] || "#000") // Use the color of the origin country or default to black
            .attr("stroke-width", arrowSize)
            .attr("stroke-linecap", "round")
            .attr("opacity", 0.6);
        }
      }
    },

    // Helper method to get the centroid of a country (simplified approach)
    getCountryCentroid(countryName) {
      return this.countryCentroids[countryName];
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
