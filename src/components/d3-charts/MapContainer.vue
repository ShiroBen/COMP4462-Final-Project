<template>
  <div ref="map-root" style="width: 100%; height: 100%; position: relative;">
    <div ref="tooltip" class="tooltip" v-if="tooltipContent">
      {{ tooltipContent }}
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

export default {
  name: 'MapContainer',
  data() {
    return {
      geojsonCountries: null,
      danceabilityData: {},
      selectedFeature: 'danceability',
      tooltipContent: null,
    };
  },
  mounted() {
    // Load the GeoJSON and CSV dat
    Promise.all([
      this.loadGeoJSON('geo.json'), // Adjust path to your geo.json
      d3.csv('src/datasets/combined_processed_2.csv'), // Adjust path to your CSV file
    ])
      .then(([geojsonData, csvData]) => {
        this.geojsonCountries = geojsonData;
        this.danceabilityData = this.processCSVData(csvData);
        this.initMap();
      })
      .catch(error => {
        alert ('Failed to load data:');
      });
  },
  methods: {
    updateMap() {
      this.danceabilityData = this.processCSVData(this.csvData);
      this.initMap();
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
      const countriesFromGeoJSON = new Set(this.geojsonCountries.features.map(feature => feature.properties.name)); // Adjust to match the property name in your GeoJSON

      // Set value to 0 for countries not in the CSV data
      countriesFromGeoJSON.forEach(country => {
        if (!(country in averageFeatureMap)) {
          averageFeatureMap[country] = 0; // Set value to 0 for countries not present in the CSV
        }
      });

      return averageFeatureMap;
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

      const vectorLayer = new VectorLayer({
        source: vectorSource,
        style: this.getStyle.bind(this), // Bind the style method for dynamic styling
      });
      // Create the map
      this.map = new Map({
        target: this.$refs['map-root'],
        layers: [rasterLayer, vectorLayer],
        view: new View({
          zoom: 2,
          center: fromLonLat([0, 20]), // Center the map appropriately
        }),
      });
      
      this.addHoverInteraction(vectorLayer);
    },
    
    addHoverInteraction(layer) {
      const defaultStyle = layer.getStyleFunction();
      
      // Define a function to get the fill color based on the feature data
      const getFillColor = (feature) => {
        const countryName = feature.get('name');
        const featureValue = this.danceabilityData[countryName];

        // Calculate min and max for the color scale
        const featureValues = Object.values(this.danceabilityData);
        const minFeature = d3.min(featureValues.filter(value => value > 0));
        const maxFeature = d3.max(featureValues);

        // Create a color scale based on the feature value
        const colorScale = d3.scaleSequential(d3.interpolateBlues)
          .domain([minFeature, maxFeature]);

        return featureValue !== undefined ? colorScale(featureValue) : 'rgba(213, 222, 255, 0.4)'; // Default color if no value
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
    },
    getStyle(feature) {
      const countryName = feature.get('name');
      const featureValue = this.danceabilityData[countryName];

      const featureValues = Object.values(this.danceabilityData);
      const minFeature = d3.min(featureValues.filter(value => value > 0));
      const maxFeature = d3.max(featureValues);

      const colorScale = d3.scaleSequential(d3.interpolateBlues)
        .domain([minFeature, maxFeature]);

      return new Style({
        fill: new Fill({
          color: (countryName === 'Antarctica') 
            ? 'rgba(0, 0, 0, 0)' 
            : ((featureValue !== undefined && featureValue !=0) ? colorScale(featureValue) : 'rgba(213, 222, 255, 0.4)'),
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
</style>