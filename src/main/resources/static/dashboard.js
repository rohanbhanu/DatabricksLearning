"use strict";

/* =========================================================
   GLOBAL STATE
========================================================= */

let trendData = [];
let currentMetric = "gwp";

const levels = [
    "region",
    "state",
    "product",
    "channel"
];

let drillIndex = 0;

let filters = {
    region: null,
    state: null,
    product: null
};


/* =========================================================
   FORMATTING
========================================================= */

function money(value) {

    const v = Number(value || 0);

    if (v >= 10000000) {
        return "₹" +
            (v / 10000000).toFixed(1) +
            " Cr";
    }

    return "₹" +
        new Intl.NumberFormat("en-IN")
            .format(v);
}


function number(value) {

    return new Intl.NumberFormat("en-IN")
        .format(Number(value || 0));
}


function percent(value) {

    return (
        Number(value || 0) * 100
    ).toFixed(1) + "%";
}


/* =========================================================
   API HELPER
========================================================= */

async function getJson(url) {

    console.log(
        "[DASHBOARD] Calling:",
        url
    );

    const response =
        await fetch(url, {
            method: "GET",
            headers: {
                "Accept": "application/json"
            },
            cache: "no-store"
        });


    let data;

    try {

        data =
            await response.json();

    } catch (error) {

        throw new Error(
            "Invalid JSON returned from " +
            url
        );
    }


    if (!response.ok) {

        throw new Error(
            data.error ||
            data.message ||
            (
                "Request failed with HTTP " +
                response.status
            )
        );
    }


    return data;
}


/* =========================================================
   EXECUTIVE KPI
========================================================= */

async function loadKpi() {

    const data =
        await getJson("/api/kpi");


    const cards = [

        {
            label: "Gross Written Premium",
            value: money(
                data.grossWrittenPremium
            )
        },

        {
            label: "Earned Premium",
            value: money(
                data.earnedPremium
            )
        },

        {
            label: "Policies in Force",
            value: number(
                data.policiesInForce
            )
        },

        {
            label: "Claims Incurred",
            value: money(
                data.claimsIncurred
            )
        },

        {
            label: "Loss Ratio",
            value: percent(
                data.lossRatio
            ),
            css:
                Number(data.lossRatio) > 1
                    ? "bad"
                    : "good"
        },

        {
            label: "Expense Ratio",
            value: percent(
                data.expenseRatio
            )
        },

        {
            label: "Combined Ratio",
            value: percent(
                data.combinedRatio
            ),
            css:
                Number(data.combinedRatio) > 1
                    ? "bad"
                    : "good"
        },

        {
            label: "Retention Rate",
            value: percent(
                data.retentionRate
            ),
            css: "good"
        },

        {
            label: "Claims / 1,000 Policies",
            value:
                Number(
                    data.claimFrequency || 0
                ).toFixed(1)
        }

    ];


    const grid =
        document.getElementById(
            "kpiGrid"
        );


    if (!grid) {

        console.error(
            "[DASHBOARD] kpiGrid not found"
        );

        return;
    }


    grid.innerHTML =
        cards.map(card => `

            <article class="kpi">

                <div class="kpi-label">
                    ${card.label}
                </div>

                <div class="kpi-value ${card.css || ""}">
                    ${card.value}
                </div>

            </article>

        `).join("");


    const reportMonth =
        document.getElementById(
            "reportMonth"
        );


    if (reportMonth) {

        reportMonth.textContent =
            "Reporting month: " +
            (
                data.asOfMonth ||
                "-"
            );
    }
}


/* =========================================================
   TREND DATA
========================================================= */

async function loadTrend() {

    trendData =
        await getJson(
            "/api/trend"
        );


    if (!Array.isArray(trendData)) {

        throw new Error(
            "/api/trend did not return an array"
        );
    }


    console.log(
        "[DASHBOARD] Trend rows:",
        trendData.length
    );


    drawTrend();
}


/* =========================================================
   METRIC CONFIGURATION
========================================================= */

