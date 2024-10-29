<template>
  <div class='mainbody'>
    <el-container>
      <!-- header of the app -->
      <el-header class='appHeader'>
        <h1> Welcome to our project for visualizing Spotify data. </h1>
      </el-header>
      
      <el-container>
        <!-- navigate into time or spatial data -->
        <el-aside width=15vw class='navBar'>
          <h3 class="navHeading"> Navigation </h3>
          <el-menu 
            default-active='1'
            router=true
          >
            <el-menu-item index='TimeDV'>
              <el-icon><Clock /></el-icon>
              <span>Time Data</span>
            </el-menu-item>
            <el-menu-item index='SpatialDV'>
              <el-icon><Location /></el-icon>
              <span>Spatial Data</span>
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
  import { Clock, Location } from '@element-plus/icons-vue'
</script>

<style scoped>
  .appHeader {
    text-align: center;
    background-color: #42b983; 
    color: white;
  }

  .navBar {
    background-color: #f4f4f4; /* Light gray navbar */
    padding: 4px;
    border-right: 1px solid #e0e0e0; /* Light border */
    height: 100vh; /* Full viewport height */
  }

  .el-menu {
    /*background-color: transparent; /* Transparent menu background - can add this as well */
    border-right: none; /* Remove right border */
  }

  .el-menu-item {
    color: #333; /* Dark text color */
  }
  .el-icon{
    color: #333; /* Dark text color */
  }
  .el-menu-item:hover {
    background-color: #e0e0e0; /* Light gray on hover */
  }

  .mainContent {
    padding: 20px;
    background-color: #ffffff; /* White background for main content */
  }

  .navHeading {
    padding-bottom: 15px;
    padding-left: 5px; /* Center align text */
    margin-bottom: 10px; /* Optional: add space below the heading */
    border-bottom: 2px solid #333; /* Line under the heading */
  } 
</style>