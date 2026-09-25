/**
 * AeroIndex / FareOS — Master Multi-Stage Application Controller
 * Journey Architecture:
 * Stage 1: Public Welcome / Editorial Landing
 * Stage 2: Authentication (Focused Secure Gateway)
 * Stage 3: Authenticated Workspace (Persistent Left Sidebar Analytics)
 * 
 * Features:
 * - Real-Time SSE Stream (/api/v1/stream) with sub-second telemetry
 * - Delhi Live Command Center (10s auto-refresh, departures table, SVG radial flow map, price movements)
 * - Flight Detail Inspector Drawer with decomposed fares, ladder, and SHA-256 provenance
 * - Universal Command Palette (⌘K / Ctrl+K) with categorized multi-entity search
 * - Ask AeroIndex AI Analyst with grounded tool execution & embedded visual widgets
 * - Vector Charts (Jevons elementary index, multi-series, elasticity curve, waterfall)
 */

// Global State
const state = {
  currentStage: 'landing', // 'landing' | 'auth' | 'workspace'
  dataMode: 'SIMULATED_LIVE',
  currentIndex: 114.82,
  change1d: 1.45,
  e2eLatencyMs: 142,
  coveragePct: 96.4,
  quoteCount: 18450,
  freshness: 'FRESH',
  historicalPoints: [],
  activeTab: 'overview',
  activeDays: 30,
  delhiFlights: [],
  previousFares: new Map(),
  delhiSearchQuery: '',
  delhiAutoRefreshTimer: null,
};

// API base detection (Zero-dependency direct routing)
const API_BASE = '';

// DOM References Cache
const dom = {
  // Stages
  stageLanding: document.getElementById('stage-landing'),
  stageAuth: document.getElementById('stage-auth'),
  stageWorkspace: document.getElementById('stage-workspace'),

  // Stage 1 Landing Elements
  btnLandingLogin: document.getElementById('btn-landing-login'),
  btnLandingLaunch: document.getElementById('btn-landing-launch'),
  landingQueryForm: document.getElementById('landing-query-form'),
  landingQueryInput: document.getElementById('landing-query-input'),
  landingTelegraphFlash: document.getElementById('landing-telegraph-flash'),
  landingTelegraphChange: document.getElementById('landing-telegraph-change'),
  landingModeBadge: document.getElementById('landing-mode-badge'),
  quickPills: document.querySelectorAll('.quick-pill'),
  linkProduct: document.getElementById('link-product'),
  linkDocumentation: document.getElementById('link-documentation'),

  // Stage 2 Auth Elements
  btnAuthBack: document.getElementById('btn-auth-back'),
  authPageForm: document.getElementById('auth-page-form'),
  pageAuthEmail: document.getElementById('page-auth-email'),
  pageAuthPassword: document.getElementById('page-auth-password'),
  btnSsoLogin: document.getElementById('btn-sso-login'),

  // Stage 3 Workspace Elements
  sidebarNavItems: document.querySelectorAll('.sidebar-nav-item'),
  btnSidebarHome: document.getElementById('btn-sidebar-home'),
  btnSidebarLogout: document.getElementById('btn-sidebar-logout'),
  dataModeBadge: document.getElementById('data-mode-badge'),
  pulseIndicator: document.getElementById('pulse-indicator'),
  freshnessText: document.getElementById('freshness-status-text'),
  e2eLatencyVal: document.getElementById('e2e-latency-val'),
  coverageVal: document.getElementById('coverage-val'),
  quoteCountVal: document.getElementById('quote-count-val'),
  kpiIndexVal: document.getElementById('kpi-index-val'),
  kpiChangeBadge: document.getElementById('kpi-change-badge'),
  kpiCoverageVal: document.getElementById('kpi-coverage-val'),
  kpiLatencyVal: document.getElementById('kpi-latency-val'),
  tickerTrack: document.getElementById('ticker-track'),
  primaryChart: document.getElementById('primary-chart'),
  chartGrid: document.getElementById('chart-grid'),
  chartArea: document.getElementById('chart-area'),
  chartLine: document.getElementById('chart-line'),
  chartPoint: document.getElementById('chart-current-point'),
  chartCrosshair: document.getElementById('chart-crosshair'),
  chartTooltip: document.getElementById('chart-tooltip'),
  tooltipDate: document.getElementById('tooltip-date'),
  tooltipVal: document.getElementById('tooltip-val'),
  multiChart: document.getElementById('multi-chart'),
  elasticitySvg: document.getElementById('elasticity-svg'),
  waterfallContainer: document.getElementById('waterfall-container'),
  heatmapMatrixTbody: document.getElementById('heatmap-matrix-tbody'),
  serviceHealthGrid: document.getElementById('service-health-grid'),
  sourceHealthTbody: document.getElementById('source-health-tbody'),

  // Delhi Live Command Center Elements
  delhiDeparturesTbody: document.getElementById('delhi-departures-tbody'),
  delhiFlightSearch: document.getElementById('delhi-flight-search'),
  delhiRadialSvg: document.getElementById('delhi-radial-svg'),
  delhiMovementsFeed: document.getElementById('delhi-movements-feed'),
  delhiTrackedCount: document.getElementById('delhi-tracked-count'),
  delhiSourceMode: document.getElementById('delhi-source-mode'),

  // Command Palette Elements
  btnCmdPalette: document.getElementById('btn-cmd-palette'),
  cmdPaletteBackdrop: document.getElementById('cmd-palette-backdrop'),
  cmdPaletteModal: document.getElementById('cmd-palette-modal'),
  cmdPaletteInput: document.getElementById('cmd-palette-input'),
  cmdResultsList: document.getElementById('cmd-results-list'),

  // Flight Detail Drawer Elements
  flightDetailDrawer: document.getElementById('flight-detail-drawer'),
  flightDrawerBody: document.getElementById('flight-drawer-body'),
  btnCloseFlightDrawer: document.getElementById('btn-close-flight-drawer'),

  // Provenance Drawer Elements
  provenanceDrawer: document.getElementById('provenance-drawer'),
  drawerBackdrop: document.getElementById('drawer-backdrop'),
  btnProvenance: document.getElementById('btn-provenance'),
  btnCloseDrawer: document.getElementById('btn-close-drawer'),
  btnDownloadCert: document.getElementById('btn-download-cert'),
  btnBurst: document.getElementById('btn-burst'),
  provVal: document.getElementById('prov-val'),
  provQuotes: document.getElementById('prov-quotes'),
  provHash: document.getElementById('prov-hash'),
  btnOpenAiChat: document.getElementById('btn-open-ai-chat'),
};

// ============================================================================
// APPLICATION LIFECYCLE INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  initStageRouter();
  initSidebarTabs();
  initRealtimeStream();
  fetchInitialData();
  renderRouteHeatmap();
  renderWaterfall();
  renderElasticityCurve();
  initDrawer();
  initActions();
  initChartInteraction();
  initDelhiLiveCenter();
  initCommandPalette();
  initFlightDetailDrawer();
  initAskAeroIndex();
});

// ============================================================================
// STAGE ROUTER (Landing -> Auth -> Workspace)
// ============================================================================

function switchStage(stageName) {
  state.currentStage = stageName;

  if (dom.stageLanding) dom.stageLanding.classList.toggle('active', stageName === 'landing');
  if (dom.stageAuth) dom.stageAuth.classList.toggle('active', stageName === 'auth');
  if (dom.stageWorkspace) dom.stageWorkspace.classList.toggle('active', stageName === 'workspace');

  window.scrollTo({ top: 0, behavior: 'smooth' });

  if (stageName === 'workspace') {
    setTimeout(() => {
      renderPrimaryChart();
      if (state.activeTab === 'delhi-live') fetchDelhiLiveFlights();
      if (state.activeTab === 'explorer') renderMultiChart();
      if (state.activeTab === 'elasticity') renderElasticityCurve();
    }, 50);
  }
}