function getMetricConfig() {

    const configs = {

        gwp: {
            label:
                "Gross Written Premium",
            color:
                "#41dfff",
            formatter:
                money
        },

        claims: {
            label:
                "Claims Incurred",
            color:
                "#ff6577",
            formatter:
                money
        },

        policies: {
            label:
                "Policies in Force",
            color:
                "#41f2b5",
            formatter:
                number
        }

    };


    return (
        configs[currentMetric] ||
        configs.gwp
    );
}


/* =========================================================
   DRAW TREND CHART
========================================================= */

function drawTrend() {

    const svg =
        document.getElementById(
            "trendChart"
        );


    if (!svg) {

        console.error(
            "[DASHBOARD] trendChart not found"
        );

        return;
    }


    svg.innerHTML = "";


    if (
        !Array.isArray(trendData) ||
        trendData.length === 0
    ) {

        showTrendMessage(
            svg,
            "No monthly portfolio data available"
        );

        return;
    }


    const config =
        getMetricConfig();


    const width =
        1200;

    const height =
        390;


    const margin = {
        left: 75,
        right: 45,
        top: 50,
        bottom: 65
    };


    const values =
        trendData.map(row =>
            Number(
                row[currentMetric] || 0
            )
        );


    const maximum =
        Math.max(
            ...values,
            1
        );


    const minimum =
        Math.min(
            ...values,
            0
        );


    const usableWidth =
        width -
        margin.left -
        margin.right;


    const usableHeight =
        height -
        margin.top -
        margin.bottom;


    const range =
        Math.max(
            maximum - minimum,
            maximum * 0.10,
            1
        );


    const step =
        trendData.length > 1
            ?
            usableWidth /
            (
                trendData.length - 1
            )
            :
            0;


    const points =
        trendData.map(
            (row, index) => {

                const value =
                    Number(
                        row[currentMetric] || 0
                    );


                const x =
                    trendData.length === 1
                        ?
                        margin.left +
                        usableWidth / 2
                        :
                        margin.left +
                        index * step;


                const normalized =
                    (
                        value -
                        minimum
                    ) / range;


                const y =
                    margin.top +
                    usableHeight -
                    (
                        normalized *
                        usableHeight
                    );


                return {
                    x,
                    y,
                    value,
                    row
                };
            }
        );


    const pathData =
        points.map(
            (point, index) => {

                const command =
                    index === 0
                        ? "M"
                        : "L";


                return (
                    command +
                    " " +
                    point.x +
                    " " +
                    point.y
                );
            }
        ).join(" ");


    const baseline =
        height -
        margin.bottom;


    const areaData =
        pathData +
        " L " +
        points[points.length - 1].x +
        " " +
        baseline +
        " L " +
        points[0].x +
        " " +
        baseline +
        " Z";


    svg.innerHTML = `

        <defs>

            <linearGradient
                id="areaGradient"
                x1="0"
                y1="0"
                x2="0"
                y2="1">

                <stop
                    offset="0%"
                    stop-color="${config.color}"
                    stop-opacity="0.38">
                </stop>

                <stop
                    offset="100%"
                    stop-color="${config.color}"
                    stop-opacity="0">
                </stop>

            </linearGradient>

        </defs>


        <text
            x="${margin.left}"
            y="24"
            fill="#8eb3da"
            font-size="14">

            ${config.label}

        </text>


        <path
            class="chart-area"
            d="${areaData}">
        </path>


        <path
            id="trendLine"
            class="chart-line"
            stroke="${config.color}"
            d="${pathData}">
        </path>

    `;


    drawYAxis(
        svg,
        maximum,
        margin,
        usableHeight,
        config
    );


    points.forEach(
        (point, index) => {

            const month =
                String(
                    point.row.month || ""
                ).substring(
                    0,
                    7
                );


            svg.insertAdjacentHTML(
                "beforeend",
                `

                <circle
                    class="chart-dot"
                    cx="${point.x}"
                    cy="${point.y}"
                    r="7"
                    stroke="${config.color}"
                    data-index="${index}">
                </circle>


                <text
                    class="axis-label"
                    x="${point.x}"
                    y="${height - 24}"
                    text-anchor="middle">

                    ${month}

                </text>

                `
            );
        }
    );


    animateTrendLine();


    bindTrendTooltips();


    console.log(
        "[DASHBOARD] Chart redrawn:",
        currentMetric
    );
}


