<template>
  <div style="display: flex; height: 100%; width: 100%;">
    <div ref="map-root" style="flex: 1; position: relative; height:100%">
      <div ref="tooltip" class="tooltip" v-if="tooltipContent">
        {{ tooltipContent }}
      </div>
    </div>
    <div class="filter-container">
      <label for="filter-selector" class="filter-label">Choose Variable:</label>
      <select id="filter-selector" v-model="selectedFeature" @change="updateMap">
        <option disabled value="">Select an option...</option>
        <option value="danceability">Danceability</option>
        <option value="liveness">Liveness</option>
        <option value="Streams">Streams</option>
        <option value="energy">Energy</option>
        <option value="loudness">Loudness</option>
        <option value="valence">Valence</option>
        <option value="acousticness">Acousticness</option>
      </select>
      <div class="color-legend" ref="legend"></div>
      <div ref="barChart" class="bar-chart"></div> <!-- Bar chart container below the map -->
    </div>
  </div>
</template>

<script>
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import XYZ from 'ol/source/XYZ';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import { fromLonLat } from 'ol/proj';
import { Style, Fill, Stroke } from 'ol/style';
import GeoJSON from 'ol/format/GeoJSON';
import * as d3 from 'd3';
import d3tip from 'd3-tip';

export default {
  name: 'MapContainer',
  data() {
    return {
      geojsonCountries: null,
      danceabilityData: {},
      selectedFeature: 'danceability',
      tooltipContent: null,
      csvData: [],
      selectedCountries: [],
      //colorScale: null,
      //map: null, // Store the map instance
      //vectorLayer: null, // Store the vector layer
    };
  },
  mounted() {
    // Load the GeoJSON and CSV data
    Promise.all([
      this.loadGeoJSON('geo.json'), // Adjust path to your geo.json
      d3.csv('src/datasets/combined_processed_2.csv'), // Adjust path to your CSV file
    ])
      .then(([geojsonData, csvData]) => {
        this.geojsonCountries = geojsonData;
        this.csvData = csvData;
        this.danceabilityData = this.processCSVData(csvData);
        this.initMap();
        this.updateLegend();
        this.updateBarChart();
        this.overallData = this.processAllCSVData(csvData);
      })
      .catch(error => {
        alert('Failed to load data: ' + error);
      });
  },
  methods: {
    updateMap() {
      // Update danceabilityData based on the newly selected feature
      this.danceabilityData = {};
      this.danceabilityData = this.processCSVData(this.csvData);
      this.updateLegend();
      this.selectedCountries = []; // Clear selected countries
      this.updateBarChart();
      // Update the vector layer's style
      if (this.vectorLayer) {
        this.vectorLayer.setStyle(this.getStyle.bind(this));
        this.vectorLayer.getSource().clear(); // Clear existing features
        this.vectorLayer.getSource().addFeatures(new GeoJSON().readFeatures(this.geojsonCountries, {
          dataProjection: 'EPSG:4326',
          featureProjection: 'EPSG:3857',
        }));
      }
    },
    loadGeoJSON(url) {
      return d3.json(url);
    },
    processCSVData(csvData) {
      const featureMap = {};
      const countMap = {};
      // Process the CSV data
      csvData.forEach(d => {
        const country = d.country;
        const featureValue = +d[this.selectedFeature]; // Use selected feature
        if (!featureMap[country]) {
          featureMap[country] = 0;
          countMap[country] = 0;
        }
        // Accumulate the feature value and count
        featureMap[country] += featureValue;
        countMap[country] += 1;
      });

      // Calculate the average for each country based on the selected feature
      const averageFeatureMap = {};
      Object.keys(featureMap).forEach(country => {
        averageFeatureMap[country] = featureMap[country] / countMap[country];
      });

      // Get countries from the GeoJSON and ensure they have a value
      const countriesFromGeoJSON = new Set(this.geojsonCountries.features.map(feature => feature.properties.name));

      // Set value to 0 for countries not in the CSV data
      countriesFromGeoJSON.forEach(country => {
        if (!(country in averageFeatureMap)) {
          averageFeatureMap[country] = 0; // Set value to 0 for countries not present in the CSV
        }
      });

      return averageFeatureMap;
    },

    processAllCSVData(csvData) {
      const featureMap = {};
      csvData.forEach(d => {
        const country = d.country;
        if (!featureMap[country]) {
          featureMap[country] = {
            acousticness: 0,
            instrumentalness: 0,
            danceability: 0,
            // Add other features as necessary
            count: 0,
          };
        }

        // Accumulate feature values
        for (const feature in featureMap[country]) {
          if (feature !== 'count') {
            featureMap[country][feature] += +d[feature] || 0;
          }
        }
        featureMap[country].count += 1; // Increment count for averaging later
      });

      // Calculate averages for each feature
      this.overallData = Object.keys(featureMap).map(country => {
        const features = featureMap[country];
        return {
          country,
          acousticness: features.acousticness / features.count,
          instrumentalness: features.instrumentalness / features.count,
          danceability: features.danceability / features.count,
          // Add other features as necessary
        };
      });
    },
    
    initMap() {
      const rasterLayer = new TileLayer({
        source: new XYZ({
          url: 'https://{a-c}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        }),
      });

      const vectorSource = new VectorSource({
        features: new GeoJSON().readFeatures(this.geojsonCountries, {
          dataProjection: 'EPSG:4326',
          featureProjection: 'EPSG:3857',
        }),
      });

      this.vectorLayer = new VectorLayer({
        source: vectorSource,
        style: this.getStyle.bind(this), // Bind the style method for dynamic styling
      });

      // Create the map only once
      if (!this.map) {
        this.map = new Map({
          target: this.$refs['map-root'],
          layers: [rasterLayer, this.vectorLayer],
          view: new View({
            zoom: 1,
            center: fromLonLat([15, 20]), // Center the map appropriately
          }),
        });
        
        this.addHoverInteraction(this.vectorLayer);
      }
    },

     
    updateBarChart() {
      
      const dummyData = this.selectedCountries
      .map(name => ({
        name,
        value: this.danceabilityData[name] || 0,
      }))
      .filter(d => d.value > 0); 
      // Clear existing chart
      const svg = d3.select(this.$refs.barChart)
        .selectAll("*").remove();

      const margin = { top: 20, right: 0, bottom: 40, left: 35 };
      const width = 185;
      const height = 70 * this.selectedCountries.length;

      // Create scales
      const x = d3.scaleLinear()
        .domain([d3.min(dummyData, d => d.value) - 0.1, d3.max(dummyData, d => d.value)])
        .range([0, width]);


      const y = d3.scaleBand()
        .domain(dummyData.map(d => d.name))
        .range([0, height])
        .padding(0.2);

      

      const svgContainer = d3.select(this.$refs.barChart) // Select the container again
        .append("svg")
        .attr("width", width + margin.left)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

      const tooltip = d3tip()
        .style('border', 'solid 3px black')
        .style('background-color', 'white')
        .style('border-radius', '10px')
        .style('font-family', 'monospace')
        .html((event, d) => `
          <div>
            <strong>Country:</strong> ${d.name}<br/>
            <strong>Value:</strong> ${d.value}<br/>
          </div>`);

      svgContainer.call(tooltip);
       
      // Create horizontal bars
      svgContainer.selectAll('rect')
        .data(dummyData)
        .enter()
        .append("rect")
          .attr("class", "bar")
          .attr("y", d => y(d.name))
          .attr("x", 0) // Start from the left
          .attr("height", y.bandwidth())
          .attr("width", d => x(d.value))
          .attr("fill", "steelblue")
          .style('stroke', 'black')
          .on('mouseover', function (event, d) {
            d3.select(this)
              .attr('opacity', 0.5)
          })
          .on('mouseover', tooltip.show)  
          // Listen to the "mouseout" event, and reset the value of "hovering" and color
          .on('mouseout', function (event, d) {
            d3.select(this)
              .attr('opacity', 1)
          })
          .on ('mouseout', tooltip.hide);

      // Add the x-axis
      svgContainer.append("g")
        .attr("class", "axis axis-x")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(10).tickValues(d3.range(d3.min(dummyData, d=> d.value) - 0.1, d3.max(dummyData, d => d.value) + 0.1, 0.05)));

      // Add the y-axis
      const yAxis = svgContainer.append("g")
        .attr("class", "axis axis-y")
        .call(d3.axisLeft(y));

      yAxis.selectAll(".tick text") // Use .tick text to select only the text elements of the ticks
          .attr("transform", "rotate(-90)") // Rotate labels 45 degrees
          .attr("dy", "-1.5em") // Adjust vertical alignment
          .attr("dx", "2em") // Adjust horizontal position
          .style("text-anchor", "end") // Align text to the end
          .style("font-size", "15px"); // Increase font size (adjust as needed)

    },

    updateLegend() {
      const legend = d3.select(this.$refs.legend);
      legend.selectAll("*").remove(); // Clear existing legend items

      // Get the feature values for the current selected feature
      const featureValues = Object.values(this.danceabilityData);
      const minFeature = d3.min(featureValues.filter(value => (value != 0 && value < 1000000)));
      const maxFeature = d3.max(featureValues.filter(value => (value != 0 && value < 1000000)));

      // Create a linear color scale based on the feature values
      const colorScale = d3.scaleSequential(d3.interpolateBlues)
        .domain([minFeature, maxFeature]);

      // Dimensions for the legend
      const legendWidth = 220;
      const legendHeight = 25;

      // Create an SVG element for the legend
      const svg = legend.append("svg")
        .attr("width", legendWidth)
        .attr("height", legendHeight + 30); // Additional height for labels

      // Create a gradient for the legend
      const gradient = svg.append("defs").append("linearGradient")
        .attr("id", "gradient");

      // Define gradient stops
      gradient.selectAll("stop")
        .data(d3.range(0, 1, 0.01)) // Create stops from 0 to 1
        .enter().append("stop")
          .attr("offset", d => `${d * 100}%`)
          .attr("stop-color", d => colorScale(minFeature + d * (maxFeature - minFeature))); // Use the color scale

      // Create a rectangle for the gradient
      svg.append("rect")
        .attr("width", legendWidth)
        .attr("height", legendHeight)
        .style("fill", "url(#gradient)")
        .style("stroke", "black")
        .style("stroke-width", 1);

      function formatNumber(num) {
        if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M'; // Millions
        if (num >= 1e3) return (num / 1e3).toFixed(1) + 'k'; // Thousands
        if (num < 1) return (num.toFixed(2));
        return num.toString(); // Fallback for smaller numbers
      }

      // Add text labels for the min and max values
      svg.append("text")
        .attr("x", 0) // Position at the left end
        .attr("y", legendHeight + 12) // Position below the legend
        .attr("text-anchor", "start") // Align text to start
        .attr ("font-size", "12px") // font size
        .text(formatNumber(minFeature)); // Display minimum value

      svg.append("text")
        .attr("x", legendWidth) // Position at the right end
        .attr("y", legendHeight + 12) // Position below the legend
        .attr("text-anchor", "end") // Align text to end
        .attr ("font-size", "12px") // font size
        .text(formatNumber(maxFeature)); // Display maximum value
      
    },
    
    addHoverInteraction(layer) {
      const defaultStyle = layer.getStyleFunction();
      
      // Define a function to get the fill color based on the feature data
      const getFillColor = (feature) => {
        const countryName = feature.get('name');
        const featureValue = this.danceabilityData[countryName];

        // Calculate min and max for the color scale
        const featureValues = Object.values(this.danceabilityData);
        const minFeature = d3.min(featureValues.filter(value => value != 0));
        const maxFeature = d3.max(featureValues.filter (value => value != 0));

        // Create a color scale based on the feature value
        const colorScale = d3.scaleSequential(d3.interpolateBlues)
          .domain([minFeature, maxFeature]);

        this.colorScale = colorScale;

        return (featureValue !== undefined && featureValue != 0) ? colorScale(featureValue) : 'rgba(0,0,0,0.25)'; // Default color if no value
      };

      let currentlyHighlightedFeature = null; // To keep track of the currently highlighted feature
      this.tooltipContent = null; // Tooltip content management

      const highlightFeature = (feature) => {
        const fillColor = getFillColor(feature); // Get the fill color based on the feature value
        const highlightStyle = new Style({
          fill: new Fill({
            color: fillColor, // Keep the original fill color based on the feature value
          }),
          stroke: new Stroke({
            color: 'black', // Change stroke color to black
            width: 2.5, // Make the stroke thicker
          }),
        });

        feature.setStyle(highlightStyle);
        currentlyHighlightedFeature = feature; // Update the currently highlighted feature

        // Update the tooltip content
        const countryName = feature.get('name');
        const featureValue = this.danceabilityData[countryName];
        if (featureValue == 0){
          this.tooltipContent = `${countryName}: No Data Available`; // If no data available
        } else {
          this.tooltipContent = `${countryName}: ${featureValue.toFixed(2)}`; // Format value to two decimal places
        }
      };

      const resetFeature = (feature) => {
        feature.setStyle(defaultStyle(feature));
      };

      // Pointer move event
      this.map.on('pointermove', (evt) => {
        const feature = this.map.forEachFeatureAtPixel(evt.pixel, (feature) => feature);
        if (feature) {
          // If the hovered feature is different from the currently highlighted feature
          if (currentlyHighlightedFeature !== feature) {
            // Reset the style of the previously highlighted feature
            if (currentlyHighlightedFeature) {
              resetFeature(currentlyHighlightedFeature);
            }
            // Highlight the new feature
            highlightFeature(feature);
          }
          
          // Show tooltip
          this.$refs.tooltip.style.display = 'block';
          this.$refs.tooltip.style.left = `${evt.pixel[0] + 10}px`;
          this.$refs.tooltip.style.top = `${evt.pixel[1] + 10}px`;
        } else {
          // If no feature is hovered, reset the currently highlighted feature
          if (currentlyHighlightedFeature) {
            resetFeature(currentlyHighlightedFeature);
            currentlyHighlightedFeature = null; // Clear the currently highlighted feature
          }
          this.tooltipContent = null; // Hide tooltip
          this.$refs.tooltip.style.display = 'none'; // Hide tooltip
        }
      });

      // Pointer leave event
      this.map.on('pointerleave', () => {
        if (currentlyHighlightedFeature) {
          resetFeature(currentlyHighlightedFeature);
          currentlyHighlightedFeature = null; // Clear the currently highlighted feature
        }
        this.tooltipContent = null; // Hide tooltip
        this.$refs.tooltip.style.display = 'none'; // Hide tooltip
      });

      this.map.on('singleclick', (evt) => {
        const feature = this.map.forEachFeatureAtPixel(evt.pixel, (feature) => feature);
        if (feature) {
          const countryName = feature.get('name');
          const countryValue = this.danceabilityData[countryName] || 0; // Get the value for the country

          // Proceed only if the value is greater than 0
          if (countryValue > 0) {
            if (this.selectedCountries.includes(countryName)) {
              // Deselect if already selected
              this.selectedCountries = this.selectedCountries.filter(c => c !== countryName);
            } else {
              // Ensure only two countries can be selected
              if (this.selectedCountries.length >= 3) {
                this.selectedCountries.shift(); // Remove the first country if two are already selected
              }
              this.selectedCountries.push(countryName); // Add the new country
            }
            this.updateBarChart(); // Update the bar chart based on selection
          }
        }
      });
    },
    getStyle(feature) {
      const countryName = feature.get('name');
      const featureValue = this.danceabilityData[countryName];

      const featureValues = Object.values(this.danceabilityData);
      const minFeature = d3.min(featureValues.filter(value => value != 0));
      const maxFeature = d3.max(featureValues.filter (value => value != 0));

      const colorScale = d3.scaleSequential(d3.interpolateBlues)
        .domain([minFeature, maxFeature]);

      return new Style({
        fill: new Fill({
          color: (countryName === 'Antarctica') 
            ? 'rgba(0, 0, 0, 0)' 
            : ((featureValue !== undefined && featureValue !=0) ? colorScale(featureValue) : 'rgba(0, 0, 0, 0.25)'),
        }),
        stroke: new Stroke({
          color: (countryName === 'Antarctica') 
            ? 'rgba(0, 0, 0, 0)' 
            : 'black',
          width: 1,
        }),
      });
    },
  },
};
      
    
</script>

<style scoped>
.tooltip {
  position: absolute;
  background: white;
  color: black;
  border: 1px solid black;
  padding: 5px;
  pointer-events: none; /* Prevent tooltip from interfering with mouse events */
  z-index: 10;
  display: none; /* Initially hidden */
}

.filter-container {
  display: flex;
  flex-direction: column; /* Stack label and select vertically */
  padding: 10px; /* Add padding */
}

.filter-label {
  font-size: 1.0em; /* Set the font size to smaller */
  margin-bottom: 10px; /* Space between label and select */
}

select {
  padding: 5px; /* Padding for select */
  border: 1px solid #ccc; /* Border for select */
  border-radius: 4px; /* Rounded corners */
}

.bar-chart {
  margin-top: 20px; /* Space above the bar chart */
  margin-left: 0px;
  margin-right: 0px;
  width: 100%; /* Width of the bar chart */
}

.color-legend {
  display: flex;
  flex-direction: column; /* Stack legend items vertically */
  margin-top: 15px;
  margin-left: 2px;
}

.color-legend div {
  height: 20px; /* Height for each legend item */
  line-height: 20px; /* Center text vertically */
  color: #000; /* Text color */
  padding-left: 5px; /* Space between text and background */
}

</style>