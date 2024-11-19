<template>
  <div id="map-container"></div>
  <div class="filter-container">
    <label for="filter-selector" class="filter-label">Choose Variable:</label>
    <select
      id="filter-selector"
      v-model="selectedFeature"
      @change="changeVariable"
      class="custom-select"
    >
      <option disabled value="">Select an option...</option>
      <option value="danceability">Danceability</option>
      <option value="energy">Energy</option>
      <option value="loudness">Loudness</option>
      <option value="speechiness">Speechiness</option>
      <option value="acousticness">Acousticness</option>
      <option value="instrumentalness">Instrumentalness</option>
      <option value="liveness">Liveness</option>
      <option value="valence">Valence</option>
      <option value="tempo">Tempo</option>
    </select>
  </div>
</template>

<script>
import { defineComponent } from "vue";
import * as d3 from "d3";
import { geoPath, geoMercator } from "d3-geo";
import { List } from "@element-plus/icons-vue";

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
  name: "Cartogram",
  data() {
    return {
      selectedFeature: "tempo",
      tempoBuckets: null, // Initialize tempoBuckets as null to store the data later
    };
  },
  mounted() {
    this.tooltip = d3
        .select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("visibility", "hidden") // Initially hidden
        .style("background-color", "rgba(0, 0, 0, 0.7)")
        .style("color", "#fff")
        .style("padding", "5px")
        .style("border-radius", "3px")
        .style("font-size", "12px");

    this.createTempoHistogram(
      "src/datasets/cartogram.countries.updated.data.json"
    ); // Call with the JSON path
  },
  methods: {
    changeVariable() {
      this.closeMap();
      console.log("selected feature is ", this.selectedFeature);
      this.createTempoHistogram(
        "src/datasets/cartogram.countries.updated.data.json"
      );
    },
    closeMap() {
      // Remove the entire map container
      d3.select("#map-container").selectAll("*").remove();
    },

    createTempoHistogram(jsonPath) {
      // Load JSON data and calculate tempo buckets
      d3.json(jsonPath).then((data) => {
        // Extract all tempo values across all countries to determine the global min and max
        const allTempos = [];
        for (const country in data[this.selectedFeature]) {
          allTempos.push(...data[this.selectedFeature][country]);
        }
        const globalMin = d3.min(allTempos);
        const globalMax = d3.max(allTempos);

        // Calculate bucket size
        const bucketSize = (globalMax - globalMin) / 10;

        // Prepare the histogram data for each country
        const countryBuckets = {};

        for (const country in data[this.selectedFeature]) {
          const countryTempos = data[this.selectedFeature][country];
          const buckets = new Array(10).fill(0);

          // For each tempo, determine its bucket
          countryTempos.forEach((tempo) => {
            const bucketIndex = Math.min(
              Math.floor((tempo - globalMin) / bucketSize),
              9 // To handle edge case where tempo == globalMax
            );
            buckets[bucketIndex]++;
          });

          // Save the bucket counts for this country
          countryBuckets[country] = buckets;
        }

        // Store the computed buckets in `this.tempoBuckets`
        this.tempoBuckets = countryBuckets;

        // Call loadMapData once tempoBuckets are ready
        this.loadMapData();
      });
    },
    drawMap(geojson) {
      const width = 800;
      const height = 400;

      // Create an SVG container
      const svg = d3
        .select("#map-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

      // Create a group element to hold the map and bubbles
      const g = svg.append("g");

      // Set up a color scale for unique colors per country
      const defaultColor = "#dcdcdc"; // Grey color for countries not in the dictionary

      const countryColors = {
        Argentina: "#FF5733", // Bright Orange
        Australia: "#33FF57", // Bright Green
        Austria: "#3357FF", // Bright Blue
        Belgium: "#FF33A1", // Bright Pink
        Brazil: "#33FFF5", // Bright Cyan
        Canada: "#FF33FF", // Bright Magenta
        Chile: "#FF8C33", // Bright Orange-Red
        China: "#33FF8C", // Bright Mint
        Colombia: "#33A1FF", // Light Blue
        "Costa Rica": "#FF3333", // Bright Red
        Denmark: "#33FF33", // Bright Lime
        Ecuador: "#FF5733", // Bright Orange
        Estonia: "#33FF57", // Bright Green
        Finland: "#3357FF", // Bright Blue
        France: "#FF33A1", // Bright Pink
        Germany: "#33FFF5", // Bright Cyan
        Greece: "#FF33FF", // Bright Magenta
        Guatemala: "#FF8C33", // Bright Orange-Red
        Hungary: "#33FF8C", // Bright Mint
        Iceland: "#33A1FF", // Light Blue
        India: "#FF3333", // Bright Red
        Ireland: "#33FF33", // Bright Lime
        Italy: "#FF5733", // Bright Orange
        Japan: "#33FF57", // Bright Green
        Latvia: "#3357FF", // Bright Blue
        Lithuania: "#FF33A1", // Bright Pink
        Malaysia: "#33FFF5", // Bright Cyan
        Mexico: "#FF33FF", // Bright Magenta
        Netherlands: "#FF8C33", // Bright Orange-Red
        "New Zealand": "#33FF8C", // Bright Mint
        Norway: "#33A1FF", // Light Blue
        Panama: "#FF3333", // Bright Red
        Paraguay: "#33FF33", // Bright Lime
        Peru: "#FF5733", // Bright Orange
        Philippines: "#33FF57", // Bright Green
        Poland: "#3357FF", // Bright Blue
        Portugal: "#FF33A1", // Bright Pink
        "South Korea": "#33FFF5", // Bright Cyan
        Spain: "#FF33FF", // Bright Magenta
        Sweden: "#FF8C33", // Bright Orange-Red
        Taiwan: "#33FF8C", // Bright Mint
        Turkey: "#33A1FF", // Light Blue
        "United Kingdom": "#FF3333", // Bright Red
        "United States": "#33FF33", // Bright Lime
        Uruguay: "#FF5733", // Bright Orange
      };

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
        .attr("fill", (d) => countryColors[d.properties.name] || defaultColor) // Use dictionary color or default grey
        .attr("stroke", "#333")
        .attr("data-name", (d) => d.properties.name) // Set a unique data-name attribute
        .each(function (d) {
          // Save the initial color in each feature for bubble coloring
          d.properties.color = countryColors[d.properties.name] || defaultColor;
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
      const tooltip = this.tooltip;
      tooltip.style("visibility", "hidden");

      // Add a tooltip to the DOM
      svg.selectAll(".tooltip-circle").remove();
      

      const countriesThatAreInDataset = [
        "Argentina",
        "Australia",
        "Austria",
        "Belgium",
        "Brazil",
        "Canada",
        "Chile",
        "China",
        "Colombia",
        "Costa Rica",
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
        "Ireland",
        "Italy",
        "Japan",
        "Latvia",
        "Lithuania",
        "Malaysia",
        "Mexico",
        "Netherlands",
        "New Zealand",
        "Norway",
        "Panama",
        "Paraguay",
        "Peru",
        "Philippines",
        "Poland",
        "Portugal",
        "South Korea",
        "Spain",
        "Sweden",
        "Taiwan",
        "Turkey",
        "United Kingdom",
        "United States",
        "Uruguay",
      ];

      const centroids = geojson.features
        .filter((feature) =>
          countriesThatAreInDataset.includes(feature.properties.name)
        )
        .map((feature) => ({
          name: feature.properties.name,
          centroid: pathGenerator.centroid(feature),
          color: feature.properties.color, // Use the assigned color for each country
          tempoBuckets:
            this.tempoBuckets[feature.properties.name] || new Array(10).fill(0),
          listOfCountriesInsideBubble: [],
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

            // Ensure tempoBuckets is defined before merging
            if (!Array.isArray(mergedBubbles[j].tempoBuckets)) {
              mergedBubbles[j].tempoBuckets = new Array(10).fill(0);
            }

            centroids[i].tempoBuckets?.forEach((count, index) => {
              mergedBubbles[j].tempoBuckets[index] += count;
            });

            mergedBubbles[j].listOfCountriesInsideBubble.push(
              centroids[i].name
            );

            merged = true;
            break;
          }
        }

        if (!merged) {
          // Create a new bubble entry with color, name, and tempo bucket data
          mergedBubbles.push({
            centroid: centroids[i].centroid,
            count: 1,
            color: centroids[i].color,
            name: centroids[i].name,
            listOfCountriesInsideBubble: [centroids[i].name], // Initialize with country name
            tempoBuckets: [
              ...(centroids[i].tempoBuckets || new Array(10).fill(0)),
            ],
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
      svg.selectAll("rect").remove();
      svg.selectAll("path.bell").remove();

      // Draw bubbles and histograms
      mergedBubbles.forEach((bubble) => {
        let [x, y] = bubble.centroid;
        const color = bubble.color;

        const transform = d3.zoomTransform(svg.node());
        x = transform.applyX(x);
        y = transform.applyY(y);

        if (x < 0 || x > svg.attr("width") || y < 0 || y > svg.attr("height")) {
          return;
        }

        // Draw histogram above the bubble based on `tempoBuckets`
        const bucketWidth = 5;
        const maxCount = d3.max(bubble.tempoBuckets);
        const scaleY = d3.scaleLinear().domain([0, maxCount]).range([0, 30]);

        bubble.tempoBuckets.forEach((count, i) => {
          const barHeight = scaleY(count);

          svg
            .append("rect")
            .attr(
              "x",
              x -
                (bucketWidth * bubble.tempoBuckets.length) / 2 +
                i * bucketWidth
            )
            .attr("y", y - 20 - barHeight)
            .attr("width", bucketWidth)
            .attr("height", barHeight)
            .attr("fill", color)
            .attr("stroke", "black")
            .attr("stroke-width", 0.5);
        });

        // Add event listeners for tooltip
        svg
          .append("circle")
          .attr("class", "tooltip-circle")
          .attr("cx", x)
          .attr("cy", y)
          .attr("r", 10)
          .attr("fill", color)
          .attr("stroke", "white") // Adds a white stroke around the circle
          .attr("stroke-width", 2) // Increases the stroke width for better visibility
          .style("filter", "drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.5))") // Adds shadow for depth
          .on("mouseover", function (event) {
            // Show tooltip with list of countries inside this bubble
            tooltip
              .style("visibility", "visible")
              .text(bubble.listOfCountriesInsideBubble.join(" & "));

            tooltip
              .style("top", `${event.pageY + 10}px`)
              .style("left", `${event.pageX + 10}px`);
          })
          .on("mousemove", function (event) {
            tooltip
              .style("top", `${event.pageY + 10}px`)
              .style("left", `${event.pageX + 10}px`);
          })
          .on("mouseout", function () {
            tooltip.style("visibility", "hidden");
          });
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

.filter-container {
  margin: 20px;
  font-family: Arial, sans-serif;
  margin-right: 30px;
}

.filter-label {
  margin-right: 10px;
  font-weight: bold;
}

.custom-select {
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.custom-select:focus {
  border-color: #007bff;
  outline: none;
}
</style>