/* =========================================================
   Y AXIS
========================================================= */

function drawYAxis(
    svg,
    maximum,
    margin,
    usableHeight,
    config
) {

    const divisions = 4;


    for (
        let i = 0;
        i <= divisions;
        i++
    ) {

        const ratio =
            i / divisions;


        const y =
            margin.top +
            usableHeight -
            (
                ratio *
                usableHeight
            );


        const value =
            maximum *
            ratio;


        svg.insertAdjacentHTML(
            "beforeend",
            `

            <line
                x1="${margin.left}"
                y1="${y}"
                x2="1160"
                y2="${y}"
                stroke="rgba(142,179,218,0.12)"
                stroke-width="1">
            </line>


            <text
                x="${margin.left - 12}"
                y="${y + 5}"
                text-anchor="end"
                fill="#6f98bf"
                font-size="12">

                ${config.formatter(value)}

            </text>

            `
        );
    }
}


/* =========================================================
   TREND EMPTY/ERROR MESSAGE
========================================================= */

function showTrendMessage(
    svg,
    message
) {

    svg.innerHTML = `

        <text
            x="600"
            y="190"
            text-anchor="middle"
            fill="#8eb3da"
            font-size="18">

            ${message}

        </text>

    `;
}


/* =========================================================
   TREND LINE ANIMATION
========================================================= */

function animateTrendLine() {

    const path =
        document.getElementById(
            "trendLine"
        );


    if (!path) {
        return;
    }


    let length;

    try {

        length =
            path.getTotalLength();

    } catch (error) {

        return;
    }


    path.style.strokeDasharray =
        String(length);


    path.style.strokeDashoffset =
        String(length);


    path.getBoundingClientRect();


    requestAnimationFrame(
        () => {

            path.style.transition =
                "stroke-dashoffset 1.35s ease";


            path.style.strokeDashoffset =
                "0";
        }
    );
}


/* =========================================================
   TREND TOOLTIP
========================================================= */

function bindTrendTooltips() {

    const dots =
        document.querySelectorAll(
            ".chart-dot"
        );


    dots.forEach(dot => {

        dot.addEventListener(
            "mousemove",
            event => {

                const index =
                    Number(
                        dot.dataset.index
                    );


                const row =
                    trendData[index];


                if (!row) {
                    return;
                }


                showTooltip(
                    event,
                    `
                    <strong>
                        ${row.month || ""}
                    </strong>

                    <br><br>

                    Premium:
                    ${money(row.gwp)}

                    <br>

                    Claims:
                    ${money(row.claims)}

                    <br>

                    Policies:
                    ${number(row.policies)}

                    <br>

                    Loss Ratio:
                    ${percent(row.loss_ratio)}
                    `
                );
            }
        );


        dot.addEventListener(
            "mouseleave",
            hideTooltip
        );
    });
}


/* =========================================================
   PREMIUM / CLAIMS / POLICIES BUTTONS
========================================================= */

function initializeMetricButtons() {

    const buttons =
        document.querySelectorAll(
            ".metric"
        );


    console.log(
        "[DASHBOARD] Metric buttons found:",
        buttons.length
    );


    buttons.forEach(button => {

        button.addEventListener(
            "click",
            event => {

                event.preventDefault();


                const selectedMetric =
                    button.dataset.metric;


                if (
                    ![
                        "gwp",
                        "claims",
                        "policies"
                    ].includes(
                        selectedMetric
                    )
                ) {

                    console.error(
                        "[DASHBOARD] Invalid metric:",
                        selectedMetric
                    );

                    return;
                }


                currentMetric =
                    selectedMetric;


                buttons.forEach(
                    otherButton => {

                        otherButton.classList
                            .remove(
                                "active"
                            );
                    }
                );


                button.classList.add(
                    "active"
                );


                console.log(
                    "[DASHBOARD] Metric selected:",
                    currentMetric
                );


                drawTrend();
            }
        );
    });
}


/* =========================================================
   TOOLTIP
========================================================= */

