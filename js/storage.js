// js/storage.js
const REPORT_ID_KEY = 'celma_report_id';

export function saveReportId(id) {
    sessionStorage.setItem(REPORT_ID_KEY, id);
}

export function getReportId() {
    return sessionStorage.getItem(REPORT_ID_KEY);
}

export function clearReportId() {
    sessionStorage.removeItem(REPORT_ID_KEY);
}

// Можно добавить сохранение любых других данных
export function saveData(key, value) {
    sessionStorage.setItem(key, JSON.stringify(value));
}

export function getData(key) {
    const data = sessionStorage.getItem(key);
    return data ? JSON.parse(data) : null;
}