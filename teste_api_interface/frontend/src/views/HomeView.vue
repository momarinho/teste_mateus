<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useOperadoraStore } from '../stores/operadoraStore';
import OperadoraTable from '../components/OperadoraTable.vue';
import ExpensesChart from '../components/ExpensesChart.vue';
import api from '../api/api';

const store = useOperadoraStore();
const router = useRouter();

const searchQuery = ref('');
const expensesByUF = ref([]);
const loadingChart = ref(false);

const handleSearch = () => {
    // Debounce handled by store? Or just simple trigger
    store.fetchOperadoras(1, searchQuery.value);
};

const handlePageChange = (page) => {
    store.fetchOperadoras(page, searchQuery.value);
};

const viewDetails = (cnpj) => {
    router.push({ name: 'operadora-details', params: { cnpj } });
};

const fetchChartData = async () => {
    loadingChart.value = true;
    try {
        const res = await api.get('/despesas/por-uf');
        expensesByUF.value = res.data;
    } catch (e) {
        console.error("Failed to fetch chart data", e);
    } finally {
        loadingChart.value = false;
    }
};

onMounted(() => {
    store.fetchOperadoras();
    fetchChartData();
});
</script>

<template>
  <main>
    <header class="header">
        <div>
            <h1>Operadoras ANS</h1>
            <p class="subtitle">Gerenciamento e Visualização de Dados</p>
        </div>
        
        <div class="search-box">
            <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="Buscar por Razão Social ou CNPJ..." 
                class="input"
                @keyup.enter="handleSearch"
            />
            <button @click="handleSearch" class="btn">Buscar</button>
        </div>
    </header>

    <div class="dashboard-grid">
        <section class="chart-section card">
            <h3>Distribuição de Despesas por UF</h3>
            <div v-if="loadingChart" class="flex-center">
                <div class="loader"></div>
            </div>
            <ExpensesChart v-else-if="expensesByUF.length > 0" :data="expensesByUF" />
            <div v-else class="text-muted">
                Sem dados de despesas disponíveis.
            </div>
        </section>

        <section class="table-section">
            <div class="section-header">
                <h3>Lista de Operadoras</h3>
                <span v-if="store.total" class="badge">{{ store.total }} Encontradas</span>
            </div>
            
            <OperadoraTable 
                :operadoras="store.operadoras" 
                :loading="store.loading"
                :page="store.page"
                :totalPages="store.totalPages"
                @page-change="handlePageChange"
                @view-details="viewDetails"
            />
        </section>
    </div>
  </main>
</template>

<style scoped>
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    flex-wrap: wrap;
    gap: 1rem;
}
.subtitle {
    color: var(--color-text-muted);
    margin: 0;
}
.search-box {
    display: flex;
    gap: 0.5rem;
    min-width: 300px;
}
.dashboard-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
}

@media (min-width: 1024px) {
    .dashboard-grid {
        grid-template-columns: 350px 1fr;
    }
}

.chart-section {
    height: fit-content;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.flex-center {
    display: flex;
    justify-content: center;
    padding: 2rem;
}

.text-muted {
    color: var(--color-text-muted);
    text-align: center;
    padding: 1rem;
}
</style>