function showTooltip(
    event,
    html
) {

    const tooltip =
        document.getElementById(
            "tooltip"
        );


    if (!tooltip) {
        return;
    }


    tooltip.innerHTML =
        html;


    const offset =
        18;


    let left =
        event.clientX +
        offset;


    let top =
        event.clientY +
        offset;


    const estimatedWidth =
        240;


    if (
        left +
        estimatedWidth >
        window.innerWidth
    ) {

        left =
            event.clientX -
            estimatedWidth -
            offset;
    }


    tooltip.style.left =
        left + "px";


    tooltip.style.top =
        top + "px";


    tooltip.style.opacity =
        "1";
}


function hideTooltip() {

    const tooltip =
        document.getElementById(
            "tooltip"
        );


    if (tooltip) {

        tooltip.style.opacity =
            "0";
    }
}


/* =========================================================
   PORTFOLIO DRILL DOWN
========================================================= */

async function loadDrilldown() {

    const level =
        levels[
            drillIndex
        ];


    const params =
        new URLSearchParams();


    params.set(
        "level",
        level
    );


    if (filters.region) {

        params.set(
            "region",
            filters.region
        );
    }


    if (filters.state) {

        params.set(
            "state",
            filters.state
        );
    }


    if (filters.product) {

        params.set(
            "product",
            filters.product
        );
    }


    const data =
        await getJson(
            "/api/drilldown?" +
            params.toString()
        );


    if (!Array.isArray(data)) {

        throw new Error(
            "Drilldown API did not return an array"
        );
    }


    drawBubbles(
        data,
        level
    );


    updateBreadcrumb();


    const rollUp =
        document.getElementById(
            "rollUp"
        );


    if (rollUp) {

        rollUp.disabled =
            drillIndex === 0;
    }
}


/* =========================================================
   BUBBLE CHART
========================================================= */

function drawBubbles(
    data,
    level
) {

    const container =
        document.getElementById(
            "bubbleChart"
        );


    if (!container) {

        console.error(
            "[DASHBOARD] bubbleChart not found"
        );

        return;
    }


    container.innerHTML =
        "";


    if (
        !data ||
        data.length === 0
    ) {

        container.innerHTML =
            `
            <p class="hint">
                No portfolio data available
                for the selected segment.
            </p>
            `;

        return;
    }


    const premiums =
        data.map(
            row =>
                Number(
                    row.premium || 0
                )
        );


    const maximum =
        Math.max(
            ...premiums,
            1
        );


    data.forEach(
        (row, index) => {

            const premium =
                Number(
                    row.premium || 0
                );


            const lossRatio =
                Number(
                    row.loss_ratio || 0
                );


            const scale =
                Math.sqrt(
                    premium /
                    maximum
                );


            const size =
                Math.max(
                    130,
                    Math.min(
                        245,
                        110 +
                        scale * 135
                    )
                );


            let hue;


            if (
                lossRatio >= 1
            ) {

                hue = 350;

            } else if (
                lossRatio >= 0.8
            ) {

                hue = 38;

            } else {

                hue = 165;
            }


            const bubble =
                document.createElement(
                    "div"
                );


            bubble.className =
                "bubble";


            bubble.style.width =
                size + "px";


            bubble.style.height =
                size + "px";


            bubble.style.background =
                `
                radial-gradient(
                    circle at 30% 25%,
                    hsla(
                        ${hue},
                        90%,
                        70%,
                        0.95
                    ),
                    hsla(
                        ${hue},
                        72%,
                        34%,
                        0.58
                    )
                )
                `;


            bubble.style.animationDelay =
                (
                    index * 70
                ) + "ms";


            const category =
                row.category ||
                "Unknown";


            bubble.innerHTML = `

                <div class="bubble-name">
                    ${escapeHtml(category)}
                </div>

                <div class="bubble-value">
                    ${money(premium)}
                </div>

                <div class="bubble-value">
                    Loss:
                    ${percent(lossRatio)}
                </div>

            `;


            bubble.addEventListener(
                "mousemove",
                event => {

                    showTooltip(
                        event,
                        `
                        <strong>
                            ${escapeHtml(category)}
                        </strong>

                        <br><br>

                        Premium:
                        ${money(row.premium)}

                        <br>

                        Claims:
                        ${money(row.claims)}

                        <br>

                        Policies:
                        ${number(row.policies)}

                        <br>

                        Loss Ratio:
                        ${percent(row.loss_ratio)}
                        `
                    );
                }
            );


            bubble.addEventListener(
                "mouseleave",
                hideTooltip
            );


            bubble.addEventListener(
                "click",
                () => {

                    drill(
                        level,
                        category
                    );
                }
            );


            container.appendChild(
                bubble
            );
        }
    );
}


