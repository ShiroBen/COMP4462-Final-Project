<template>
  <div class='appContainer'>
    <!-- header of the app -->
    <div class='appHeader'>
      <h1> Welcome to our project for visualizing Spotify data. </h1>
    </div>

    <!-- main body of the app (overview of our visualization) -->
    <div class='visOverview'>
      
    </div>

    <!-- navigate into time or spatial data -->
    <div>
      <TimeOrSpatial></TimeOrSpatial>
    </div>
  </div>
</template>

<script lang="ts">
  export default { name: 'App' }
</script>


<script setup lang="ts">
  import { RouterLink, RouterView } from 'vue-router'
  import TimeOrSpatial from './components/TimeOrSpatial.vue';
</script>

<style scoped>
  .appContainer {
    background-color: white;
    min-width: 80vw;
    min-height: 80vh;
    margin: 0;
    padding: 0;
  }

  .appHeader {
    display: block;
    background-color: white;
    color: black;

  }

  .visOverview {
    min-height: 60vh;
  }
</style>
