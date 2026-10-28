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


const money = value => {

    const v = Number(value || 0);

    if (v >= 10000000) {
        return "₹" +
            (v / 10000000).toFixed(1) +
            " Cr";
    }

    return "₹" +
        new Intl.NumberFormat("en-IN")
            .format(v);
};


const number = value =>
    new Intl.NumberFormat("en-IN")
        .format(Number(value || 0));


const percent = value =>
    (Number(value || 0) * 100)
        .toFixed(1) + "%";


async function getJson(url) {

    const response =
        await fetch(url);

    const data =
        await response.json();

    if (!response.ok) {

        throw new Error(
            data.error ||
            "Request failed"
        );
    }

    return data;
}


/* ======================================================
   KPI
====================================================== */

async function loadKpi() {

    const d =
        await getJson("/api/kpi");

    const cards = [

        [
            "Gross Written Premium",
            money(d.grossWrittenPremium)
        ],

        [
            "Earned Premium",
            money(d.earnedPremium)
        ],

        [
            "Policies in Force",
            number(d.policiesInForce)
        ],

        [
            "Claims Incurred",
            money(d.claimsIncurred)
        ],

        [
            "Loss Ratio",
            percent(d.lossRatio),
            d.lossRatio > 1
                ? "bad"
                : "good"
        ],

        [
            "Expense Ratio",
            percent(d.expenseRatio)
        ],

        [
            "Combined Ratio",
            percent(d.combinedRatio),
            d.combinedRatio > 1
                ? "bad"
                : "good"
        ],

        [
            "Retention Rate",
            percent(d.retentionRate),
            "good"
        ],

        [
            "Claims / 1,000",
            Number(
                d.claimFrequency
            ).toFixed(1)
        ]

    ];

    document.getElementById(
        "kpiGrid"
    ).innerHTML =
        cards.map(
            ([label, value, cls = ""]) => `
                <div class="kpi">
                    <div class="kpi-label">
                        ${label}
                    </div>

                    <div
                        class="kpi-value ${cls}"
                        data-target="${value}"
                    >
                        ${value}
                    </div>
                </div>
            `
        ).join("");

    document.getElementById(
        "reportMonth"
    ).textContent =
        "Reporting month: " +
        d.asOfMonth;
}


/* ======================================================
   TREND
====================================================== */

async function loadTrend() {

    trendData =
        await getJson("/api/trend");

    drawTrend();
}


function drawTrend() {

    const svg =
        document.getElementById(
            "trendChart"
        );

    svg.innerHTML = "";

    if (!trendData.length) return;

    const width = 1200;
    const height = 390;

    const margin = {
        left: 60,
        right: 30,
        top: 35,
        bottom: 55
    };

    const values =
        trendData.map(
            d => Number(
                d[currentMetric] || 0
            )
        );

    const max =
        Math.max(...values, 1);

    const step =
        (
            width -
            margin.left -
            margin.right
        ) /
        Math.max(
            trendData.length - 1,
            1
        );


    const points =
        trendData.map(
            (d, i) => {

                const x =
                    margin.left +
                    i * step;

                const y =
                    height -
                    margin.bottom -
                    (
                        Number(
                            d[currentMetric] || 0
                        ) / max
                    ) *
                    (
                        height -
                        margin.top -
                        margin.bottom
                    );

                return {
                    x,
                    y,
                    d
                };
            }
        );


    svg.innerHTML = `
        <defs>

            <linearGradient
                id="areaGradient"
                x1="0"
                y1="0"
                x2="0"
                y2="1"
            >

                <stop
                    offset="0%"
                    stop-color="#41dfff"
                    stop-opacity=".34"
                />

                <stop
                    offset="100%"
                    stop-color="#41dfff"
                    stop-opacity="0"
                />

            </linearGradient>

        </defs>
    `;


    const path =
        points.map(
            (p, i) =>
                `${i ? "L" : "M"} ${p.x} ${p.y}`
        ).join(" ");


    const baseline =
        height - margin.bottom;


    const area =
        `${path}
         L ${points.at(-1).x} ${baseline}
         L ${points[0].x} ${baseline}
         Z`;


    svg.insertAdjacentHTML(
        "beforeend",
        `
        <path
            class="chart-area"
            d="${area}"
        />

        <path
            id="trendLine"
            class="chart-line"
            d="${path}"
        />
        `
    );


    points.forEach(
        (p, i) => {

            const label =
                String(
                    p.d.month || ""
                ).substring(0, 7);

            svg.insertAdjacentHTML(
                "beforeend",
                `
                <circle
                    class="chart-dot"
                    cx="${p.x}"
                    cy="${p.y}"
                    r="7"
                    data-index="${i}"
                />

                <text
                    class="axis-label"
                    x="${p.x}"
                    y="${height - 20}"
                    text-anchor="middle"
                >
                    ${label}
                </text>
                `
            );
        }
    );


    animatePath(
        document.getElementById(
            "trendLine"
        )
    );


    bindTrendTooltips();
}


