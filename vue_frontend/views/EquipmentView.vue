<template>
  <div>
    <h1>Primary View</h1>
    <div class="uk-divider-icon"></div>
    <equipment-table/>
  </div>
</template>

<script>
import EquipmentTable from "../components/inspection-items/EquipmentTable.vue";
export default {
  name: "EquipmentView",
  components: {EquipmentTable}
}
</script>

<style scoped>

</style>