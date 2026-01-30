<script setup>
import { computed } from 'vue';
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps({
  data: {
    type: Array,
    required: true,
  }
});

const chartData = computed(() => {
  const labels = props.data.map(d => d.uf);
  const values = props.data.map(d => d.total_despesas);

  // Generates random colors or a fixed palette
  const backgroundColors = [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', 
    '#ec4899', '#06b6d4', '#84cc16', '#6366f1', '#14b8a6'
  ];

  return {
    labels: labels,
    datasets: [
      {
        backgroundColor: labels.map((_, i) => backgroundColors[i % backgroundColors.length]),
        data: values,
        borderWidth: 0,
      }
    ]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right',
      labels: {
        color: '#94a3b8', // text-muted
        font: {
          family: 'Inter',
        }
      }
    },
    tooltip: {
      callbacks: {
        label: (context) => {
          let label = context.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed !== null) {
            label += new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(context.parsed);
          }
          return label;
        }
      }
    }
  }
};
</script>

<template>
  <div class="chart-container">
    <Doughnut :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}
</style>