/* =========================================================
   DRILL ACTION
========================================================= */

function drill(
    level,
    value
) {

    if (
        drillIndex >=
        levels.length - 1
    ) {

        console.log(
            "[DASHBOARD] Lowest drill level reached"
        );

        return;
    }


    if (
        level === "region"
    ) {

        filters.region =
            value;


        filters.state =
            null;


        filters.product =
            null;

    } else if (
        level === "state"
    ) {

        filters.state =
            value;


        filters.product =
            null;

    } else if (
        level === "product"
    ) {

        filters.product =
            value;
    }


    drillIndex++;


    console.log(
        "[DASHBOARD] Drill:",
        level,
        value
    );


    loadDrilldown()
        .catch(error => {

            console.error(
                "[DASHBOARD] Drilldown failed:",
                error
            );
        });
}


/* =========================================================
   ROLL UP
========================================================= */

function rollUp() {

    if (
        drillIndex === 0
    ) {

        return;
    }


    const selectedParentLevel =
        levels[
            drillIndex - 1
        ];


    if (
        selectedParentLevel ===
        "product"
    ) {

        filters.product =
            null;

    } else if (
        selectedParentLevel ===
        "state"
    ) {

        filters.state =
            null;


        filters.product =
            null;

    } else if (
        selectedParentLevel ===
        "region"
    ) {

        filters.region =
            null;


        filters.state =
            null;


        filters.product =
            null;
    }


    drillIndex--;


    console.log(
        "[DASHBOARD] Roll up to:",
        levels[drillIndex]
    );


    loadDrilldown()
        .catch(error => {

            console.error(
                "[DASHBOARD] Roll-up failed:",
                error
            );
        });
}


/* =========================================================
   BREADCRUMB
========================================================= */

function updateBreadcrumb() {

    const breadcrumb =
        document.getElementById(
            "breadcrumb"
        );


    if (!breadcrumb) {
        return;
    }


    const pieces = [
        "Enterprise"
    ];


    if (filters.region) {

        pieces.push(
            filters.region
        );
    }


    if (filters.state) {

        pieces.push(
            filters.state
        );
    }


    if (filters.product) {

        pieces.push(
            filters.product
        );
    }


    const currentLevel =
        levels[
            drillIndex
        ];


    const title =
        currentLevel
            .charAt(0)
            .toUpperCase() +
        currentLevel.slice(1);


    pieces.push(
        title
    );


    breadcrumb.textContent =
        pieces.join(
            " › "
        );
}


/* =========================================================
   CLAIM STATUS
========================================================= */

async function loadClaims() {

    const data =
        await getJson(
            "/api/claims"
        );


    if (!Array.isArray(data)) {

        throw new Error(
            "Claims API did not return an array"
        );
    }


    const container =
        document.getElementById(
            "claimsChart"
        );


    if (!container) {

        console.error(
            "[DASHBOARD] claimsChart not found"
        );

        return;
    }


    if (
        data.length === 0
    ) {

        container.innerHTML =
            `
            <p class="hint">
                No claims data available.
            </p>
            `;

        return;
    }


    const maximum =
        Math.max(
            ...data.map(
                row =>
                    Number(
                        row.claim_count || 0
                    )
            ),
            1
        );


    container.innerHTML =
        data.map(
            row => {

                const count =
                    Number(
                        row.claim_count || 0
                    );


                const width =
                    (
                        count /
                        maximum
                    ) * 100;


                return `

                <div class="claim-row">

                    <span>
                        ${escapeHtml(
                            row.claim_status ||
                            "Unknown"
                        )}
                    </span>


                    <div class="claim-track">

                        <div
                            class="claim-bar"
                            data-width="${width}">
                        </div>

                    </div>


                    <strong>
                        ${number(count)}
                    </strong>

                </div>

                `;
            }
        ).join("");


    requestAnimationFrame(
        () => {

            const bars =
                document.querySelectorAll(
                    ".claim-bar"
                );


            bars.forEach(
                (bar, index) => {

                    setTimeout(
                        () => {

                            bar.style.width =
                                bar.dataset.width +
                                "%";
                        },
                        index * 100
                    );
                }
            );
        }
    );
}


