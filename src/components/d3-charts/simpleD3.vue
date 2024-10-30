<template>
  <h1>a sample bar chart</h1>
  <div id="bar-chart-container"></div>
</template>
 
<script>
import { defineComponent } from "vue";
import * as d3 from "d3";

export default defineComponent({
  mounted() {
    this.loadData();
  },
  methods: {
    drawBarChart(dataset) {
      const w = 1200;
      const h = 500;
      const color = d3.schemeCategory10;

      const padding = 200;
      const bargap = (w - 2*padding) / dataset.length;
      const barwidth = bargap * 2 / 3;
      const barheight = (freq) => {return freq * 2000};

      var svg = d3
        .select("#bar-chart-container")
        .append("svg")
        .attr("width", w)
        .attr("height", h);

      var rect = svg
        .selectAll("rect")
        .data(dataset)
        .enter()
        .append("rect")
        .attr("x", function (d, i) {
          return padding + i * bargap;
        })
        .attr("y", function (d) {
          return h - barheight(d.frequency) - 50;
        })
        .attr("width", barwidth)
        .attr("height", function (d) {
          return barheight(d.frequency)
        })
        .attr("fill", function (d, i) {
          return color[i % 10];
        });

      var number = svg
        .selectAll()
        .data(dataset)
        .enter()
        .append("text")
        .attr("fill", "black")
        .attr("x", function (d, i) {
          return padding + i * bargap;
        })
        .attr("y", function (d) {
          return h - barheight(d.frequency) - 65;
        })
        .attr("font-size", 14)
        .text(function (d) {
          return Math.round(d.frequency * 1000) / 10 + "%";
        });

      var index = svg
        .selectAll()
        .data(dataset)
        .enter()
        .append("text")
        .attr("fill", "black")
        .attr("x", function (d, i) {
          return padding + bargap * i + barwidth / 3;
        })
        .attr("y", h-15)
        .attr("font-size", 14)
        .text(function (d, i) {
          return d.letter;
        });
    },
    loadData() {
      d3.csv("src/datasets/SampleData.csv").then((data) => {
        data.forEach((d) => {
          d.frequency = +d.frequency; // convert frequency to numbers
        });
        this.dataset = data;
        this.drawBarChart(this.dataset);
      });
    },
  },
});
</script>