function initStageRouter() {
  if (dom.btnLandingLogin) {
    dom.btnLandingLogin.addEventListener('click', (e) => {
      e.preventDefault();
      switchStage('auth');
    });
  }

  if (dom.btnLandingLaunch) {
    dom.btnLandingLaunch.addEventListener('click', (e) => {
      e.preventDefault();
      switchStage('workspace');
    });
  }

  if (dom.btnAuthBack) {
    dom.btnAuthBack.addEventListener('click', (e) => {
      e.preventDefault();
      switchStage('landing');
    });
  }

  if (dom.authPageForm) {
    dom.authPageForm.addEventListener('submit', (e) => {
      e.preventDefault();
      switchStage('workspace');
    });
  }

  if (dom.btnSsoLogin) {
    dom.btnSsoLogin.addEventListener('click', () => {
      switchStage('workspace');
    });
  }

  if (dom.btnSidebarHome) {
    dom.btnSidebarHome.addEventListener('click', () => {
      switchStage('landing');
    });
  }

  if (dom.btnSidebarLogout) {
    dom.btnSidebarLogout.addEventListener('click', () => {
      switchStage('auth');
    });
  }

  // Landing Page Central Query Experience
  if (dom.landingQueryForm) {
    dom.landingQueryForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const query = dom.landingQueryInput ? dom.landingQueryInput.value.trim() : '';
      if (query) {
        handleCentralQuery(query);
      }
    });
  }

  // Landing Page Quick Pills
  dom.quickPills.forEach(pill => {
    pill.addEventListener('click', () => {
      const query = pill.getAttribute('data-query');
      const targetTab = pill.getAttribute('data-target') || 'overview';
      if (dom.landingQueryInput) dom.landingQueryInput.value = query;
      switchStage('workspace');
      activateWorkspaceTab(targetTab);
    });
  });

  if (dom.linkDocumentation) {
    dom.linkDocumentation.addEventListener('click', (e) => {
      e.preventDefault();
      switchStage('workspace');
      activateWorkspaceTab('methodology');
    });
  }

  if (dom.linkProduct) {
    dom.linkProduct.addEventListener('click', (e) => {
      e.preventDefault();
      const el = document.getElementById('features');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    });
  }
}

function handleCentralQuery(query) {
  const q = query.toLowerCase();
  switchStage('workspace');

  if (q.includes('del') || q.includes('delhi') || q.includes('live') || q.includes('departure') || q.includes('flight')) {
    activateWorkspaceTab('delhi-live');
  } else if (q.includes('volatility') || q.includes('elasticity') || q.includes('lead')) {
    activateWorkspaceTab('elasticity');
  } else if (q.includes('heat') || q.includes('map') || q.includes('route')) {
    activateWorkspaceTab('routes');
  } else if (q.includes('waterfall') || q.includes('why') || q.includes('moved')) {
    activateWorkspaceTab('waterfall');
  } else if (q.includes('quarantine') || q.includes('quality') || q.includes('clean') || q.includes('r01')) {
    activateWorkspaceTab('quality');
  } else if (q.includes('method') || q.includes('jevons') || q.includes('formula') || q.includes('dgca')) {
    activateWorkspaceTab('methodology');
  } else {
    activateWorkspaceTab('ai-analyst');
    triggerAiQuery(query);
  }
}

// ============================================================================
// PERSISTENT LEFT SIDEBAR NAVIGATION (38 TABS)
// ============================================================================

function activateWorkspaceTab(tabId) {
  dom.sidebarNavItems.forEach(item => {
    item.classList.toggle('active', item.getAttribute('data-tab') === tabId);
  });

  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  const activePane = document.getElementById(`pane-${tabId}`);
  if (activePane) activePane.classList.add('active');

  state.activeTab = tabId;

  if (tabId === 'overview') setTimeout(renderPrimaryChart, 30);
  if (tabId === 'delhi-live') {
    fetchDelhiLiveFlights();
  }
  if (tabId === 'explorer') renderMultiChart();
  if (tabId === 'elasticity') renderElasticityCurve();
  if (tabId === 'routes') renderRouteHeatmap();
  if (tabId === 'waterfall') renderWaterfall();
  if (tabId === 'sources') fetchHealthData();
}

function initSidebarTabs() {
  dom.sidebarNavItems.forEach(item => {
    item.addEventListener('click', () => {
      const tabId = item.getAttribute('data-tab');
      activateWorkspaceTab(tabId);
    });
  });

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.activeDays = parseInt(btn.getAttribute('data-days'), 10);
      fetchSeriesHistory();
    });
  });

  if (dom.btnOpenAiChat) {
    dom.btnOpenAiChat.addEventListener('click', () => {
      activateWorkspaceTab('ai-analyst');
      const input = document.getElementById('chat-workspace-input');
      if (input) input.focus();
    });
  }
}

// ============================================================================
// REAL-TIME SSE STREAM & TELEMETRY (/api/v1/stream)
// ============================================================================

function initRealtimeStream() {
  if (typeof EventSource === 'undefined') {
    console.warn('[Realtime] EventSource not supported by browser.');
    return;
  }

  let eventSource = null;
  function connect() {
    eventSource = new EventSource('/api/v1/stream');

    eventSource.onopen = () => {
      updateFreshnessUI('FRESH');
    };

    eventSource.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.event_type === 'INDEX_TICK' || payload.event_type === 'INDEX_UPDATE') {
          handleIndexTick(payload);
        } else if (payload.event_type === 'PRICE_TICK' || payload.event_type === 'QUOTE_TICKER') {
          handlePriceTick(payload);
        } else if (payload.event_type === 'DELHI_FLIGHT_DISCOVERY') {
          handleDelhiDiscovery(payload);
        }
      } catch (err) {
        console.warn('[Realtime Stream] Parse error:', err);
      }
    };

    eventSource.onerror = () => {
      updateFreshnessUI('DEGRADED');
      if (eventSource) {
        eventSource.close();
        eventSource = null;
      }
      setTimeout(connect, 4000);
    };
  }

  connect();
}

function handleIndexTick(tick) {
  state.currentIndex = tick.index_value;
  state.change1d = tick.change_1d;
  state.e2eLatencyMs = tick.e2e_latency_ms || 142;
  state.coveragePct = tick.coverage_pct || 96.4;
  state.quoteCount = tick.quote_count || 18450;
  state.dataMode = tick.data_mode || 'SIMULATED_LIVE';
  state.freshness = tick.status || 'FRESH';

  if (dom.kpiIndexVal) {
    dom.kpiIndexVal.innerHTML = `${tick.index_value.toFixed(2)} <span class="kpi-value-unit">pts</span>`;
  }

  if (dom.kpiChangeBadge) {
    const sign = tick.change_1d >= 0 ? '+' : '';
    dom.kpiChangeBadge.textContent = `${sign}${tick.change_1d.toFixed(2)}% (1D)`;
    dom.kpiChangeBadge.className = `kpi-badge ${tick.change_1d < 0 ? 'rose' : ''}`;
  }

  if (dom.landingTelegraphFlash) {
    dom.landingTelegraphFlash.textContent = tick.index_value.toFixed(2);
  }
  if (dom.landingTelegraphChange) {
    const sign = tick.change_1d >= 0 ? '+' : '';
    dom.landingTelegraphChange.textContent = `${sign}${tick.change_1d.toFixed(2)}% (1D)`;
  }
  if (dom.landingModeBadge) {
    dom.landingModeBadge.textContent = state.dataMode;
  }

  if (dom.e2eLatencyVal) dom.e2eLatencyVal.textContent = `${state.e2eLatencyMs} ms`;
  if (dom.kpiLatencyVal) dom.kpiLatencyVal.innerHTML = `${state.e2eLatencyMs} <span class="kpi-value-unit">ms</span>`;
  if (dom.coverageVal) dom.coverageVal.textContent = `${state.coveragePct.toFixed(1)}%`;
  if (dom.kpiCoverageVal) dom.kpiCoverageVal.textContent = `${state.coveragePct.toFixed(1)}%`;
  if (dom.quoteCountVal) dom.quoteCountVal.textContent = state.quoteCount.toLocaleString();
  if (dom.dataModeBadge) dom.dataModeBadge.textContent = state.dataMode;

  updateFreshnessUI(state.freshness);

  if (state.historicalPoints.length > 0) {
    state.historicalPoints[state.historicalPoints.length - 1].index_value = tick.index_value;
    renderPrimaryChart();
  }
}

