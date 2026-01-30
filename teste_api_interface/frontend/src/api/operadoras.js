import api from './api';

export const getOperadoras = (page = 1, limit = 10, search = '') => {
    return api.get('/operadoras/', {
        params: {
            page,
            limit,
            search,
        },
    });
};

export const getOperadoraByCnpj = (cnpj) => {
    return api.get(`/operadoras/${cnpj}`);
};