/* =========================================================
   CLAIM RISK
========================================================= */

async function loadRisk() {

    const data =
        await getJson(
            "/api/claim-risk"
        );


    const container =
        document.getElementById(
            "riskCards"
        );


    if (!container) {

        console.error(
            "[DASHBOARD] riskCards not found"
        );

        return;
    }


    const totalClaims =
        data.total_claims ??
        data.TOTAL_CLAIMS ??
        0;


    const slaBreaches =
        data.sla_breaches ??
        data.SLA_BREACHES ??
        0;


    const fraudRisk =
        data.avg_fraud_score ??
        data.AVG_FRAUD_SCORE ??
        0;


    const settlementDays =
        data.avg_settlement_days ??
        data.AVG_SETTLEMENT_DAYS ??
        0;


    const outstanding =
        data.outstanding_amount ??
        data.OUTSTANDING_AMOUNT ??
        0;


    const cards = [

        {
            label:
                "Total Claims",
            value:
                number(
                    totalClaims
                )
        },

        {
            label:
                "SLA Breaches",
            value:
                number(
                    slaBreaches
                ),
            css:
                Number(
                    slaBreaches
                ) > 0
                    ? "bad"
                    : "good"
        },

        {
            label:
                "Average Fraud Risk",
            value:
                Number(
                    fraudRisk
                ).toFixed(2)
        },

        {
            label:
                "Avg Settlement Days",
            value:
                Number(
                    settlementDays
                ).toFixed(1)
        },

        {
            label:
                "Outstanding Claims",
            value:
                money(
                    outstanding
                )
        }

    ];


    container.innerHTML =
        cards.map(
            card => `

            <article class="risk-card">

                <div class="kpi-label">
                    ${card.label}
                </div>

                <div
                    class="risk-value ${card.css || ""}">
                    ${card.value}
                </div>

            </article>

            `
        ).join("");
}


/* =========================================================
   HTML ESCAPE
========================================================= */

function escapeHtml(value) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        String(
            value ?? ""
        );


    return div.innerHTML;
}


/* =========================================================
   ROLL-UP BUTTON INITIALIZATION
========================================================= */

function initializeRollUpButton() {

    const button =
        document.getElementById(
            "rollUp"
        );


    if (!button) {

        console.error(
            "[DASHBOARD] rollUp button not found"
        );

        return;
    }


    button.addEventListener(
        "click",
        event => {

            event.preventDefault();

            rollUp();
        }
    );
}


/* =========================================================
   LOAD COMPONENT SAFELY
========================================================= */

async function loadComponent(
    name,
    functionToRun
) {

    try {

        await functionToRun();


        console.log(
            "[DASHBOARD] Loaded:",
            name
        );


        return true;

    } catch (error) {

        console.error(
            "[DASHBOARD] Failed:",
            name,
            error
        );


        return false;
    }
}


/* =========================================================
   DASHBOARD START
========================================================= */

async function startDashboard() {

    console.log(
        "[DASHBOARD] Initializing..."
    );


    /*
     * Attach browser interaction first.
     * These should work independently of API calls.
     */

    initializeMetricButtons();

    initializeRollUpButton();


    /*
     * Load components independently.
     *
     * A failure in Claims, for example,
     * must not prevent KPI or Trend from working.
     */

    await loadComponent(
        "Executive KPI",
        loadKpi
    );


    await loadComponent(
        "Portfolio Trend",
        loadTrend
    );


    await loadComponent(
        "Portfolio Drilldown",
        loadDrilldown
    );


    await loadComponent(
        "Claims Summary",
        loadClaims
    );


    await loadComponent(
        "Claim Risk",
        loadRisk
    );


    console.log(
        "[DASHBOARD] Initialization complete."
    );
}


/* =========================================================
   START AFTER HTML IS READY
========================================================= */

if (
    document.readyState ===
    "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        startDashboard
    );

} else {

    startDashboard();
}