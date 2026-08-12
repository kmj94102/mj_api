const API_BASE = 'https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app';
const ACCOUNT_API = `${API_BASE}/accountBook`;

const WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토'];

let baseDate = parseInt(localStorage.getItem('accountBookBaseDate') || '1', 10);
let referenceDate = new Date();
let cycleStartDate = null;
let cycleEndDate = null;
let cycleList = [];
let selectedDayDate = null; // Date currently open in the day dialog

// ---------------------------------------------------------------
// helpers
// ---------------------------------------------------------------
function pad2(n) {
    return String(n).padStart(2, '0');
}

function toDateInputValue(date) {
    return `${date.getFullYear()}-${pad2(date.getMonth() + 1)}-${pad2(date.getDate())}`;
}

function toIsoMidnight(date) {
    return `${toDateInputValue(date)}T00:00:00.000Z`;
}

function parseDotDate(str) {
    // "2026.08.01" -> Date
    const [y, m, d] = str.split('.').map(Number);
    return new Date(y, m - 1, d);
}

function parseServerDate(str) {
    // server returns ISO-ish datetime string, e.g. "2026-08-01T00:00:00"
    return new Date(str);
}

function dateKey(date) {
    return `${date.getFullYear()}-${pad2(date.getMonth() + 1)}-${pad2(date.getDate())}`;
}

function formatWon(amount) {
    const sign = amount < 0 ? '-' : '';
    return `${sign}${Math.abs(amount).toLocaleString('ko-KR')}원`;
}

function toDateConfig(date) {
    return { date: toIsoMidnight(date), baseDate: baseDate };
}

