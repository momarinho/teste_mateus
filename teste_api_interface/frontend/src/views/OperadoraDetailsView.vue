<script setup>
import { onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useOperadoraStore } from '../stores/operadoraStore';
import api from '../api/api';
import { ref } from 'vue';

const route = useRoute();
const router = useRouter();
const store = useOperadoraStore();
const expensesHistory = ref([]);
const loadingHistory = ref(false);

const cnpj = route.params.cnpj;

const fetchExpenses = async () => {
    loadingHistory.value = true;
    try {
        const res = await api.get(`/despesas/operadora/${cnpj}`);
        expensesHistory.value = res.data;
    } catch (e) {
        console.error("Failed to load expenses history", e);
    } finally {
        loadingHistory.value = false;
    }
};

onMounted(async () => {
    await store.fetchOperadoraDetails(cnpj);
    fetchExpenses();
});

const formatMoney = (val) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
};

const goBack = () => router.push('/');
</script>

<template>
  <div class="details-page">
    <button @click="goBack" class="btn btn-secondary mb-4">&larr; Voltar</button>

    <div v-if="store.loading" class="loader-container">
        <div class="loader"></div>
    </div>

    <div v-else-if="store.currentOperadora" class="content">
        <header class="card profile-header">
            <div>
                <h2>{{ store.currentOperadora.razao_social }}</h2>
                <div class="meta">
                    <span class="badge">{{ store.currentOperadora.modalidade }}</span>
                    <span class="cnpj">{{ store.currentOperadora.cnpj }}</span>
                </div>
            </div>
            <div class="status">
               <!-- Placeholder for status if available -->
            </div>
        </header>

        <div class="grid-details">
            <section class="card info-card">
                <h3>Informações Cadastrais</h3>
                <div class="info-list">
                    <div class="info-item">
                        <label>Nome Fantasia</label>
                        <p>{{ store.currentOperadora.nome_fantasia || '-' }}</p>
                    </div>
                    <div class="info-item">
                        <label>Registro ANS</label>
                        <p>{{ store.currentOperadora.registro_operadora }}</p>
                    </div>
                    <div class="info-item">
                        <label>Representante</label>
                        <p>{{ store.currentOperadora.representante || '-' }}</p>
                    </div>
                    <div class="info-item">
                        <label>Endereço</label>
                        <p>
                            {{ store.currentOperadora.logradouro }}, {{ store.currentOperadora.numero }} 
                            {{ store.currentOperadora.complemento }} <br/>
                            {{ store.currentOperadora.bairro }} - {{ store.currentOperadora.cidade }}/{{ store.currentOperadora.uf }}
                        </p>
                    </div>
                </div>
            </section>

            <section class="card expenses-card">
                <h3>Histórico de Despesas</h3>
                
                <div v-if="loadingHistory" class="loader-container">
                    <div class="loader"></div>
                </div>
                
                <table v-else-if="expensesHistory.length > 0">
                    <thead>
                        <tr>
                            <th>Ano</th>
                            <th>Trimestre</th>
                            <th>Valor</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(item, index) in expensesHistory" :key="index">
                            <td>{{ item.ano }}</td>
                            <td>{{ item.trimestre }}º</td>
                            <td class="money">{{ formatMoney(item.valor_despesas) }}</td>
                        </tr>
                    </tbody>
                </table>
                
                <div v-else class="empty-state">
                    Sem registros de despesas.
                </div>
            </section>
        </div>
    </div>

    <div v-else class="error">
        {{ store.error || 'Operadora não encontrada.' }}
    </div>
  </div>
</template>

<style scoped>
.mb-4 { margin-bottom: 2rem; }
.loader-container { display: flex; justify-content: center; padding: 2rem; }
.profile-header {
    margin-bottom: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.meta {
    display: flex;
    gap: 1rem;
    margin-top: 0.5rem;
    color: var(--color-text-muted);
}
.grid-details {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
}
@media(min-width: 768px) {
    .grid-details {
        grid-template-columns: 1fr 1fr;
    }
}
.info-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
.info-item label {
    font-size: 0.875rem;
    color: var(--color-text-muted);
    font-weight: 500;
}
.info-item p {
    margin: 0.25rem 0 0 0;
}
.money {
    font-family: monospace;
    font-weight: 600;
}
.empty-state {
    padding: 1rem;
    color: var(--color-text-muted);
    text-align: center;
}
</style>
