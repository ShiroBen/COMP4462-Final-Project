<template>
  <h1>World Map with Bubbles</h1>
  <div id="map-container"></div>
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
  data() {
    return {
      tempoBuckets: null, // Initialize tempoBuckets as null to store the data later
    };
  },
  mounted() {
    this.createTempoHistogram("src/datasets/cartogram.countries.data.json"); // Call with the JSON path
  },
  methods: {
    createTempoHistogram(jsonPath) {
      // Load JSON data and calculate tempo buckets
      d3.json(jsonPath).then((data) => {
        // Extract all tempo values across all countries to determine the global min and max
        const allTempos = [];
        for (const country in data.tempo) {
          allTempos.push(...data.tempo[country]);
        }
        const globalMin = d3.min(allTempos);
        const globalMax = d3.max(allTempos);

        // Calculate bucket size
        const bucketSize = (globalMax - globalMin) / 10;

        // Prepare the histogram data for each country
        const countryBuckets = {};

        for (const country in data.tempo) {
          const countryTempos = data.tempo[country];
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
        console.log("Tempo Buckets:", this.tempoBuckets);

        // Call loadMapData once tempoBuckets are ready
        this.loadMapData();
      });
    },
    drawMap(geojson) {
      console.log(this.tempoBuckets.Germany);

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
        tempoBuckets: this.tempoBuckets[feature.properties.name] || new Array(10).fill(0),
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

        // Append the bubble with the adjusted coordinates as a square
        svg
          .append("rect")
          .attr("x", x - 10) // Center the square at (x, y)
          .attr("y", y - 10)
          .attr("width", 20)
          .attr("height", 20)
          .attr("fill", color);

        // Draw histogram above the bubble based on `tempoBuckets`
        const bucketWidth = 5;
        const maxCount = d3.max(bubble.tempoBuckets);
        const scaleY = d3.scaleLinear().domain([0, maxCount]).range([0, 30]); // Set maximum height of the histogram

        console.log(bubble.tempoBuckets);
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
</style>
