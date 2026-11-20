<template>
  <div class="bc-card-grid"><slot /></div>
</template>

<style scoped>
.bc-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
  margin: 24px 0;
}
</style>
