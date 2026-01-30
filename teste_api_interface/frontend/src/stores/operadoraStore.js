import { defineStore } from 'pinia';
import { getOperadoras, getOperadoraByCnpj } from '../api/operadoras';

export const useOperadoraStore = defineStore('operadora', {
    state: () => ({
        operadoras: [],
        total: 0,
        page: 1,
        limit: 10,
        totalPages: 0,
        loading: false,
        error: null,
        currentOperadora: null,
    }),
    actions: {
        async fetchOperadoras(page = 1, search = '') {
            this.loading = true;
            this.error = null;
            try {
                const response = await getOperadoras(page, this.limit, search);
                const { data, total, total_pages } = response.data;
                this.operadoras = data;
                this.total = total;
                this.totalPages = total_pages;
                this.page = page;
            } catch (err) {
                this.error = 'Erro ao buscar operadoras. Tente novamente.';
                console.error(err);
            } finally {
                this.loading = false;
            }
        },
        async fetchOperadoraDetails(cnpj) {
            this.loading = true;
            this.error = null;
            this.currentOperadora = null;
            try {
                const response = await getOperadoraByCnpj(cnpj);
                this.currentOperadora = response.data;
            } catch (err) {
                this.error = 'Erro ao buscar detalhes da operadora.';
                console.error(err);
            } finally {
                this.loading = false;
            }
        }
    },
});
