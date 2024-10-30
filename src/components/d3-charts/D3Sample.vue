<template>
  <h1>Here is an example chart genereated with d3.js</h1>
  <div id="chart-container"></div>
</template>

<script>
import { defineComponent } from "vue";
import * as d3 from "d3";

export default defineComponent({
  mounted() {
    this.loadData();
  },
  methods: {
    MakeChart(data) {
      // Specify the chart’s dimensions.
      const width = 928;
      const height = Math.min(width, 500);

      // Create the color scale.
      const color = d3
        .scaleOrdinal()
        .domain(data.map((d) => d.letter))
        .range(
          d3
            .quantize((t) => d3.interpolateSpectral(t * 0.8 + 0.1), data.length)
            .reverse()
        );

      // Create the pie layout and arc generator.
      const pie = d3
        .pie()
        .sort(null)
        .value((d) => d.frequency);

      const arc = d3
        .arc()
        .innerRadius(0)
        .outerRadius(Math.min(width, height) / 2 - 1);

      const labelRadius = arc.outerRadius()() * 0.8;

      // A separate arc generator for labels.
      const arcLabel = d3
        .arc()
        .innerRadius(labelRadius)
        .outerRadius(labelRadius);

      const arcs = pie(data);
      console.log(arcs)

      // Create the SVG container.
      const svg = d3
        .select("#chart-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [-width / 2, -height / 2, width, height])
        .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;");

      // Add a sector path for each value.
      svg
        .selectAll()
        .data(arcs)
        .enter()
        .append("g")
        .attr("stroke", "white")
        .append("path")
        .attr("fill", (d) => color(d.data.letter))
        .attr("d", arc)
        .append("title")
        .text((d) => `${d.data.letter}: ${d.data.frequency.toLocaleString("en-US")}`);

      // Create a new arc generator to place a label close to the edge.
      // The label shows the value if there is enough room.
      svg
        .append("g")
        .attr("text-anchor", "middle")
        .selectAll()
        .data(arcs)
        .join("text")
        .attr("transform", (d) => `translate(${arcLabel.centroid(d)})`)
        .call((text) =>
          text
            .append("tspan")
            .attr("y", "-0.4em")
            .attr("font-weight", "bold")
            .text((d) => d.data.letter)
        )
        .call((text) =>
          text
            .filter((d) => d.endAngle - d.startAngle > 0.25)
            .append("tspan")
            .attr("x", 0)
            .attr("y", "0.7em")
            .attr("fill-opacity", 0.7)
            .text((d) => d.data.frequency.toLocaleString("en-US"))
        );

      return svg.node();
    },
    loadData() {
      d3.csv("src/datasets/SampleData.csv").then((data) => {
        data.forEach((d) => {
          d.frequency = +d.frequency; // convert frequency to numbers
        });
        this.dataset = data;
        this.MakeChart(this.dataset);
      });
    },
  },
});
</script>