function animatePath(path) {

    if (!path) return;

    const length =
        path.getTotalLength();

    path.style.strokeDasharray =
        length;

    path.style.strokeDashoffset =
        length;

    path
        .getBoundingClientRect();

    path.style.transition =
        "stroke-dashoffset 1.5s ease";

    path.style.strokeDashoffset =
        "0";
}


/* ======================================================
   TOOLTIP
====================================================== */

function showTooltip(
    event,
    html
) {

    const t =
        document.getElementById(
            "tooltip"
        );

    t.innerHTML = html;

    t.style.left =
        event.clientX + 15 + "px";

    t.style.top =
        event.clientY + 15 + "px";

    t.style.opacity = 1;
}


function hideTooltip() {

    document.getElementById(
        "tooltip"
    ).style.opacity = 0;
}


function bindTrendTooltips() {

    document
        .querySelectorAll(
            ".chart-dot"
        )
        .forEach(dot => {

            dot.addEventListener(
                "mousemove",
                e => {

                    const d =
                        trendData[
                            Number(
                                dot.dataset.index
                            )
                        ];

                    showTooltip(
                        e,
                        `
                        <b>${d.month}</b><br>
                        Premium:
                        ${money(d.gwp)}
                        <br>
                        Claims:
                        ${money(d.claims)}
                        <br>
                        Policies:
                        ${number(d.policies)}
                        <br>
                        Loss Ratio:
                        ${percent(d.loss_ratio)}
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


/* ======================================================
   DRILL DOWN
====================================================== */

async function loadDrilldown() {

    const level =
        levels[drillIndex];

    const params =
        new URLSearchParams({
            level
        });

    if (filters.region)
        params.set(
            "region",
            filters.region
        );

    if (filters.state)
        params.set(
            "state",
            filters.state
        );

    if (filters.product)
        params.set(
            "product",
            filters.product
        );


    const data =
        await getJson(
            "/api/drilldown?" +
            params.toString()
        );


    drawBubbles(
        data,
        level
    );

    updateBreadcrumb();

    document.getElementById(
        "rollUp"
    ).disabled =
        drillIndex === 0;
}


function drawBubbles(
    data,
    level
) {

    const container =
        document.getElementById(
            "bubbleChart"
        );

    container.innerHTML = "";


    if (!data.length) {

        container.innerHTML =
            "<p>No portfolio data.</p>";

        return;
    }


    const premiums =
        data.map(
            d => Number(
                d.premium || 0
            )
        );


    const max =
        Math.max(
            ...premiums,
            1
        );


    data.forEach(
        (d, i) => {

            const premium =
                Number(
                    d.premium || 0
                );

            const loss =
                Number(
                    d.loss_ratio || 0
                );


            const size =
                105 +
                Math.sqrt(
                    premium / max
                ) * 125;


            const hue =
                loss > 1
                    ? "350"
                    : loss > .75
                        ? "37"
                        : "165";


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
                    hsla(${hue},90%,70%,.9),
                    hsla(${hue},70%,38%,.55)
                )
                `;


            bubble.style.animationDelay =
                i * 60 + "ms";


            bubble.innerHTML =
                `
                <div class="bubble-name">
                    ${d.category}
                </div>

                <div class="bubble-value">
                    ${money(premium)}
                </div>

                <div class="bubble-value">
                    LR ${percent(loss)}
                </div>
                `;


            bubble.addEventListener(
                "mousemove",
                e => {

                    showTooltip(
                        e,
                        `
                        <b>${d.category}</b>
                        <br>
                        Premium:
                        ${money(d.premium)}
                        <br>
                        Claims:
                        ${money(d.claims)}
                        <br>
                        Policies:
                        ${number(d.policies)}
                        <br>
                        Loss Ratio:
                        ${percent(d.loss_ratio)}
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
                () => drill(
                    level,
                    d.category
                )
            );


            container.appendChild(
                bubble
            );
        }
    );
}


function drill(
    level,
    value
) {

    if (
        drillIndex >=
        levels.length - 1
    ) return;


    filters[level] =
        value;

    drillIndex++;

    loadDrilldown();
}


function rollUp() {

    if (drillIndex === 0)
        return;


    const previousLevel =
        levels[
            drillIndex - 1
        ];


    filters[
        previousLevel
    ] = null;


    drillIndex--;

    loadDrilldown();
}


function updateBreadcrumb() {

    let pieces = [
        "Enterprise"
    ];

    if (filters.region)
        pieces.push(
            filters.region
        );

    if (filters.state)
        pieces.push(
            filters.state
        );

    if (filters.product)
        pieces.push(
            filters.product
        );


    pieces.push(
        levels[drillIndex]
            .charAt(0)
            .toUpperCase() +
        levels[drillIndex]
            .slice(1)
    );


    document.getElementById(
        "breadcrumb"
    ).textContent =
        pieces.join(" › ");
}


/* ======================================================
   CLAIMS
====================================================== */

async function loadClaims() {

    const data =
        await getJson(
            "/api/claims"
        );


    const container =
        document.getElementById(
            "claimsChart"
        );


    const max =
        Math.max(
            ...data.map(
                x =>
                    Number(
                        x.claim_count || 0
                    )
            ),
            1
        );


    container.innerHTML =
        data.map(
            d => {

                const count =
                    Number(
                        d.claim_count || 0
                    );

                const width =
                    count / max * 100;


                return `
                    <div class="claim-row">

                        <span>
                            ${d.claim_status}
                        </span>

                        <div class="claim-track">

                            <div
                                class="claim-bar"
                                data-width="${width}"
                            ></div>

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

            document
                .querySelectorAll(
                    ".claim-bar"
                )
                .forEach(
                    bar => {

                        bar.style.width =
                            bar.dataset.width +
                            "%";
                    }
                );
        }
    );
}


/* ======================================================
   RISK
====================================================== */

async function loadRisk() {

    const d =
        await getJson(
            "/api/claim-risk"
        );


    const cards = [

        [
            "Total Claims",
            number(d.total_claims)
        ],

        [
            "SLA Breaches",
            number(d.sla_breaches),
            "bad"
        ],

        [
            "Average Fraud Risk",
            Number(
                d.avg_fraud_score || 0
            ).toFixed(2)
        ],

        [
            "Avg Settlement Days",
            Number(
                d.avg_settlement_days || 0
            ).toFixed(1)
        ],

        [
            "Outstanding Claims",
            money(
                d.outstanding_amount
            )
        ]

    ];


    document.getElementById(
        "riskCards"
    ).innerHTML =
        cards.map(
            ([label, value, cls = ""]) =>
                `
                <div class="risk-card">

                    <div class="kpi-label">
                        ${label}
                    </div>

                    <div
                        class="risk-value ${cls}"
                    >
                        ${value}
                    </div>

                </div>
                `
        ).join("");
}


/* ======================================================
   METRIC BUTTONS
====================================================== */

document
    .querySelectorAll(
        ".metric"
    )
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                document
                    .querySelectorAll(
                        ".metric"
                    )
                    .forEach(
                        x =>
                            x.classList.remove(
                                "active"
                            )
                    );

                button.classList.add(
                    "active"
                );

                currentMetric =
                    button.dataset.metric;

                drawTrend();
            }
        );
    });


document
    .getElementById(
        "rollUp"
    )
    .addEventListener(
        "click",
        rollUp
    );


/* ======================================================
   INITIAL LOAD
====================================================== */

async function startDashboard() {

    try {

        await Promise.all([
            loadKpi(),
            loadTrend(),
            loadDrilldown(),
            loadClaims(),
            loadRisk()
        ]);

    }
    catch (error) {

        console.error(
            "Dashboard load failed:",
            error
        );
    }
}


startDashboard();