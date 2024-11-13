<template>
    <div class="container">
      <div class="label-container">
        <router-link to="/SpatialDV" class="label" active-class="active">Choropleth</router-link>
        <router-link to="/sankey" class="label" active-class="active">Sankey</router-link>
        <router-link to="/cartogram" class="label" active-class="active">Cartogram</router-link>
      </div>
      <h1>This is Sankey</h1>
    </div>
  </template>
  
  <script lang="ts">
  export default {
    name: 'Sankey',
  };
  </script>
  
  <script setup lang="ts">
  import { RouterLink } from 'vue-router'; // Import RouterLink for navigation
  </script>
  
  <style scoped>
  .choropleth-container {
    padding: 20px; /* Add padding to the container for spacing */
    background-color: #ffffff; /* Set background to white for main content */
  }
  
  .label-container {
    display: flex;                    /* Use flexbox for horizontal layout */
    justify-content: space-around;    /* Evenly distribute space */
    padding: 10px 0;                 /* Add padding to the label container */
    border-bottom: 2px solid #333;    /* Add a bottom border for separation */
  }
  
  .label {
    text-decoration: none;            /* Remove underline */
    color: black;                     /* Text color */
    transition: color 0.3s;          /* Smooth transition for color */
    padding: 10px 15px;               /* Padding for clickable area */
  }
  
  .label:hover {
    color: green;                   /* Change color on hover to match app theme */
  }
  
  .label.active {
    color: #42b983;                   /* Change color when active (clicked) */
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
  </style>