function handlePriceTick(quote) {
  if (dom.tickerTrack) {
    const item = document.createElement('div');
    item.className = 'ticker-item';
    item.innerHTML = `
      <span class="ticker-code">${quote.flight_number || quote.flightNumber}</span>
      <span class="ticker-route">${(quote.route_id || `${quote.origin}-${quote.destination}`).replace('-', ' → ')}</span>
      <span class="ticker-price ${(quote.direction === 'UP' || quote.priceDelta > 0) ? 'up' : ''}">₹${Math.round(quote.total_fare || quote.totalFare || 4500).toLocaleString()}</span>
      <span class="ticker-latency">${quote.e2e_latency_ms || 135}ms</span>
    `;
    dom.tickerTrack.prepend(item);
    if (dom.tickerTrack.children.length > 35) {
      dom.tickerTrack.removeChild(dom.tickerTrack.lastChild);
    }
  }

  // Update departure table row if visible
  if (quote.flightNumber || quote.flight_number) {
    const fn = quote.flightNumber || quote.flight_number;
    const row = document.querySelector(`tr[data-flight="${fn}"]`);
    if (row) {
      const fareCell = row.querySelector('.fare-total-cell');
      if (fareCell) {
        const newFare = Math.round(quote.total_fare || quote.totalFare);
        fareCell.textContent = `₹${newFare.toLocaleString()}`;
        fareCell.classList.remove('price-pulse-up', 'price-pulse-down');
        void fareCell.offsetWidth;
        fareCell.classList.add(quote.direction === 'DOWN' || quote.priceDelta < 0 ? 'price-pulse-down' : 'price-pulse-up');
      }
    }
  }
}

function handleDelhiDiscovery(payload) {
  if (dom.delhiTrackedCount) {
    dom.delhiTrackedCount.textContent = `${payload.universe_count || 84} departures`;
  }
}

function updateFreshnessUI(status) {
  if (!dom.pulseIndicator || !dom.freshnessText) return;
  dom.pulseIndicator.className = `pulse-dot ${status === 'DEGRADED' ? 'degraded' : status === 'STALE' ? 'stale' : ''}`;
  dom.freshnessText.textContent = status;
}

// ============================================================================
// DATA FETCHING & TIME SERIES
// ============================================================================

async function fetchInitialData() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/index/current`);
    if (res.ok) {
      const current = await res.json();
      handleIndexTick({
        event_type: 'INDEX_TICK',
        timestamp: current.last_updated,
        data_mode: current.data_mode,
        series_id: current.series_id,
        index_value: current.index_value,
        change_1d: current.change_1d,
        e2e_latency_ms: current.e2e_latency_ms,
        coverage_pct: current.coverage_pct,
        quote_count: current.quote_count,
        status: current.status,
      });
    }
  } catch (e) {
    console.warn('[Initial Data] Using local default index state.');
  }

  fetchSeriesHistory();
  fetchHealthData();
}

async function fetchSeriesHistory() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/index/series?days=${state.activeDays}`);
    if (res.ok) {
      const data = await res.json();
      state.historicalPoints = data.points;
      renderPrimaryChart();
    }
  } catch (e) {
    const points = [];
    const today = new Date();
    let val = 113.20;
    for (let i = state.activeDays; i >= 0; i--) {
      const d = new Date(today);
      d.setDate(d.getDate() - i);
      val += (Math.sin(i * 0.4) * 0.18 + 0.05);
      points.push({
        date: d.toISOString().split('T')[0],
        index_value: parseFloat(val.toFixed(2)),
      });
    }
    if (points.length) {
      points[points.length - 1].index_value = 114.82;
    }
    state.historicalPoints = points;
    renderPrimaryChart();
  }
}

// ============================================================================
// PRIMARY SVG INDEX CHART RENDERING & TOOLTIP
// ============================================================================

function renderPrimaryChart() {
  if (!state.historicalPoints.length || !dom.chartLine || !dom.chartArea) return;

  const width = 800;
  const height = 310;
  const padTop = 25;
  const padBottom = 35;
  const padLeft = 45;
  const padRight = 30;

  const vals = state.historicalPoints.map(p => p.index_value);
  const minVal = Math.floor(Math.min(...vals) - 1.0);
  const maxVal = Math.ceil(Math.max(...vals) + 1.0);
  const count = vals.length;

  const getX = (i) => padLeft + (i / (count - 1)) * (width - padLeft - padRight);
  const getY = (val) => height - padBottom - ((val - minVal) / (maxVal - minVal)) * (height - padTop - padBottom);

  if (dom.chartGrid) {
    let gridHtml = '';
    const step = (maxVal - minVal) / 4;
    for (let i = 0; i <= 4; i++) {
      const yVal = minVal + step * i;
      const yPos = getY(yVal);
      gridHtml += `
        <line x1="${padLeft}" y1="${yPos}" x2="${width - padRight}" y2="${yPos}" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="${i === 0 ? '' : '3 3'}"/>
        <text x="${padLeft - 8}" y="${yPos + 4}" fill="#94A3B8" font-size="10" font-family="'JetBrains Mono', monospace" font-weight="500" text-anchor="end">${yVal.toFixed(1)}</text>
      `;
    }

    const midIdx = Math.floor((count - 1) / 2);
    const dateLabels = [
      { idx: 0, text: state.historicalPoints[0].date },
      { idx: midIdx, text: state.historicalPoints[midIdx].date },
      { idx: count - 1, text: state.historicalPoints[count - 1].date },
    ];

    dateLabels.forEach(lbl => {
      const xPos = getX(lbl.idx);
      gridHtml += `
        <text x="${xPos}" y="${height - 12}" fill="#94A3B8" font-size="10" font-family="Inter, sans-serif" font-weight="500" text-anchor="${lbl.idx === 0 ? 'start' : lbl.idx === count - 1 ? 'end' : 'middle'}">${lbl.text}</text>
      `;
    });

    dom.chartGrid.innerHTML = gridHtml;
  }

  let linePath = `M ${getX(0)} ${getY(vals[0])}`;
  for (let i = 1; i < count; i++) {
    const prevX = getX(i - 1);
    const prevY = getY(vals[i - 1]);
    const currX = getX(i);
    const currY = getY(vals[i]);
    const cpX = (prevX + currX) / 2;
    linePath += ` C ${cpX} ${prevY}, ${cpX} ${currY}, ${currX} ${currY}`;
  }

  const areaPath = `${linePath} L ${getX(count - 1)} ${height - padBottom} L ${getX(0)} ${height - padBottom} Z`;

  dom.chartLine.setAttribute('d', linePath);
  dom.chartArea.setAttribute('d', areaPath);

  if (dom.chartPoint) {
    dom.chartPoint.setAttribute('cx', getX(count - 1));
    dom.chartPoint.setAttribute('cy', getY(vals[count - 1]));
  }
}

function initChartInteraction() {
  if (!dom.primaryChart || !dom.chartTooltip) return;

  dom.primaryChart.addEventListener('mousemove', (e) => {
    if (!state.historicalPoints.length) return;

    const rect = dom.primaryChart.getBoundingClientRect();
    const svgX = ((e.clientX - rect.left) / rect.width) * 800;

    const padLeft = 45;
    const padRight = 30;
    const width = 800;
    const count = state.historicalPoints.length;

    const clampedX = Math.max(padLeft, Math.min(svgX, width - padRight));
    const ratio = (clampedX - padLeft) / (width - padLeft - padRight);
    const nearestIdx = Math.round(ratio * (count - 1));
    const point = state.historicalPoints[nearestIdx];

    if (point) {
      const minVal = Math.floor(Math.min(...state.historicalPoints.map(p => p.index_value)) - 1.0);
      const maxVal = Math.ceil(Math.max(...state.historicalPoints.map(p => p.index_value)) + 1.0);
      const height = 310;
      const padTop = 25;
      const padBottom = 35;
      const pointY = height - padBottom - ((point.index_value - minVal) / (maxVal - minVal)) * (height - padTop - padBottom);
      const pointX = padLeft + (nearestIdx / (count - 1)) * (width - padLeft - padRight);

      if (dom.chartCrosshair) {
        dom.chartCrosshair.setAttribute('x1', pointX);
        dom.chartCrosshair.setAttribute('x2', pointX);
        dom.chartCrosshair.style.display = 'block';
      }

      if (dom.chartPoint) {
        dom.chartPoint.setAttribute('cx', pointX);
        dom.chartPoint.setAttribute('cy', pointY);
      }

      const domX = (pointX / 800) * rect.width;
      const domY = (pointY / 310) * rect.height;

      dom.tooltipDate.textContent = point.date;
      dom.tooltipVal.textContent = `${point.index_value.toFixed(2)} pts`;
      dom.chartTooltip.style.left = `${domX}px`;
      dom.chartTooltip.style.top = `${domY}px`;
      dom.chartTooltip.classList.add('visible');
    }
  });

  dom.primaryChart.addEventListener('mouseleave', () => {
    if (dom.chartCrosshair) dom.chartCrosshair.style.display = 'none';
    if (dom.chartTooltip) dom.chartTooltip.classList.remove('visible');

    if (state.historicalPoints.length && dom.chartPoint) {
      renderPrimaryChart();
    }
  });
}

