<template>
  <div>
    <div class="label-container">
      <router-link to="/SpatialDV" class="label" active-class="active">Choropleth</router-link>
      <router-link to="/sankey" class="label" active-class="active">Sankey</router-link>
      <router-link to="/cartogram" class="label" active-class="active">Cartogram</router-link>
    </div>
    <h1>This is Default Choropleth</h1>
    
    <div class="map-container">
      <MapContainer />
      <div class="filter-container">
        <label for="filter-selector" class="filter-label">Choose Variable:</label>
        <select id="filter-selector">
          <option disabled selected value="">Select an option...</option>
          <option value="option1">Danceability</option>
          <option value="option2">Instrumentalness</option>
          <option value="option3">Streams</option>
          <option value="option4">More</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import MapContainer from '../components/d3-charts/MapContainer.vue'; // Adjust the path as necessary

export default {
  name: 'SpatialDV',
};
</script>

<script setup lang="ts">
import { RouterLink } from 'vue-router'; // Import RouterLink for navigation
</script>

<style>
.label-container {
  display: flex;                    
  justify-content: space-around;    
  padding: 10px 0;                 
  border-bottom: 2px solid #333;    
}

.label {
  text-decoration: none;            
  color: black;                     
  transition: color 0.3s;          
  padding: 10px 15px;               
  position: relative;               
}

.label:hover {
  color: #66d6a1;                   
}

.label.active,
.label.exact-active {
  color: #66d6a1;                   
}

.label:not(:last-child)::after {
  content: '';                    
  display: inline-block;          
  width: 2px;                     
  height: 20px;                  
  background-color: #333;         
  margin-left: 150px;   
  vertical-align: middle;          
}

/* Style for the map container */
.map-container {
  display: flex; /* Use flexbox to align map and filter container */
  justify-content: space-between; /* Space between map and filter */
  width: 100%;         
  height: 450px;      
  margin-top: 20px;   
  border: 1px solid #ccc; /* Optional: Add a border for visibility */
}

/* Style for the filter container */
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
</style>