<template>
  <div class="mainbody">
    <el-container>
      <!-- header of the app -->
      <el-header>
        <h1> Welcome to our project for visualizing Spotify data. </h1>
      </el-header>
      
      <el-container>
        <!-- navigate into time or spatial data -->
        <el-aside width=15vw>
          <h5> Navigation </h5>
          <el-menu>
            <el-menu-item index=1>
              <RouterLink to="/TimeDV">Time Data</RouterLink>
            </el-menu-item>
            <el-menu-item index=2>
              <RouterLink to="/SpatialDV">Spatial Data</RouterLink>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- main body of the app (overview of our visualization) -->
        <el-main>
          <RouterView></RouterView>
        </el-main>

      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
  import { RouterLink, RouterView } from 'vue-router'
  // import TimeOrSpatial from './views/TimeOrSpatial.vue';
  import TimeDV from '@/views/TimeDV.vue'
  import SpatialDV from '@/views/SpatialDV.vue'
</script>
