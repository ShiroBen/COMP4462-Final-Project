<template>
  <header>
  <TimeOrSpatial></TimeOrSpatial>
  </header>
</template>

<script lang="ts">
  export default { name: 'App' }
</script>


<script setup lang="ts">
  import { RouterLink, RouterView } from 'vue-router'
  import TimeOrSpatial from './components/TimeOrSpatial.vue';
</script>

<style scoped>

</style>