function postJson(path, body) {
    return fetch(`${ACCOUNT_API}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    }).then(res => {
        if (!res.ok) {
            throw new Error('요청 처리 중 오류가 발생했습니다.');
        }
        return res.json();
    });
}

function deleteRequest(path) {
    return fetch(`${ACCOUNT_API}${path}`, { method: 'DELETE' }).then(res => {
        if (!res.ok) {
            throw new Error('삭제 중 오류가 발생했습니다.');
        }
    });
}

// ---------------------------------------------------------------
// dialogs
// ---------------------------------------------------------------
function openDialog(id) {
    document.getElementById(id).style.display = 'block';
    document.getElementById('dimLayer').style.display = 'block';
}

function closeDialog(id) {
    document.getElementById(id).style.display = 'none';
    document.getElementById('dimLayer').style.display = 'none';
}

document.getElementById('dimLayer').addEventListener('click', () => {
    ['jumpDialog', 'settingsDialog', 'dayDialog', 'addDialog', 'addFixedDialog'].forEach(id => {
        document.getElementById(id).style.display = 'none';
    });
    document.getElementById('dimLayer').style.display = 'none';
});

// ---------------------------------------------------------------
// tabs
// ---------------------------------------------------------------
document.querySelectorAll('.tabBtn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tabBtn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tabPanel').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        const tab = btn.dataset.tab;
        document.getElementById(`${tab}Tab`).classList.add('active');

        if (tab === 'stats') {
            loadStats();
        } else if (tab === 'fixed') {
            loadFixed();
            loadFrequently();
        }
    });
});

// ---------------------------------------------------------------
// cycle navigation
// ---------------------------------------------------------------
document.getElementById('prevCycle').addEventListener('click', () => {
    if (!cycleStartDate) return;
    const d = new Date(cycleStartDate);
    d.setDate(d.getDate() - 1);
    referenceDate = d;
    loadCycle();
});

document.getElementById('nextCycle').addEventListener('click', () => {
    if (!cycleEndDate) return;
    const d = new Date(cycleEndDate);
    d.setDate(d.getDate() + 1);
    referenceDate = d;
    loadCycle();
});

document.getElementById('cycleLabel').addEventListener('click', () => {
    document.getElementById('jumpDate').value = toDateInputValue(referenceDate);
    openDialog('jumpDialog');
});

function applyJumpDate() {
    const val = document.getElementById('jumpDate').value;
    if (!val) return;
    referenceDate = new Date(`${val}T00:00:00`);
    closeDialog('jumpDialog');
    loadCycle();
}

// ---------------------------------------------------------------
// settings
// ---------------------------------------------------------------
document.getElementById('settingsBtn').addEventListener('click', () => {
    document.getElementById('baseDateInput').value = baseDate;
    openDialog('settingsDialog');
});

function applySettings() {
    const val = parseInt(document.getElementById('baseDateInput').value, 10);
    if (!val || val < 1 || val > 31) {
        alert('1 ~ 31 사이의 날짜를 입력해 주세요.');
        return;
    }
    baseDate = val;
    localStorage.setItem('accountBookBaseDate', String(baseDate));
    closeDialog('settingsDialog');
    loadCycle();
    if (document.getElementById('statsTab').classList.contains('active')) {
        loadStats();
    }
}

// ---------------------------------------------------------------
// calendar / cycle
// ---------------------------------------------------------------
async function loadCycle() {
    document.getElementById('cycleLabel').textContent = '불러오는 중...';
    try {
        const data = await postJson('/select/thisMonthDetail', toDateConfig(referenceDate));

        cycleStartDate = parseDotDate(data.startDate);
        cycleEndDate = parseDotDate(data.endDate);
        cycleList = data.list || [];

        document.getElementById('cycleLabel').textContent = `${data.startDate} ~ ${data.endDate}`;
        document.getElementById('sumIncome').textContent = formatWon(data.income || 0);
        document.getElementById('sumExpenditure').textContent = formatWon(data.expenditure || 0);
        document.getElementById('sumTotal').textContent = formatWon((data.income || 0) + (data.expenditure || 0));

        renderCalendar();
    } catch (err) {
        console.error(err);
        document.getElementById('cycleLabel').textContent = '불러오기 실패';
        alert(`${err}`);
    }
}

function renderCalendar() {
    const calendarEl = document.getElementById('calendar');
    calendarEl.innerHTML = '';

    if (!cycleStartDate || !cycleEndDate) return;

    // group transactions by day
    const byDay = {};
    cycleList.forEach(item => {
        const d = parseServerDate(item.date);
        const key = dateKey(d);
        if (!byDay[key]) byDay[key] = [];
        byDay[key].push(item);
    });

    const leadingBlanks = cycleStartDate.getDay();
    for (let i = 0; i < leadingBlanks; i++) {
        const blank = document.createElement('div');
        blank.className = 'day empty';
        calendarEl.appendChild(blank);
    }

    const cursor = new Date(cycleStartDate);
    while (cursor <= cycleEndDate) {
        const key = dateKey(cursor);
        const dayItems = byDay[key] || [];

        const cell = document.createElement('div');
        cell.className = 'day';

        const isFirstOfMonth = cursor.getDate() === 1;
        const label = isFirstOfMonth ? `${cursor.getMonth() + 1}/${cursor.getDate()}` : String(cursor.getDate());

        const numEl = document.createElement('div');
        numEl.className = 'dayNum';
        numEl.textContent = label;
        cell.appendChild(numEl);

        if (dayItems.length > 0) {
            cell.classList.add('hasData');
            let income = 0;
            let expense = 0;
            dayItems.forEach(item => {
                if (item.amount > 0) income += item.amount;
                else expense += item.amount;
            });
            if (income > 0) {
                const incomeEl = document.createElement('div');
                incomeEl.className = 'dayIncome';
                incomeEl.textContent = `+${income.toLocaleString('ko-KR')}`;
                cell.appendChild(incomeEl);
            }
            if (expense < 0) {
                const expenseEl = document.createElement('div');
                expenseEl.className = 'dayExpense';
                expenseEl.textContent = expense.toLocaleString('ko-KR');
                cell.appendChild(expenseEl);
            }

            const capturedDate = new Date(cursor);
            cell.addEventListener('click', () => openDayDialog(capturedDate, dayItems));
        }

        calendarEl.appendChild(cell);
        cursor.setDate(cursor.getDate() + 1);
    }
}

function openDayDialog(date, items) {
    selectedDayDate = date;
    const title = `${date.getFullYear()}.${pad2(date.getMonth() + 1)}.${pad2(date.getDate())} (${WEEKDAYS[date.getDay()]})`;
    document.getElementById('dayDialogTitle').textContent = title;

    const listEl = document.getElementById('dayDialogList');
    listEl.innerHTML = '';

    items.forEach(item => {
        const row = document.createElement('div');
        row.className = 'listRow';

        const info = document.createElement('div');
        info.className = 'listRowInfo';
        const t = document.createElement('div');
        t.className = 'listRowTitle';
        t.textContent = item.whereToUse;
        const m = document.createElement('div');
        m.className = 'listRowMeta';
        m.textContent = item.usageType;
        info.appendChild(t);
        info.appendChild(m);

        const amount = document.createElement('div');
        amount.className = `listRowAmount ${item.amount >= 0 ? 'income' : 'expense'}`;
        amount.textContent = formatWon(item.amount);

        row.appendChild(info);
        row.appendChild(amount);
        listEl.appendChild(row);
    });

    openDialog('dayDialog');
}

function openAddDialogFromDay() {
    closeDialog('dayDialog');
    openAddDialog(selectedDayDate);
}

// ---------------------------------------------------------------
// add account book item
// ---------------------------------------------------------------
let addType = 'expense';

document.querySelectorAll('#addTypeToggle .typeBtn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('#addTypeToggle .typeBtn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        addType = btn.dataset.type;
    });
});

function openAddDialog(presetDate, prefill) {
    const date = presetDate || selectedDayDate || new Date();
    document.getElementById('addDate').value = toDateInputValue(date);

    if (prefill) {
        document.getElementById('addAmount').value = Math.abs(prefill.amount);
        document.getElementById('addUsageType').value = prefill.usageType;
        document.getElementById('addWhereToUse').value = prefill.whereToUse;
        addType = prefill.amount < 0 ? 'expense' : 'income';
    } else {
        document.getElementById('addAmount').value = '';
        document.getElementById('addUsageType').value = '';
        document.getElementById('addWhereToUse').value = '';
        addType = 'expense';
    }
    document.getElementById('addFrequentlyCheck').checked = false;

    document.querySelectorAll('#addTypeToggle .typeBtn').forEach(b => {
        b.classList.toggle('active', b.dataset.type === addType);
    });

    openDialog('addDialog');
}

async function submitAccountBook() {
    const dateVal = document.getElementById('addDate').value;
    const amountVal = document.getElementById('addAmount').value;
    const usageType = document.getElementById('addUsageType').value.trim();
    const whereToUse = document.getElementById('addWhereToUse').value.trim();

    if (!dateVal || !amountVal || !usageType || !whereToUse) {
        alert('날짜, 금액, 분류, 내용을 모두 입력해 주세요.');
        return;
    }

    const dateObj = new Date(`${dateVal}T00:00:00`);
    let amount = Math.abs(parseInt(amountVal, 10));
    if (addType === 'expense') amount = -amount;

    const body = {
        id: 0,
        date: `${dateVal}T00:00:00.000Z`,
        dateOfWeek: WEEKDAYS[dateObj.getDay()],
        amount: amount,
        usageType: usageType,
        whereToUse: whereToUse,
        isAddFrequently: document.getElementById('addFrequentlyCheck').checked
    };

    try {
        await postJson('/insert', body);
        closeDialog('addDialog');
        referenceDate = dateObj;
        await loadCycle();
        if (document.getElementById('fixedTab').classList.contains('active')) {
            loadFrequently();
        }
    } catch (err) {
        console.error(err);
        alert(`${err}`);
    }
}

// ---------------------------------------------------------------
// stats tab
// ---------------------------------------------------------------
async function loadStats() {
    const config = toDateConfig(referenceDate);

    try {
        const lastMonth = await postJson('/select/lastMonthAnalysis', config);
        document.getElementById('lastMonthRange').textContent = `${lastMonth.start} ~ ${lastMonth.end}`;
        renderLastMonthChart(lastMonth.result || []);
    } catch (err) {
        console.error(err);
    }

    try {
        const yearSummary = await postJson('/select/thisYearSummary', config);
        renderYearChart(yearSummary || []);
    } catch (err) {
        console.error(err);
    }
}

function renderLastMonthChart(result) {
    const el = document.getElementById('lastMonthChart');
    el.innerHTML = '';

    if (result.length === 0) {
        el.innerHTML = '<div class="emptyState">지난달 내역이 없어요.</div>';
        return;
    }

    result.forEach(entry => {
        const isIncome = entry.amount >= 0;
        const row = document.createElement('div');
        row.className = 'barRow';

        const labelRow = document.createElement('div');
        labelRow.className = 'barLabelRow';
        labelRow.innerHTML = `<span>${entry.usageType}</span><span>${formatWon(entry.amount)} (${Math.abs(entry.percentage)}%)</span>`;

        const track = document.createElement('div');
        track.className = 'barTrack';
        const fill = document.createElement('div');
        fill.className = `barFill ${isIncome ? 'income' : 'expense'}`;
        fill.style.width = `${Math.min(Math.abs(entry.percentage), 100)}%`;
        track.appendChild(fill);

        row.appendChild(labelRow);
        row.appendChild(track);
        el.appendChild(row);
    });
}

function renderYearChart(monthData) {
    const el = document.getElementById('yearChart');
    el.innerHTML = '';

    const maxAbs = Math.max(1, ...monthData.map(m => Math.abs(m.info || 0)));

    monthData.forEach(m => {
        const col = document.createElement('div');
        col.className = 'yearBarCol';

        const bar = document.createElement('div');
        const isIncome = (m.info || 0) >= 0;
        bar.className = `yearBar ${isIncome ? 'income' : 'expense'}`;
        const heightPct = Math.max(2, (Math.abs(m.info || 0) / maxAbs) * 100);
        bar.style.height = `${heightPct}%`;
        bar.title = formatWon(m.info || 0);

        const label = document.createElement('div');
        label.className = 'monthLabel';
        label.textContent = `${m.month}월`;

        col.appendChild(bar);
        col.appendChild(label);
        el.appendChild(col);
    });
}

// ---------------------------------------------------------------
// fixed items
// ---------------------------------------------------------------
let fixedType = 'expense';

document.querySelectorAll('#fixedTypeToggle .typeBtn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('#fixedTypeToggle .typeBtn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        fixedType = btn.dataset.type;
    });
});

function openAddFixedDialog() {
    document.getElementById('fixedDay').value = '';
    document.getElementById('fixedAmount').value = '';
    document.getElementById('fixedUsageType').value = '';
    document.getElementById('fixedWhereToUse').value = '';
    fixedType = 'expense';
    document.querySelectorAll('#fixedTypeToggle .typeBtn').forEach(b => {
        b.classList.toggle('active', b.dataset.type === 'expense');
    });
    openDialog('addFixedDialog');
}

async function submitFixed() {
    const day = parseInt(document.getElementById('fixedDay').value, 10);
    const amountVal = document.getElementById('fixedAmount').value;
    const usageType = document.getElementById('fixedUsageType').value.trim();
    const whereToUse = document.getElementById('fixedWhereToUse').value.trim();

    if (!day || day < 1 || day > 31 || !amountVal || !usageType || !whereToUse) {
        alert('모든 항목을 입력해 주세요.');
        return;
    }

    const body = {
        id: 0,
        date: String(day),
        amount: Math.abs(parseInt(amountVal, 10)),
        usageType: usageType,
        whereToUse: whereToUse,
        isIncome: fixedType === 'income'
    };

    try {
        await postJson('/insert/fixed', body);
        closeDialog('addFixedDialog');
        loadFixed();
    } catch (err) {
        console.error(err);
        alert(`${err}`);
    }
}

async function loadFixed() {
    const el = document.getElementById('fixedList');
    el.innerHTML = '';

    try {
        const list = await postJson('/select/fixed', {});
        if (!list || list.length === 0) {
            el.innerHTML = '<div class="emptyState">등록된 고정 내역이 없어요.</div>';
            return;
        }

        list.sort((a, b) => Number(a.date) - Number(b.date));

        list.forEach(item => {
            const row = document.createElement('div');
            row.className = 'listRow';

            const info = document.createElement('div');
            info.className = 'listRowInfo';
            const t = document.createElement('div');
            t.className = 'listRowTitle';
            t.textContent = item.whereToUse;
            const m = document.createElement('div');
            m.className = 'listRowMeta';
            m.textContent = `매월 ${item.date}일 · ${item.usageType}`;
            info.appendChild(t);
            info.appendChild(m);

            const amount = document.createElement('div');
            amount.className = `listRowAmount ${item.isIncome ? 'income' : 'expense'}`;
            amount.textContent = formatWon(item.isIncome ? item.amount : -item.amount);

            const delBtn = document.createElement('button');
            delBtn.className = 'deleteBtn';
            delBtn.innerHTML = '<i class="fa-solid fa-xmark"></i>';
            delBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                deleteFixed(item.id);
            });

            row.appendChild(info);
            row.appendChild(amount);
            row.appendChild(delBtn);

            row.addEventListener('click', () => {
                closeDialog('dayDialog');
                openAddDialog(pickDateForFixedDay(item.date), {
                    amount: item.isIncome ? item.amount : -item.amount,
                    usageType: item.usageType,
                    whereToUse: item.whereToUse
                });
            });

            el.appendChild(row);
        });
    } catch (err) {
        console.error(err);
        el.innerHTML = '<div class="emptyState">불러오기에 실패했어요.</div>';
    }
}

function pickDateForFixedDay(day) {
    const base = referenceDate || new Date();
    const d = new Date(base.getFullYear(), base.getMonth(), Number(day));
    return d;
}

async function deleteFixed(id) {
    if (!confirm('이 고정 내역을 삭제할까요?')) return;
    try {
        await deleteRequest(`/delete/fixed?id_=${id}`);
        loadFixed();
    } catch (err) {
        console.error(err);
        alert(`${err}`);
    }
}

// ---------------------------------------------------------------
// frequently used items
// ---------------------------------------------------------------
async function loadFrequently() {
    const el = document.getElementById('frequentlyList');
    el.innerHTML = '';

    try {
        const list = await postJson('/select/frequently', {});
        if (!list || list.length === 0) {
            el.innerHTML = '<div class="emptyState">즐겨찾기한 내역이 없어요.</div>';
            return;
        }

        list.forEach(item => {
            const row = document.createElement('div');
            row.className = 'listRow';

            const info = document.createElement('div');
            info.className = 'listRowInfo';
            const t = document.createElement('div');
            t.className = 'listRowTitle';
            t.textContent = item.whereToUse;
            const m = document.createElement('div');
            m.className = 'listRowMeta';
            m.textContent = item.usageType;
            info.appendChild(t);
            info.appendChild(m);

            const amount = document.createElement('div');
            amount.className = `listRowAmount ${item.amount >= 0 ? 'income' : 'expense'}`;
            amount.textContent = formatWon(item.amount);

            const delBtn = document.createElement('button');
            delBtn.className = 'deleteBtn';
            delBtn.innerHTML = '<i class="fa-solid fa-xmark"></i>';
            delBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                deleteFrequently(item.id);
            });

            row.appendChild(info);
            row.appendChild(amount);
            row.appendChild(delBtn);

            row.addEventListener('click', () => {
                closeDialog('dayDialog');
                openAddDialog(null, { amount: item.amount, usageType: item.usageType, whereToUse: item.whereToUse });
            });

            el.appendChild(row);
        });
    } catch (err) {
        console.error(err);
        el.innerHTML = '<div class="emptyState">불러오기에 실패했어요.</div>';
    }
}

async function deleteFrequently(id) {
    if (!confirm('이 즐겨찾기를 삭제할까요?')) return;
    try {
        await deleteRequest(`/delete/frequently?id_=${id}`);
        loadFrequently();
    } catch (err) {
        console.error(err);
        alert(`${err}`);
    }
}

// ---------------------------------------------------------------
// init
// ---------------------------------------------------------------
loadCycle();
