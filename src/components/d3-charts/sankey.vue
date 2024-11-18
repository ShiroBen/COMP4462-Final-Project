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
    //this.drawMap();
    this.drawSankeyDiagram([
  { id: "USA" },
  { id: "China" },
  { id: "Germany" },
  { id: "France" },
  { id: "India" }
], [
  { source: "USA", target: "China", value: 10 },
  { source: "Germany", target: "France", value: 5 },
  { source: "India", target: "USA", value: 8 }
])
  },
  methods: {
    drawSankeyDiagram(nodes, links) {
    const width = 800;
    const height = 500;

    // Set up the SVG container
    const svg = d3
      .select("#map-container")
      .append("svg")
      .attr("width", width)
      .attr("height", height);

    // Initialize the Sankey diagram generator
    const sankeyGenerator = sankey()
      .nodeWidth(36) // Width of the nodes
      .nodePadding(40) // Space between nodes
      .size([width, height]);

    // Create a map from node ids to indices
    const nodeIdToIndex = new Map();
    nodes.forEach((node, index) => {
      nodeIdToIndex.set(node.id, index);
    });

    // Convert links to use indices rather than node ids
    const indexedLinks = links.map(link => ({
      source: nodeIdToIndex.get(link.source),
      target: nodeIdToIndex.get(link.target),
      value: link.value
    }));

    // Generate the Sankey nodes and links with automatic layout
    const { nodes: sankeyNodes, links: sankeyLinks } = sankeyGenerator({
      nodes: nodes.map(d => ({ ...d })),
      links: indexedLinks
    });

    // Custom node positions (dynamically set)
    sankeyNodes.forEach((node, index) => {
      // Example of setting custom positions:
      node.x0 = index * (width / sankeyNodes.length); // Custom x0 position
      node.y0 = 100 + Math.random() * 100; // Custom y0 position
      node.x1 = node.x0 + 100; // Node width
      node.y1 = node.y0 + 50; // Node height
    });

    // Draw the links (edges)
    svg
      .append("g")
      .selectAll(".link")
      .data(sankeyLinks)
      .enter()
      .append("path")
      .attr("class", "link")
      .attr("d", sankeyLinkHorizontal())
      .attr("fill", "none")
      .attr("stroke", "#888")
      .attr("stroke-width", d => Math.max(1, d.width))
      .attr("opacity", 0.6);

    // Draw the nodes with custom positions
    svg
      .append("g")
      .selectAll(".node")
      .data(sankeyNodes)
      .enter()
      .append("rect")
      .attr("class", "node")
      .attr("x", d => d.x0)
      .attr("y", d => d.y0)
      .attr("width", d => d.x1 - d.x0)
      .attr("height", d => d.y1 - d.y0)
      .attr("fill", "#8a2be2")
      .attr("stroke", "#444")
      .append("title")
      .text(d => `${d.id}: ${d.value}`);

    // Add labels to the nodes
    svg
      .append("g")
      .selectAll(".node-label")
      .data(sankeyNodes)
      .enter()
      .append("text")
      .attr("class", "node-label")
      .attr("x", d => (d.x0 + d.x1) / 2)
      .attr("y", d => (d.y0 + d.y1) / 2)
      .attr("dy", ".35em")
      .attr("text-anchor", "middle")
      .attr("fill", "white")
      .text(d => d.id);
  }
,
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