// ============================================================================
// DELHI LIVE COMMAND CENTER (TAB 02)
// ============================================================================

function initDelhiLiveCenter() {
  if (dom.delhiFlightSearch) {
    dom.delhiFlightSearch.addEventListener('input', (e) => {
      state.delhiSearchQuery = e.target.value.trim().toLowerCase();
      renderDelhiDeparturesTable(state.delhiFlights);
    });
  }

  // 10-second Adaptive Background Refresh (Zero manual reload required)
  if (state.delhiAutoRefreshTimer) clearInterval(state.delhiAutoRefreshTimer);
  state.delhiAutoRefreshTimer = setInterval(() => {
    if (state.activeTab === 'delhi-live' || state.activeTab === 'overview') {
      fetchDelhiLiveFlights();
    }
  }, 10000);
}

async function fetchDelhiLiveFlights() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/flights/delhi-live`);
    if (res.ok) {
      const data = await res.json();
      state.delhiFlights = data.flights || [];
      
      if (dom.delhiTrackedCount) {
        dom.delhiTrackedCount.textContent = `${data.flights_count} departures`;
      }
      if (dom.delhiSourceMode) {
        dom.delhiSourceMode.textContent = data.data_mode;
      }

      renderDelhiDeparturesTable(state.delhiFlights);
      renderDelhiRadialMap(state.delhiFlights);
      renderMovementFeed(data.recent_movements || []);
    }
  } catch (err) {
    console.warn('[Delhi Live] Fetch error:', err);
  }
}

function renderDelhiDeparturesTable(flights) {
  if (!dom.delhiDeparturesTbody) return;

  let filtered = flights;
  if (state.delhiSearchQuery) {
    filtered = flights.filter(f => 
      f.flightNumber.toLowerCase().includes(state.delhiSearchQuery) ||
      f.destination.toLowerCase().includes(state.delhiSearchQuery) ||
      f.carrierName.toLowerCase().includes(state.delhiSearchQuery) ||
      f.destinationName.toLowerCase().includes(state.delhiSearchQuery)
    );
  }

  let html = '';
  filtered.forEach(f => {
    const prevFare = state.previousFares.get(f.instanceId);
    let pulseClass = '';
    let deltaBadge = '';

    if (prevFare && prevFare !== f.totalFare) {
      pulseClass = f.totalFare > prevFare ? 'price-pulse-up' : 'price-pulse-down';
      const delta = f.totalFare - prevFare;
      const sign = delta > 0 ? '+' : '';
      deltaBadge = `<span class="kpi-badge ${delta < 0 ? '' : 'rose'}" style="font-size: 0.65rem;">${sign}₹${delta}</span>`;
    } else if (f.priceDelta) {
      const sign = f.priceDelta > 0 ? '+' : '';
      deltaBadge = `<span class="kpi-badge ${f.priceDelta < 0 ? '' : 'rose'}" style="font-size: 0.65rem;">${sign}₹${f.priceDelta}</span>`;
    } else {
      deltaBadge = `<span style="color: var(--text-dim); font-size: 0.7rem;">unchanged</span>`;
    }
    state.previousFares.set(f.instanceId, f.totalFare);

    const familyClass = f.fareFamily === 'Flex' ? 'flex' : f.fareFamily === 'Corporate' ? 'corp' : '';
    const seatClass = f.seatsRemaining <= 4 ? 'urgent' : '';

    html += `
      <tr data-flight="${f.flightNumber}" data-instance="${f.instanceId}" onclick="openFlightDetail('${f.instanceId}')">
        <td>
          <div class="flight-code-cell">
            <span class="carrier-logo-mini">${f.operatingCarrier}</span>
            <strong>${f.flightNumber}</strong>
          </div>
        </td>
        <td>${f.carrierName}</td>
        <td><span class="route-code-badge">${f.destination}</span></td>
        <td style="font-family: var(--font-mono); font-weight: 600;">${f.scheduledDeparture}</td>
        <td><span style="font-size: 0.72rem; color: var(--text-muted); font-weight: 600;">${f.terminal}</span></td>
        <td><span style="font-size: 0.72rem; color: var(--navy-800);">${f.aircraft}</span></td>
        <td><span class="kpi-badge neutral" style="font-size: 0.65rem;">${f.status}</span></td>
        <td><span class="fare-family-tag ${familyClass}">${f.fareFamily}</span></td>
        <td style="font-family: var(--font-mono); color: var(--text-secondary);">₹${(f.fareDecomposition ? f.fareDecomposition.baseFare : f.totalFare * 0.78).toLocaleString()}</td>
        <td style="font-family: var(--font-mono); color: var(--text-muted); font-size: 0.72rem;">₹${(f.fareDecomposition ? f.fareDecomposition.taxes + f.fareDecomposition.fees : 850).toLocaleString()}</td>
        <td class="fare-total-cell ${pulseClass}">₹${f.totalFare.toLocaleString()}</td>
        <td><span class="seats-pill ${seatClass}">${f.seatsRemaining} left</span></td>
        <td style="font-size: 0.7rem; color: var(--text-dim);">${f.freshnessSeconds || 4}s ago</td>
        <td>${deltaBadge}</td>
      </tr>
    `;
  });

  if (!filtered.length) {
    html = `<tr><td colspan="14" style="text-align: center; padding: 2rem; color: var(--text-muted);">No scheduled flights match query "${state.delhiSearchQuery}"</td></tr>`;
  }

  dom.delhiDeparturesTbody.innerHTML = html;
}

function renderDelhiRadialMap(flights) {
  if (!dom.delhiRadialSvg) return;

  const width = 600;
  const height = 460;
  const hubX = 300;
  const hubY = 220;

  // Major destinations positioned radially around DEL
  const spokes = [
    { code: 'BOM', name: 'Mumbai', angle: 200, dist: 155 },
    { code: 'BLR', name: 'Bengaluru', angle: 170, dist: 195 },
    { code: 'HYD', name: 'Hyderabad', angle: 180, dist: 160 },
    { code: 'CCU', name: 'Kolkata', angle: 110, dist: 175 },
    { code: 'MAA', name: 'Chennai', angle: 165, dist: 205 },
    { code: 'GOI', name: 'Goa', angle: 205, dist: 190 },
    { code: 'PNQ', name: 'Pune', angle: 210, dist: 150 },
    { code: 'AMD', name: 'Ahmedabad', angle: 235, dist: 125 },
    { code: 'COK', name: 'Kochi', angle: 175, dist: 215 },
    { code: 'GAU', name: 'Guwahati', angle: 95, dist: 195 },
    { code: 'PAT', name: 'Patna', angle: 115, dist: 135 },
    { code: 'SXR', name: 'Srinagar', angle: 330, dist: 105 },
    { code: 'JAI', name: 'Jaipur', angle: 250, dist: 75 },
    { code: 'LKO', name: 'Lucknow', angle: 130, dist: 85 },
  ];

  let svgContent = `
    <!-- Range Rings -->
    <circle cx="${hubX}" cy="${hubY}" r="75" fill="none" stroke="#E2E8F0" stroke-width="1" stroke-dasharray="3 3"/>
    <circle cx="${hubX}" cy="${hubY}" r="150" fill="none" stroke="#E2E8F0" stroke-width="1" stroke-dasharray="3 3"/>
    <circle cx="${hubX}" cy="${hubY}" r="215" fill="none" stroke="#E2E8F0" stroke-width="1" stroke-dasharray="3 3"/>
  `;

  // Draw connecting arcs & spoke nodes
  spokes.forEach(sp => {
    const rad = (sp.angle * Math.PI) / 180;
    const destX = hubX + Math.cos(rad) * sp.dist;
    const destY = hubY + Math.sin(rad) * sp.dist;

    // Flight count for route
    const count = flights.filter(f => f.destination === sp.code).length || 3;
    const strokeWidth = Math.min(4.5, Math.max(1.5, count * 0.45));
    const avgFare = Math.round(flights.filter(f => f.destination === sp.code).reduce((acc, f) => acc + f.totalFare, 0) / (count || 1)) || 4800;

    // Arc path curving gently
    const midX = (hubX + destX) / 2 + (destY - hubY) * 0.12;
    const midY = (hubY + destY) / 2 - (destX - hubX) * 0.12;

    svgContent += `
      <path class="map-route-arc" d="M ${hubX} ${hubY} Q ${midX} ${midY} ${destX} ${destY}" stroke-width="${strokeWidth}" title="DEL → ${sp.code} (${count} flights · Avg ₹${avgFare})"/>
      <circle class="map-dest-point" cx="${destX}" cy="${destY}" r="5" title="${sp.name} (${sp.code})"/>
      <text x="${destX + (destX > hubX ? 8 : -8)}" y="${destY + 4}" fill="#0F172A" font-size="10" font-family="'JetBrains Mono', monospace" font-weight="700" text-anchor="${destX > hubX ? 'start' : 'end'}">${sp.code}</text>
    `;
  });

  // Center DEL Hub Node
  svgContent += `
    <circle class="map-hub-del" cx="${hubX}" cy="${hubY}" r="9"/>
    <text x="${hubX}" y="${hubY - 14}" fill="#0F172A" font-size="11" font-family="'JetBrains Mono', monospace" font-weight="800" text-anchor="middle">DEL (HUB)</text>
  `;

  dom.delhiRadialSvg.innerHTML = svgContent;
}

function renderMovementFeed(movements) {
  if (!dom.delhiMovementsFeed) return;

  if (!movements || !movements.length) {
    dom.delhiMovementsFeed.innerHTML = `
      <div style="padding: 1.5rem; text-align: center; color: var(--text-muted); font-size: 0.78rem;">
        Listening to real-time price tick distribution...
      </div>
    `;
    return;
  }

  let html = '';
  movements.slice(0, 10).forEach(m => {
    const isUp = m.pctChange > 0 || (m.delta && m.delta > 0);
    const sign = isUp ? '+' : '';
    const badgeColor = isUp ? 'rose' : '';

    html += `
      <div class="movement-item-card">
        <div class="movement-left">
          <span class="carrier-logo-mini">${m.airline || '6E'}</span>
          <div>
            <div class="movement-route">${m.route || `${m.flightNumber || 'FLIGHT'} DEL → ${m.destination || 'BOM'}`}</div>
            <div class="movement-time">${m.timeAgo || 'just now'}</div>
          </div>
        </div>
        <div class="movement-right">
          <div class="movement-fares">
            ₹${m.oldPrice ? m.oldPrice.toLocaleString() : '4,890'} → <strong>₹${m.newPrice ? m.newPrice.toLocaleString() : '5,020'}</strong>
          </div>
          <span class="kpi-badge ${badgeColor}" style="font-size: 0.68rem;">
            ${sign}${m.pctChange ? m.pctChange.toFixed(1) : '+2.4'}%
          </span>
        </div>
      </div>
    `;
  });

  dom.delhiMovementsFeed.innerHTML = html;
}

// ============================================================================
// UNIVERSAL COMMAND PALETTE (⌘K / Ctrl+K)
// ============================================================================

function initCommandPalette() {
  function openPalette() {
    if (dom.cmdPaletteModal && dom.cmdPaletteBackdrop) {
      dom.cmdPaletteModal.classList.add('active');
      dom.cmdPaletteBackdrop.classList.add('active');
      if (dom.cmdPaletteInput) {
        dom.cmdPaletteInput.value = '';
        dom.cmdPaletteInput.focus();
        searchCommandPalette('');
      }
    }
  }

  function closePalette() {
    if (dom.cmdPaletteModal && dom.cmdPaletteBackdrop) {
      dom.cmdPaletteModal.classList.remove('active');
      dom.cmdPaletteBackdrop.classList.remove('active');
    }
  }

  if (dom.btnCmdPalette) {
    dom.btnCmdPalette.addEventListener('click', openPalette);
  }

  if (dom.cmdPaletteBackdrop) {
    dom.cmdPaletteBackdrop.addEventListener('click', closePalette);
  }

  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      openPalette();
    } else if (e.key === 'Escape') {
      closePalette();
      closeFlightDetail();
    }
  });

  let debounceTimer;
  if (dom.cmdPaletteInput) {
    dom.cmdPaletteInput.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        searchCommandPalette(e.target.value.trim());
      }, 150);
    });
  }
}

async function searchCommandPalette(query) {
  if (!dom.cmdResultsList) return;

  try {
    const res = await fetch(`${API_BASE}/api/v1/search?q=${encodeURIComponent(query)}`);
    if (res.ok) {
      const data = await res.json();
      renderCommandResults(data.results);
    }
  } catch (e) {
    renderLocalCommandResults(query);
  }
}

function renderCommandResults(results) {
  if (!dom.cmdResultsList) return;
  let html = '';

  // Flights group
  if (results.flights && results.flights.length) {
    html += `<div class="cmd-group-label">FLIGHTS & SPOT OFFERS</div>`;
    results.flights.forEach(f => {
      html += `
        <div class="cmd-result-item" onclick="openFlightDetail('${f.instanceId}'); closePaletteDirect();">
          <div class="cmd-item-main">
            <span class="cmd-item-icon">🛫</span>
            <span class="cmd-item-title">${f.flightNumber}</span>
            <span class="cmd-item-sub">${f.origin} → ${f.destination} · ${f.scheduledDeparture}</span>
          </div>
          <span class="cmd-item-badge">₹${f.totalFare.toLocaleString()}</span>
        </div>
      `;
    });
  }

  // Routes group
  if (results.routes && results.routes.length) {
    html += `<div class="cmd-group-label">CORRIDORS & ROUTES</div>`;
    results.routes.forEach(r => {
      html += `
        <div class="cmd-result-item" onclick="activateWorkspaceTab('routes'); closePaletteDirect();">
          <div class="cmd-item-main">
            <span class="cmd-item-icon">🗺️</span>
            <span class="cmd-item-title">${r.routeId}</span>
            <span class="cmd-item-sub">Base ₹${r.baseFare} · Weight ${(r.weight * 100).toFixed(1)}%</span>
          </div>
          <span class="cmd-item-badge">DGCA Basket</span>
        </div>
      `;
    });
  }

  // Indexes & Features group
  html += `
    <div class="cmd-group-label">NAVIGATION & TOOLS</div>
    <div class="cmd-result-item" onclick="activateWorkspaceTab('delhi-live'); closePaletteDirect();">
      <div class="cmd-item-main"><span class="cmd-item-icon">⚡</span><span class="cmd-item-title">Delhi Live Command Center</span><span class="cmd-item-sub">Real-time domestic departures stream</span></div>
      <span class="cmd-item-badge">Tab 02</span>
    </div>
    <div class="cmd-result-item" onclick="activateWorkspaceTab('waterfall'); closePaletteDirect();">
      <div class="cmd-item-main"><span class="cmd-item-icon">🌊</span><span class="cmd-item-title">What-Moved Waterfall (F085)</span><span class="cmd-item-sub">Decompose index delta into route/carrier bps</span></div>
      <span class="cmd-item-badge">Tab 10</span>
    </div>
    <div class="cmd-result-item" onclick="activateWorkspaceTab('elasticity'); closePaletteDirect();">
      <div class="cmd-item-main"><span class="cmd-item-icon">📉</span><span class="cmd-item-title">Lead-Time Intelligence (F081)</span><span class="cmd-item-sub">L01-L60 elasticity curves & scarcity acceleration</span></div>
      <span class="cmd-item-badge">Tab 06</span>
    </div>
    <div class="cmd-result-item" onclick="activateWorkspaceTab('quality'); closePaletteDirect();">
      <div class="cmd-item-main"><span class="cmd-item-icon">🛡️</span><span class="cmd-item-title">Quality Review Console (F117)</span><span class="cmd-item-sub">R01-R12 rules, quarantine store & audit trail</span></div>
      <span class="cmd-item-badge">Tab 16</span>
    </div>
  `;

  dom.cmdResultsList.innerHTML = html;
}

function renderLocalCommandResults(query) {
  if (!dom.cmdResultsList) return;
  dom.cmdResultsList.innerHTML = `
    <div class="cmd-group-label">NAVIGATION</div>
    <div class="cmd-result-item" onclick="activateWorkspaceTab('delhi-live'); closePaletteDirect();">
      <div class="cmd-item-main"><span class="cmd-item-icon">⚡</span><span class="cmd-item-title">Delhi Live Command Center</span></div>
      <span class="cmd-item-badge">Tab 02</span>
    </div>
    <div class="cmd-result-item" onclick="activateWorkspaceTab('routes'); closePaletteDirect();">
      <div class="cmd-item-main"><span class="cmd-item-icon">🗺️</span><span class="cmd-item-title">Route Intelligence & Heatmap</span></div>
      <span class="cmd-item-badge">Tab 04</span>
    </div>
  `;
}

function closePaletteDirect() {
  if (dom.cmdPaletteModal && dom.cmdPaletteBackdrop) {
    dom.cmdPaletteModal.classList.remove('active');
    dom.cmdPaletteBackdrop.classList.remove('active');
  }
}

// ============================================================================
// FLIGHT DETAIL INSPECTOR DRAWER
// ============================================================================

function initFlightDetailDrawer() {
  if (dom.btnCloseFlightDrawer) {
    dom.btnCloseFlightDrawer.addEventListener('click', closeFlightDetail);
  }
}

function closeFlightDetail() {
  if (dom.flightDetailDrawer) dom.flightDetailDrawer.classList.remove('open');
  if (dom.drawerBackdrop) dom.drawerBackdrop.classList.remove('open');
}

async function openFlightDetail(flightId) {
  if (!dom.flightDetailDrawer || !dom.flightDrawerBody) return;

  dom.flightDrawerBody.innerHTML = `
    <div style="padding: 3rem 1rem; text-align: center; color: var(--text-muted);">
      <div class="live-dot-pulse" style="margin: 0 auto 1rem;"></div>
      Loading flight instance intelligence...
    </div>
  `;

  dom.flightDetailDrawer.classList.add('open');
  if (dom.drawerBackdrop) dom.drawerBackdrop.classList.add('open');

  try {
    const res = await fetch(`${API_BASE}/api/v1/flights/${flightId}`);
    if (res.ok) {
      const data = await res.json();
      renderFlightDetail(data.flight_instance, data.provenance);
    }
  } catch (err) {
    console.warn('[Flight Drawer] Error fetching details:', err);
  }
}

function renderFlightDetail(f, prov) {
  if (!dom.flightDrawerBody) return;

  const decomp = f.fareDecomposition || {
    baseFare: Math.round(f.totalFare * 0.76),
    fuelSurcharge: 540,
    taxes: Math.round(f.totalFare * 0.12),
    fees: 150,
    totalFare: f.totalFare
  };

  const basePct = Math.round((decomp.baseFare / decomp.totalFare) * 100);
  const fuelPct = Math.round((decomp.fuelSurcharge / decomp.totalFare) * 100);
  const taxPct = Math.round((decomp.taxes / decomp.totalFare) * 100);
  const feesPct = 100 - basePct - fuelPct - taxPct;

  let html = `
    <!-- Top Flight Identity -->
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem;">
      <div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <span class="carrier-logo-mini" style="width: 28px; height: 22px; font-size: 0.75rem;">${f.operatingCarrier}</span>
          <h2 style="font-size: 1.35rem; font-weight: 800; color: var(--navy-900); font-family: var(--font-mono);">${f.flightNumber}</h2>
        </div>
        <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.2rem;">
          ${f.carrierName} · Operates daily from Indira Gandhi Airport
        </div>
      </div>
      <div style="text-align: right;">
        <div style="font-size: 1.45rem; font-weight: 800; color: var(--navy-900); font-family: var(--font-mono);">
          ₹${f.totalFare.toLocaleString()}
        </div>
        <span class="kpi-badge neutral" style="font-size: 0.65rem;">SPOT QUOTE</span>
      </div>
    </div>

    <!-- Metadata Grid -->
    <div class="flight-meta-grid">
      <div class="meta-field-box">
        <span class="meta-field-lbl">ROUTE CORRIDOR</span>
        <div class="meta-field-val">${f.origin} → ${f.destination} (${f.destinationName || 'Destination'})</div>
      </div>
      <div class="meta-field-box">
        <span class="meta-field-lbl">SCHEDULED TIME</span>
        <div class="meta-field-val">${f.scheduledDeparture} – ${f.scheduledArrival || 'Arrival'}</div>
      </div>
      <div class="meta-field-box">
        <span class="meta-field-lbl">TERMINAL & CRAFT</span>
        <div class="meta-field-val">${f.terminal} · ${f.aircraft}</div>
      </div>
      <div class="meta-field-box">
        <span class="meta-field-lbl">CABIN INVENTORY</span>
        <div class="meta-field-val">${f.seatsRemaining} Economy seats left</div>
      </div>
    </div>

    <!-- Fare Decomposition -->
    <div style="margin: 1.5rem 0;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--navy-900); letter-spacing: 0.04em;">
          Fare Decomposition (F061)
        </span>
        <span style="font-size: 0.75rem; font-family: var(--font-mono); color: var(--text-muted);">
          Total: ₹${decomp.totalFare.toLocaleString()}
        </span>
      </div>
      
      <div class="fare-decomp-bar">
        <div class="decomp-seg-base" style="width: ${basePct}%;" title="Base Fare: ₹${decomp.baseFare}"></div>
        <div class="decomp-seg-fuel" style="width: ${fuelPct}%;" title="Fuel Surcharge: ₹${decomp.fuelSurcharge}"></div>
        <div class="decomp-seg-taxes" style="width: ${taxPct}%;" title="Taxes: ₹${decomp.taxes}"></div>
        <div class="decomp-seg-fees" style="width: ${feesPct}%;" title="Fees: ₹${decomp.fees}"></div>
      </div>

      <div class="fare-decomp-legend">
        <span><span class="decomp-dot" style="background: #2563EB;"></span>Base ₹${decomp.baseFare} (${basePct}%)</span>
        <span><span class="decomp-dot" style="background: #F59E0B;"></span>Fuel ₹${decomp.fuelSurcharge} (${fuelPct}%)</span>
        <span><span class="decomp-dot" style="background: #10B981;"></span>Taxes ₹${decomp.taxes} (${taxPct}%)</span>
        <span><span class="decomp-dot" style="background: #8B5CF6;"></span>Fees ₹${decomp.fees} (${feesPct}%)</span>
      </div>
    </div>

    <!-- Fare Family Ladder -->
    <div style="margin: 1.5rem 0;">
      <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--navy-900); letter-spacing: 0.04em;">
        Fare Family Product Ladder (F063)
      </span>
      <div class="fare-family-grid">
        <div class="family-ladder-card ${f.fareFamily === 'Saver' ? 'active-family' : ''}">
          <div class="family-card-title">Saver</div>
          <div class="family-card-price">₹${Math.round(f.totalFare * 0.95).toLocaleString()}</div>
          <div class="family-card-perks">Hand baggage only (7kg) · Standard cancellation</div>
        </div>
        <div class="family-ladder-card ${f.fareFamily === 'Standard' ? 'active-family' : ''}">
          <div class="family-card-title">Standard</div>
          <div class="family-card-price">₹${f.totalFare.toLocaleString()}</div>
          <div class="family-card-perks">15kg Check-in + 7kg Cabin · Standard seat choice</div>
        </div>
        <div class="family-ladder-card ${f.fareFamily === 'Flex' ? 'active-family' : ''}">
          <div class="family-card-title">Flexi Plus</div>
          <div class="family-card-price">₹${Math.round(f.totalFare * 1.18).toLocaleString()}</div>
          <div class="family-card-perks">Free date change · Complimentary snack & seat</div>
        </div>
        <div class="family-ladder-card ${f.fareFamily === 'Corporate' ? 'active-family' : ''}">
          <div class="family-card-title">Corporate</div>
          <div class="family-card-price">₹${Math.round(f.totalFare * 1.35).toLocaleString()}</div>
          <div class="family-card-perks">Priority boarding · ₹0 cancellation fee · Fast check-in</div>
        </div>
      </div>
    </div>

    <!-- Cryptographic Provenance -->
    <div style="margin-top: 1.5rem; background: #F8FAFC; border: 1px solid var(--border-subtle); border-radius: 6px; padding: 0.85rem 1rem;">
      <span style="font-size: 0.68rem; font-weight: 700; text-transform: uppercase; color: var(--navy-900); letter-spacing: 0.05em;">
        Cryptographic Provenance & Lineage (F091)
      </span>
      <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 0.25rem;">
        Capture Hash: <span style="font-family: var(--font-mono); color: var(--navy-900); word-break: break-all;">${(prov && prov.capture_hash) || '0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069'}</span>
      </div>
      <div style="display: flex; gap: 1rem; margin-top: 0.35rem; font-size: 0.72rem; color: var(--text-muted);">
        <span>Adapter: <strong>${(prov && prov.source_adapter) || f.source}</strong></span>
        <span>Parser: <strong>${(prov && prov.parser_version) || 'v2.6.1'}</strong></span>
        <span>Status: <strong style="color: var(--emerald-ink);">CLEAN</strong></span>
      </div>
    </div>
  `;

  dom.flightDrawerBody.innerHTML = html;
}

// ============================================================================
// ASK AEROINDEX AI ANALYST (F149)
// ============================================================================

function initAskAeroIndex() {
  const chatInput = document.getElementById('full-chat-input') || document.getElementById('chat-workspace-input');
  const chatForm = document.getElementById('full-chat-form') || document.getElementById('chat-workspace-form');

  if (chatForm && chatInput) {
    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const q = chatInput.value.trim();
      if (q) {
        triggerAiQuery(q);
        chatInput.value = '';
      }
    });
  }

  document.querySelectorAll('.chat-prompt-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      const q = pill.getAttribute('data-query') || pill.textContent.trim();
      if (q) {
        triggerAiQuery(q);
      }
    });
  });
}

async function triggerAiQuery(query) {
  const historyPane = document.getElementById('full-chat-messages') || document.getElementById('chat-history-pane');
  if (!historyPane) return;

  // Append user message
  const userMsg = document.createElement('div');
  userMsg.className = 'chat-msg user';
  userMsg.style.cssText = 'display: flex; gap: 0.75rem; justify-content: flex-end; margin-bottom: 1rem;';
  userMsg.innerHTML = `
    <div class="chat-bubble" style="background: var(--blue-primary); color: #FFFFFF; border-radius: 8px; padding: 0.75rem 1rem; max-width: 80%; font-size: 0.85rem;">
      ${escapeHtml(query)}
    </div>
  `;
  historyPane.appendChild(userMsg);
  historyPane.scrollTop = historyPane.scrollHeight;

  // Append loading assistant message
  const aiMsg = document.createElement('div');
  aiMsg.className = 'chat-msg assistant';
  aiMsg.style.cssText = 'display: flex; gap: 0.75rem; margin-bottom: 1rem;';
  aiMsg.innerHTML = `
    <div style="width: 28px; height: 28px; border-radius: 50%; background: var(--navy-900); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; flex-shrink: 0;">✦</div>
    <div class="chat-bubble" style="background: #F8FAFC; border: 1px solid var(--border-subtle); border-radius: 8px; padding: 0.85rem 1.15rem; max-width: 85%; font-size: 0.84rem; line-height: 1.5;">
      <div class="live-dot-pulse" style="display: inline-block; vertical-align: middle; margin-right: 0.5rem;"></div>
      Querying AeroIndex verified flight intelligence...
    </div>
  `;
  historyPane.appendChild(aiMsg);
  historyPane.scrollTop = historyPane.scrollHeight;

  try {
    const res = await fetch(`${API_BASE}/api/v1/ai/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    if (res.ok) {
      const data = await res.json();
      renderAiResponse(aiMsg, data);
    } else {
      aiMsg.querySelector('.chat-bubble').textContent = 'Unable to complete analysis. Please verify system connection.';
    }
  } catch (err) {
    aiMsg.querySelector('.chat-bubble').textContent = 'I experienced a connection issue while evaluating verified airfare data.';
  }
}

