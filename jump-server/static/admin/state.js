// 保存状态

const state = {
    page: 1,
    pageSize: 12,
    totalPages: 1,
    total: 0,
    domains: [],
    groups: [],

    batchSearchMode: false,
    batchSearchDomains: [],
};

const batchState = {
    checked: null,
};