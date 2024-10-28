<template>
  <!-- Choose which one to display -->
  <div class='choices'>
  <h1>Hello, users!</h1>
  <RouterLink :to="{name:'TimeDV'}"> Time Series Data Visulization </RouterLink>
  <RouterLink :to="{name:'SpatialDV'}"> Spatial Data Visualization </RouterLink>
  </div>

  <!-- The display section -->
  <div class='visDisplay'> 
    <RouterView/>
  </div>
</template>

<script lang="ts">
  export default { name: 'TimeOrSpatial' }
</script>

<script lang="ts" setup>
  import { RouterLink, RouterView} from 'vue-router';

</script>

<style scoped>
  .TimeOrSpatial {
    display: block;
    color: black;
    background-color: #ddd;
    box-shadow: 0 0 10px;
    border-radius: 10px;
    padding: 20px;
    
  }

  .visDisplay {
    display: block;
  }

</style>