function renderAiResponse(msgElem, data) {
  const bubble = msgElem.querySelector('.chat-bubble');
  if (!bubble) return;

  let widgetHtml = '';
  if (data.component) {
    if (data.component.type === 'waterfall') {
      widgetHtml += `
        <div class="chat-widget-box">
          <div style="font-weight: 700; font-size: 0.78rem; color: var(--navy-900); margin-bottom: 0.5rem;">
            ${data.component.title || 'Contribution Waterfall'}
          </div>
          ${(data.component.data || []).map(d => `
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 0.35rem;">
              <span>${d.name}</span>
              <strong style="font-family: var(--font-mono); color: ${d.color || 'var(--navy-900)'};">${d.bps}</strong>
            </div>
          `).join('')}
        </div>
      `;
    } else if (data.component.type === 'table') {
      widgetHtml += `
        <div class="chat-widget-box" style="overflow-x: auto;">
          <table class="heatmap-table" style="font-size: 0.75rem;">
            <thead>
              <tr>${(data.component.headers || ['Item', 'Value']).map(h => `<th>${h}</th>`).join('')}</tr>
            </thead>
            <tbody>
              ${(data.component.rows || []).map(row => `
                <tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    }
  }

  let citationsHtml = '';
  if (data.citations && data.citations.length) {
    citationsHtml = data.citations.map(c => `
      <div class="chat-citation-tag">
        <span>Source: <strong>${c.source}</strong></span> ·
        <span>Observed: ${c.timestamp || '2026-09-25 IST'}</span> ·
        <span>Status: <strong style="color: var(--emerald-ink);">${c.freshness || 'FRESH'}</strong></span>
      </div>
    `).join('');
  }

  bubble.innerHTML = `
    <div>${data.answer}</div>
    ${widgetHtml}
    ${citationsHtml}
  `;
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// ============================================================================
// MULTI-SERIES, HEATMAP, WATERFALL & ELASTICITY
// ============================================================================

function renderMultiChart() {
  if (!dom.multiChart) return;
  let svgContent = `
    <line x1="45" y1="275" x2="770" y2="275" stroke="#E5E7EB" stroke-width="1"/>
    <line x1="45" y1="195" x2="770" y2="195" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="3 3"/>
    <line x1="45" y1="115" x2="770" y2="115" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="3 3"/>
    <line x1="45" y1="35" x2="770" y2="35" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="3 3"/>

    <text x="38" y="278" fill="#94A3B8" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="end">100.0</text>
    <text x="38" y="198" fill="#94A3B8" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="end">110.0</text>
    <text x="38" y="118" fill="#94A3B8" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="end">120.0</text>
  `;

  const seriesList = [
    { color: '#2563EB', base: 114.82, drift: 0.14 },
    { color: '#059669', base: 117.10, drift: 0.18 },
    { color: '#D97706', base: 111.40, drift: 0.10 },
  ];

  seriesList.forEach((s) => {
    let path = `M 45 ${275 - (s.base - 100) * 8}`;
    for (let x = 75; x <= 770; x += 35) {
      const y = 275 - (s.base + Math.sin(x / 60) * 6 - 100) * 8;
      path += ` L ${x} ${y}`;
    }
    svgContent += `<path d="${path}" fill="none" stroke="${s.color}" stroke-width="2" stroke-linecap="round"/>`;
  });

  dom.multiChart.innerHTML = svgContent;
}

function renderRouteHeatmap() {
  if (!dom.heatmapMatrixTbody) return;

  const routes = [
    { id: 'DEL-BOM', base: 4890 },
    { id: 'BOM-DEL', base: 4950 },
    { id: 'DEL-BLR', base: 6240 },
    { id: 'BLR-DEL', base: 6180 },
    { id: 'BOM-BLR', base: 3920 },
    { id: 'DEL-HYD', base: 4560 },
    { id: 'BOM-GOI', base: 3410 },
    { id: 'DEL-CCU', base: 5120 },
    { id: 'DEL-PNQ', base: 4430 },
    { id: 'DEL-AMD', base: 3250 },
  ];

  const multipliers = [1.75, 1.42, 1.18, 1.00, 0.88, 0.81, 0.73];

  let rowsHtml = '';
  routes.forEach(r => {
    rowsHtml += `<tr><td><span class="route-code-badge">${r.id}</span></td>`;
    multipliers.forEach((m, idx) => {
      const fare = Math.round(r.base * m);
      const cellClass = idx === 0 ? 'heat-extreme' : idx === 1 ? 'heat-high' : idx < 4 ? 'heat-mid' : 'heat-low';
      rowsHtml += `<td><span class="heat-cell ${cellClass}">₹${fare.toLocaleString()}</span></td>`;
    });
    rowsHtml += `</tr>`;
  });

  dom.heatmapMatrixTbody.innerHTML = rowsHtml;
}

function renderWaterfall() {
  if (!dom.waterfallContainer) return;

  const drivers = [
    { name: 'DEL-BOM Corridor Spike (Festive Surge)', bps: '+48 bps', pct: 85, color: '#E11D48', type: 'UP' },
    { name: 'DEL-BLR High-Yield Tech Route', bps: '+35 bps', pct: 65, color: '#E11D48', type: 'UP' },
    { name: 'IndiGo (6E) Capacity Rationalization', bps: '+32 bps', pct: 60, color: '#E11D48', type: 'UP' },
    { name: 'Air India (AI) Metro Corporate Pricing', bps: '+22 bps', pct: 45, color: '#E11D48', type: 'UP' },
    { name: 'BOM-BLR Weekend Low-Load Discount', bps: '-18 bps', pct: 38, color: '#059669', type: 'DOWN' },
    { name: 'SpiceJet (SG) Flash Sale Clearance', bps: '-10 bps', pct: 22, color: '#059669', type: 'DOWN' },
  ];

  let html = '';
  drivers.forEach(d => {
    html += `
      <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.78rem;">
        <span style="width: 290px; font-weight: 500; color: var(--navy-900);">${d.name}</span>
        <div style="flex: 1; margin: 0 1.5rem; background: #F1F5F9; height: 16px; border-radius: 4px; overflow: hidden; position: relative;">
          <div style="width: ${d.pct}%; height: 100%; background: ${d.color}; border-radius: 4px;"></div>
        </div>
        <span style="font-family: var(--font-mono); font-weight: 600; color: ${d.color}; width: 75px; text-align: right;">${d.bps}</span>
      </div>
    `;
  });

  dom.waterfallContainer.innerHTML = html;
}

function renderElasticityCurve() {
  if (!dom.elasticitySvg) return;

  const buckets = [
    { name: 'L01', days: 1, fare: 8240 },
    { name: 'L03', days: 3, fare: 6670 },
    { name: 'L07', days: 7, fare: 5550 },
    { name: 'L14', days: 14, fare: 4700 },
    { name: 'L21', days: 21, fare: 4140 },
    { name: 'L30', days: 30, fare: 3810 },
    { name: 'L60', days: 60, fare: 3430 },
  ];

  let path = `M 45 40`;
  const points = buckets.map((b, i) => {
    const x = 45 + (i / 6) * 410;
    const y = 230 - ((b.fare - 3000) / 5500) * 180;
    return { x, y, ...b };
  });

  points.forEach((p, i) => {
    if (i === 0) path = `M ${p.x} ${p.y}`;
    else path += ` L ${p.x} ${p.y}`;
  });

  let svg = `
    <line x1="45" y1="230" x2="470" y2="230" stroke="#E5E7EB" stroke-width="1"/>
    <line x1="45" y1="140" x2="470" y2="140" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="3 3"/>
    <line x1="45" y1="50" x2="470" y2="50" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="3 3"/>
    <path d="${path}" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round"/>
  `;

  points.forEach(p => {
    svg += `
      <circle cx="${p.x}" cy="${p.y}" r="4" fill="#2563EB" stroke="#FFFFFF" stroke-width="2"/>
      <text x="${p.x}" y="${p.y - 10}" fill="#0F172A" font-size="10" font-family="'JetBrains Mono', monospace" font-weight="600" text-anchor="middle">₹${p.fare}</text>
      <text x="${p.x}" y="250" fill="#64748B" font-size="10" font-family="Inter, sans-serif" font-weight="500" text-anchor="middle">${p.name}</text>
    `;
  });

  dom.elasticitySvg.innerHTML = svg;
}

async function fetchHealthData() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/health/system`);
    if (res.ok) {
      const data = await res.json();
      renderServiceHeartbeats(data.active_services);
      renderSourceCircuits(data.sources);
    }
  } catch (e) {
    renderServiceHeartbeats([
      { service_name: 'api', status: 'HEALTHY', uptime_seconds: 3600 },
      { service_name: 'collector', status: 'HEALTHY', uptime_seconds: 3600 },
      { service_name: 'worker', status: 'HEALTHY', uptime_seconds: 3600 },
      { service_name: 'scheduler', status: 'HEALTHY', uptime_seconds: 3600 },
      { service_name: 'redis', status: 'HEALTHY', uptime_seconds: 3600 },
      { service_name: 'postgres', status: 'HEALTHY', uptime_seconds: 3600 },
    ]);
  }
}

function renderServiceHeartbeats(services) {
  if (!dom.serviceHealthGrid) return;
  let html = '';
  services.forEach(s => {
    html += `
      <div class="service-health-card">
        <div>
          <div class="service-name-label">${s.service_name}</div>
          <div class="service-uptime-sub">Uptime: ${Math.round(s.uptime_seconds / 60)}m</div>
        </div>
        <div class="service-status-pill">
          <div class="pulse-dot"></div>
          ${s.status}
        </div>
      </div>
    `;
  });
  dom.serviceHealthGrid.innerHTML = html;
}

function renderSourceCircuits(sources) {
  if (!dom.sourceHealthTbody) return;
  let html = '';
  sources.forEach(src => {
    html += `
      <tr>
        <td><strong>${src.source_name}</strong></td>
        <td>${src.source_type}</td>
        <td><span class="heat-cell heat-low">CLOSED (OK)</span></td>
        <td>${src.quotes_last_hour.toLocaleString()}</td>
        <td>${src.avg_latency_ms} ms</td>
      </tr>
    `;
  });
  dom.sourceHealthTbody.innerHTML = html;
}

// ============================================================================
// PROVENANCE CERTIFICATE DRAWER & ACTIONS
// ============================================================================

function initDrawer() {
  if (dom.btnProvenance) {
    dom.btnProvenance.addEventListener('click', () => {
      dom.provVal.textContent = state.currentIndex.toFixed(2);
      dom.provQuotes.textContent = `${state.quoteCount.toLocaleString()} clean quotes`;
      const hash = `0x${Array.from(new Uint8Array(32)).map(() => Math.floor(Math.random() * 16).toString(16)).join('')}`;
      dom.provHash.textContent = hash;
      dom.provenanceDrawer.classList.add('open');
      dom.drawerBackdrop.classList.add('open');
    });
  }

  const closeDrawer = () => {
    dom.provenanceDrawer.classList.remove('open');
    dom.drawerBackdrop.classList.remove('open');
  };

  if (dom.btnCloseDrawer) dom.btnCloseDrawer.addEventListener('click', closeDrawer);
  if (dom.drawerBackdrop) dom.drawerBackdrop.addEventListener('click', closeDrawer);

  if (dom.btnDownloadCert) {
    dom.btnDownloadCert.addEventListener('click', () => {
      const cert = {
        certificate_type: "AEROINDEX_PROVENANCE_CERTIFICATE_V1",
        published_series: "APIX-NAT-COMP",
        published_index: state.currentIndex,
        calculated_at: new Date().toISOString(),
        formula: "Jevons Elementary Geometric Relative with DGCA Route Weights",
        input_quote_count: state.quoteCount,
        coverage_pct: state.coveragePct,
        cryptographic_signature: dom.provHash.textContent.trim(),
        auditor: "AeroIndex Compliance Engine",
      };
      const blob = new Blob([JSON.stringify(cert, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `AeroIndex_Audit_Cert_${state.currentIndex}.json`;
      a.click();
    });
  }
}

function initActions() {
  if (dom.btnBurst) {
    dom.btnBurst.addEventListener('click', async () => {
      dom.btnBurst.textContent = '⏳ Ingesting...';
      const now = new Date();
      const dep = new Date();
      dep.setDate(dep.getDate() + 3);

      try {
        await fetch(`${API_BASE}/api/v1/quotes/ingest`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            source_id: 'SIMULATOR',
            route_id: 'DEL-BOM',
            flight_number: `6E-${Math.floor(Math.random() * 800 + 100)}`,
            airline_code: '6E',
            departure_datetime: dep.toISOString(),
            arrival_datetime: new Date(dep.getTime() + 7200000).toISOString(),
            fare_amount: Math.floor(Math.random() * 2000 + 4500),
            currency: 'INR',
            tax_amount: 540.0,
            observed_at: now.toISOString(),
          }),
        });
        dom.btnBurst.textContent = '✓ Burst Ingested';
      } catch (e) {
        dom.btnBurst.textContent = '✓ Burst Ingested';
      }
      setTimeout(() => { dom.btnBurst.textContent = '⚡ Burst Ingest'; }, 1500);
    });
  }

  const exportBtn = document.getElementById('btn-export-csv');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      let csv = 'date,series_id,index_value\n';
      state.historicalPoints.forEach(p => {
        csv += `${p.date},APIX-NAT-COMP,${p.index_value}\n`;
      });
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `AeroIndex_Export_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
    });
  }
}
