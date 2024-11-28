<template>
  <div class="container">
    <div class="left"><div id="map-container"></div></div>
    <div class="right">
      <div class="top-right">
        <div class="slider-container">
          <label for="bucketCount">Bucket Count: {{ bucketCount }}</label>
          <input
            type="range"
            id="bucketCount"
            min="1"
            max="100"
            v-model="bucketCount"
          />
        </div>
      </div>
      <div class="bottom-right">
        <div class="slider-container">
          <label for="arrowSize">Arrow Size: {{ arrowSize }}</label>
          <input
            type="range"
            id="arrowSize"
            min="1"
            max="60"
            v-model="arrowSize"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Arrange sliders in a vertical layout */
.slider-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  margin: 30px 0;
  margin-left: 20px;
}

/* Style label to center-align it with the slider */
label {
  font-weight: bold;
  margin-bottom: 5px;
  text-align: center;
}

/* Style slider input */
input[type="range"] {
  -webkit-appearance: none;
  width: 170px;
  height: 8px;
  background: #ddd;
  border-radius: 5px;
  outline: none;
  cursor: pointer;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 15px;
  height: 15px;
  background-color: #007bff;
  border-radius: 50%;
}

input[type="range"]::-moz-range-thumb {
  width: 15px;
  height: 15px;
  background-color: #007bff;
  border-radius: 50%;
}

.container {
  display: flex;
}

.left {
  flex: 1;
  /* Adjust width if needed */
}

