<template>
  <div class="mainbody">
    <el-container>
      <!-- Navigation header of this page -->
      <el-header>
        <el-menu mode="horizontal">
          <el-menu-item index="1">
            <router-link to="/bar"> Bar Chart </router-link>
          </el-menu-item>
          <el-menu-item index="2">
            <router-link to="/radar"> Radar Chart </router-link>
          </el-menu-item>
          <el-menu-item index="3">
            <router-link to="/scatter"> Scatter Plot </router-link>
          </el-menu-item>
        </el-menu>
      </el-header>
  
      <!-- Main body -->
      <el-main>
        <router-view />
      </el-main>

    </el-container>

  </div>
</template>

<script lang="js">
export default { name: "TimeDV" };
</script>

<script setup lang="js">
// @ts-ignore
import simpleD3 from '../components/d3-charts/simpleD3.vue'

</script>

<style scoped></style>
