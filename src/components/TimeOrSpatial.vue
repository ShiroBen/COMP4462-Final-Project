<template>
  <div id='TimeOrSpatial'>
  <h1>Hello, users!</h1>
  <RouterLink :to="{name:'TimeDV'}"> Time Series Data Visulization </RouterLink>
  <RouterLink :to="{name:'SpatialDV'}"> Spatial Data Visualization </RouterLink>
  </div>
</template>

<script lang="ts">
  export default { name: 'TimeOrSpatial' }
</script>

<script lang="ts" setup>
  import { RouterLink, RouterView} from 'vue-router';

</script>

<style scoped>
  #TimeOrSpatial {
    color: black;
    background-color: #ddd;
    box-shadow: 0 0 10px;
    border-radius: 10px;
    padding: 20px;
    
  }

</style>