.right {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.top-right,
.bottom-right {
  /* Styles for right elements */
}
</style>

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
        Afghanistan: "#FF5733", // Bright Orange
        Angola: "#33FF57", // Bright Green
        Argentina: "#3357FF", // Bright Blue
        Armenia: "#FF33A1", // Bright Pink
        Australia: "#33FFF5", // Bright Cyan
        Austria: "#FF33FF", // Bright Magenta
        Azerbaijan: "#FF8C33", // Bright Orange-Red
        Belgium: "#33FF8C", // Bright Mint
        Brazil: "#33A1FF", // Light Blue
        Canada: "#FF3333", // Bright Red
        Chile: "#33FF33", // Bright Lime
        China: "#FF5733", // Bright Orange
        Colombia: "#33FF57", // Bright Green
        "Costa Rica": "#3357FF", // Bright Blue
        Croatia: "#FF33A1", // Bright Pink
        Cuba: "#33FFF5", // Bright Cyan
        Cyprus: "#FF33FF", // Bright Magenta
        "Côte d'Ivoire": "#FF8C33", // Bright Orange-Red
        Denmark: "#33FF8C", // Bright Mint
        Ecuador: "#33A1FF", // Light Blue
        Estonia: "#FF3333", // Bright Red
        Finland: "#33FF33", // Bright Lime
        France: "#FF5733", // Bright Orange
        Germany: "#33FF57", // Bright Green
        Greece: "#3357FF", // Bright Blue
        Guatemala: "#FF33A1", // Bright Pink
        Hungary: "#33FFF5", // Bright Cyan
        Iceland: "#FF33FF", // Bright Magenta
        India: "#FF8C33", // Bright Orange-Red
        Indonesia: "#33FF8C", // Bright Mint
        Iraq: "#33A1FF", // Light Blue
        Ireland: "#FF3333", // Bright Red
        Israel: "#33FF33", // Bright Lime
        Italy: "#FF5733", // Bright Orange
        Jamaica: "#33FF57", // Bright Green
        Japan: "#3357FF", // Bright Blue
        Kosovo: "#FF33A1", // Bright Pink
        Latvia: "#33FFF5", // Bright Cyan
        Lithuania: "#FF33FF", // Bright Magenta
        Malaysia: "#FF8C33", // Bright Orange-Red
        Mali: "#33FF8C", // Bright Mint
        Mexico: "#33A1FF", // Light Blue
        Moldova: "#FF3333", // Bright Red
        Montenegro: "#33FF33", // Bright Lime
        Netherlands: "#FF5733", // Bright Orange
        "New Zealand": "#33FF57", // Bright Green
        Nicaragua: "#3357FF", // Bright Blue
        Nigeria: "#FF33A1", // Bright Pink
        "North Macedonia": "#33FFF5", // Bright Cyan
        Norway: "#FF33FF", // Bright Magenta
        Panama: "#FF8C33", // Bright Orange-Red
        Paraguay: "#33FF8C", // Bright Mint
        Peru: "#33A1FF", // Light Blue
        Philippines: "#FF3333", // Bright Red
        Poland: "#33FF33", // Bright Lime
        Portugal: "#FF5733", // Bright Orange
        Romania: "#33FF57", // Bright Green
        Russia: "#3357FF", // Bright Blue
        Senegal: "#FF33A1", // Bright Pink
        Slovakia: "#33FFF5", // Bright Cyan
        Slovenia: "#FF33FF", // Bright Magenta
        "South Africa": "#FF8C33", // Bright Orange-Red
        "South Korea": "#33FF8C", // Bright Mint
        Spain: "#33A1FF", // Light Blue
        Suriname: "#FF3333", // Bright Red
        Sweden: "#33FF33", // Bright Lime
        Switzerland: "#FF5733", // Bright Orange
        Taiwan: "#33FF57", // Bright Green
        Thailand: "#3357FF", // Bright Blue
        Turkey: "#FF33A1", // Bright Pink
        Ukraine: "#33FFF5", // Bright Cyan
        "United Kingdom": "#FF33FF", // Bright Magenta
        "United States": "#FF8C33", // Bright Orange-Red
        Uruguay: "#33FF8C", // Bright Mint
        Venezuela: "#33A1FF", // Light Blue
      };
    },
    maxStreams() {
      return 18174185977;
    },
  },
  watch: {
    bucketCount() {
      this.clearArrowLines();
      this.calculateArrowSizes().then(() => this.plotArrows());
    },
    arrowSize() {
      this.clearArrowLines();
      this.calculateArrowSizes().then(() => this.plotArrows());
    },
  },
  data() {
    return {
      streamData: {}, // Store loaded data here
      arrowSize: 10,
      bucketCount: 10,
    };
  },
  mounted() {
    this.loadStreamingData()
      .then(() => this.drawMap())
      .then(() => {
        this.plotCountries();
        this.calculateArrowSizes().then(() => this.plotArrows());
      });
  },
  methods: {
    isValidCountry(country) {
      const countries = [
        "Afghanistan",
        "Angola",
        "Argentina",
        "Armenia",
        "Australia",
        "Austria",
        "Azerbaijan",
        "Belgium",
        "Brazil",
        "Canada",
        "Chile",
        "China",
        "Colombia",
        "Costa Rica",
        "Croatia",
        "Cuba",
        "Cyprus",
        "Côte d'Ivoire",
        "Denmark",
        "Ecuador",
        "Estonia",
        "Finland",
        "France",
        "Germany",
        "Greece",
        "Guatemala",
        "Hungary",
        "Iceland",
        "India",
        "Indonesia",
        "Iraq",
        "Ireland",
        "Israel",
        "Italy",
        "Jamaica",
        "Japan",
        "Kosovo",
        "Latvia",
        "Lithuania",
        "Malaysia",
        "Mali",
        "Mexico",
        "Moldova",
        "Montenegro",
        "Netherlands",
        "New Zealand",
        "Nicaragua",
        "Nigeria",
        "North Macedonia",
        "Norway",
        "Panama",
        "Paraguay",
        "Peru",
        "Philippines",
        "Poland",
        "Portugal",
        "Romania",
        "Russia",
        "Senegal",
        "Slovakia",
        "Slovenia",
        "South Africa",
        "South Korea",
        "Spain",
        "Suriname",
        "Sweden",
        "Switzerland",
        "Taiwan",
        "Thailand",
        "Turkey",
        "Ukraine",
        "United Kingdom",
        "United States",
        "Uruguay",
        "Venezuela",
      ];
      return countries.includes(country);
    },
    async loadStreamingData() {
      try {
        const data = await d3.json("src/datasets/country_to_country.json");
        this.streamData = data;
        console.log("Streaming data loaded:", this.streamData);
      } catch (error) {
        console.error("Error loading streaming data:", error);
      }
      this.validCountries = Object.keys(this.streamData);
    },
    async drawMap() {
      const width = 800;
      const height = 400;

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

      // Add a tooltip to the DOM
      const tooltip = d3
        .select("body") // Attach to the body or a parent element
        .append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("visibility", "hidden") // Initially hidden
        .style("background-color", "rgba(0, 0, 0, 0.7)")
        .style("color", "#fff")
        .style("padding", "5px")
        .style("border-radius", "3px")
        .style("font-size", "12px");

      svg
        .selectAll("path")
        .data(geojson.features)
        .enter()
        .append("path")
        .attr("d", path)
        .attr(
          "fill",
          (d) => this.countryColours[d.properties.name] || "#dcdcdc"
        ) // Color based on countryColours, default to "#dcdcdc"
        .attr("stroke", "#888")
        .each((d) => {
          // Calculate the centroid for each country and store it in the dictionary
          const centroid = path.centroid(d);
          this.countryCentroids[d.properties.name] = centroid; // Store centroid by country name
        })
        .on(
          "mouseover",
          function (event, d) {
            if (this.isValidCountry(d.properties.name)) {
              // Show the tooltip with the country name
              tooltip.style("visibility", "visible").text(d.properties.name); // Country name from GeoJSON properties

              // Optionally, position the tooltip near the mouse pointer
              tooltip
                .style("top", `${event.pageY + 10}px`) // Adjust positioning
                .style("left", `${event.pageX + 10}px`);
            }
          }.bind(this)
        )
        .on("mousemove", function (event) {
          // Update the tooltip position as the mouse moves
          tooltip
            .style("top", `${event.pageY + 10}px`)
            .style("left", `${event.pageX + 10}px`);
        })
        .on("mouseout", function () {
          // Hide the tooltip when mouse leaves the country
          tooltip.style("visibility", "hidden");
        })
        .on(
          "click",
          function (event, d) {
            // Toggle clicked state for the country
            const countryName = d.properties.name;
            if (this.clicked === countryName) {
              // If already clicked, unclick by setting this.clicked to null
              this.clicked = null;
            } else {
              // Otherwise, store the country name in this.clicked
              this.clicked = countryName;
            }

            this.clearArrowLines();
            this.calculateArrowSizes().then(() => this.plotArrows());
          }.bind(this)
        );

      // Save projection and path for later use in plotCountries
      this.projection = projection;
      this.geojson = geojson;
      this.svg = svg;
    },

    plotCountries() {
      if (!this.projection || !this.geojson) return;

      // Select only countries listed as keys in streamData
      const countryNames = Object.keys(this.streamData);
    },
    async calculateArrowSizes() {
      // Access the stream data
      const data = this.streamData;

      const chunk_size = this.maxStreams / this.bucketCount;

      // Object to store the arrow sizes
      this.arrowSizes = {};

      // Iterate over each pair of countries in the data
      for (let origin in data) {
        for (let destination in data[origin]) {
          // Get the number of streams, assume 0 if missing
          const streams = data[origin][destination] || 0;

          // Skip if there are no streams
          if (streams === 0) continue;

          // Calculate the arrow size (adjust the scale as needed)
          //const arrowSize = Math.sqrt(streams) * 2; // Arbitrary scaling factor
          const arrowSize =
            (Math.round(streams / chunk_size) / this.bucketCount) *
            10 *
            this.arrowSize;

          // Store the arrow size in the object
          if (!this.arrowSizes[origin]) {
            this.arrowSizes[origin] = {};
          }
          this.arrowSizes[origin][destination] = arrowSize;
        }
      }
    },
    async plotArrows() {
      const width = 800;
      const height = 400;

      // Access the data and country colors
      const data = this.streamData;
      const countryColors = this.countryColours;

      // Set up the SVG container if it doesn't exist yet
      const svg = this.svg;

      // Iterate over each pair of countries in the data
      for (let origin in data) {
        for (let destination in data[origin]) {
          if (
            this.clicked != null &&
            this.clicked != origin &&
            this.clicked != destination
          ) {
            continue;
          }

          // Get the number of streams, assume 0 if missing
          const streams = data[origin][destination] || 0;

          // Skip if there are no streams
          if (streams === 0) continue;

          // Get the centroid of the origin and destination countries
          const originCountry = this.getCountryCentroid(origin);
          const destinationCountry = this.getCountryCentroid(destination);

          // Skip if centroids are missing
          if (!originCountry || !destinationCountry) continue;

          // Retrieve the arrow size from the precalculated arrow sizes
          const arrowSize =
            (this.arrowSizes[origin] && this.arrowSizes[origin][destination]) ||
            0; // Default to 10 if missing

          if (arrowSize == 0) {
            continue;
          }
          // Draw the arrow
          svg
            .append("line")
            .attr("class", "arrow-line")
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
    clearArrowLines() {
      d3.selectAll(".arrow-line").remove();
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
