<template>
  <div ref="map-root" style="width: 100%; height: 100%;"></div>
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
        style: (feature) => {
          const countryName = feature.get('name');
          const featureValue = this.danceabilityData[countryName]; // Use the selected feature data

          // Calculate min and max for the color scale
          const featureValues = Object.values(this.danceabilityData);
          const minFeature = d3.min(featureValues);
          const maxFeature = d3.max(featureValues);

          const colorScale = d3.scaleSequential(d3.interpolateBlues)
            .domain([minFeature, maxFeature]); // Set domain based on the selected feature

          return new Style({
            fill: new Fill({
              color: (countryName === 'Antarctica') 
                ? 'rgba(0, 0, 0, 0)' // Transparent color for Antarctica
                : (featureValue !== undefined ? colorScale(featureValue) : 'rgba(213, 222, 255, 0.4)'),
            }),
            stroke: new Stroke({
              color: (countryName === 'Antarctica') 
                ? 'rgba(0, 0, 0, 0)' // Transparent stroke for Antarctica
                : 'black', // Dark grey stroke color for other countries
              width: 1,
            }),
          });
        },
      });
      // Create the map
      new Map({
        target: this.$refs['map-root'],
        layers: [rasterLayer, vectorLayer],
        view: new View({
          zoom: 2,
          center: fromLonLat([0, 20]), // Center the map appropriately
        }),
      });
    },
  },
};
</script>

<style scoped>
/* Optional styles for MapContainer */
</style>