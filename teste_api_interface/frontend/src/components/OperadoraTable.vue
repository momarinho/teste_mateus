<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  operadoras: Array,
  loading: Boolean,
  page: Number,
  totalPages: Number,
});

const emit = defineEmits(['page-change', 'view-details']);

const formatCnpj = (cnpj) => {
  return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
};

const goToPage = (p) => {
  if (p >= 1 && p <= props.totalPages) {
    emit('page-change', p);
  }
};
</script>

<template>
  <div>
    <div class="table-container card">
      <div v-if="loading" class="loading-overlay">
        <div class="loader"></div>
      </div>
      
      <table v-else>
        <thead>
          <tr>
            <th>Registro ANS</th>
            <th>CNPJ</th>
            <th>Razão Social</th>
            <th>Modalidade</th>
            <th>UF</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="operadoras.length === 0">
            <td colspan="6" class="text-center">Nenhuma operadora encontrada.</td>
          </tr>
          <tr v-for="op in operadoras" :key="op.registro_operadora">
            <td>{{ op.registro_operadora }}</td>
            <td>{{ formatCnpj(op.cnpj) }}</td>
            <td>
              <span class="font-medium">{{ op.razao_social }}</span>
            </td>
            <td>{{ op.modalidade }}</td>
            <td><span class="badge">{{ op.uf }}</span></td>
            <td>
              <button class="btn btn-sm" @click="$emit('view-details', op.cnpj)">
                Detalhes
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="totalPages > 1">
      <button 
        class="btn btn-secondary" 
        :disabled="page === 1"
        @click="goToPage(page - 1)"
      >
        Anterior
      </button>
      <span class="page-info">
        Página {{ page }} de {{ totalPages }}
      </span>
      <button 
        class="btn btn-secondary" 
        :disabled="page === totalPages"
        @click="goToPage(page + 1)"
      >
        Próxima
      </button>
    </div>
  </div>
</template>

<style scoped>
.loading-overlay {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}
.text-center {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-muted);
}
.page-info {
  display: flex;
  align-items: center;
  color: var(--color-text-muted);
}
.btn-sm {
    padding: 0.25rem 0.75rem;
    font-size: 0.875rem;
}
</style>
