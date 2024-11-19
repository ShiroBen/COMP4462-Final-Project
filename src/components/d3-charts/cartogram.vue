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
    this.createTempoHistogram("src/datasets/cartogram.countries.data.json"); // Call with the JSON path
  },
  methods: {
    changeVariable() {
      this.closeMap();
      console.log("selected feature is ", this.selectedFeature);
      this.createTempoHistogram("src/datasets/cartogram.countries.data.json");
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
      const countriesThatAreInDataset = [
        "Lithuania",
        "Latvia",
        "Germany",
        "France",
        "Ireland",
        "Japan",
        "Philippines",
        "India",
        "Guatemala",
        "Canada",
        "Costa Rica",
        "United Kingdom",
        "United States of America",
        "Malaysia",
        "Bolivia",
        "Italy",
        "Mexico",
        "Colombia",
        "Netherlands",
        "Brazil",
        "Norway",
        "Ecuador",
        "Iceland",
        "Greece",
        "Estonia",
        "Sweden",
        "Australia",
        "Taiwan",
        "Denmark",
        "Dominican Republic",
        "Turkey",
        "Hungary",
        "El Salvador",
        "Honduras",
        "Belgium",
        "South Korea",
        "Austria",
        "Uruguay",
        "Panama",
        "Spain",
        "Finland",
        "Paraguay",
        "Peru",
        "Luxembourg",
        "Chile",
        "New Zealand",
        "Portugal",
        "Czech Republic",
        "China",
        "Poland",
        "Argentina",
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
            tempoBuckets: [
              ...(centroids[i].tempoBuckets || new Array(10).fill(0)),
            ], // Copy or default to empty array
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

        // Adjust x, y coordinates by the current zoom transformation
        const transform = d3.zoomTransform(svg.node());
        x = transform.applyX(x);
        y = transform.applyY(y);

        // Check if the bubble is within the visible bounds of the SVG
        if (x < 0 || x > svg.attr("width") || y < 0 || y > svg.attr("height")) {
          return; // Skip drawing this bubble if it's outside the viewport
        }
        // Draw histogram above the bubble based on `tempoBuckets`
        const bucketWidth = 5;
        const maxCount = d3.max(bubble.tempoBuckets);
        const scaleY = d3.scaleLinear().domain([0, maxCount]).range([0, 30]); // Set maximum height of the histogram

        bubble.tempoBuckets.forEach((count, i) => {
          // Calculate the height of each bar based on bucket count
          const barHeight = scaleY(count);

          // Append a rectangle for each histogram bar
          svg
            .append("rect")
            .attr(
              "x",
              x -
                (bucketWidth * bubble.tempoBuckets.length) / 2 +
                i * bucketWidth
            )
            .attr("y", y - 20 - barHeight) // Position above the bubble
            .attr("width", bucketWidth)
            .attr("height", barHeight)
            .attr("fill", color)
            .attr("stroke", "black")
            .attr("stroke-width", 0.5);
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
