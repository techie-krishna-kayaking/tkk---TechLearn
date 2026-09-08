# AI/BI Concepts - Business Intelligence and Analytics from QA Perspective

## Executive Summary

Business Intelligence (BI) transforms raw data into actionable insights through reports, dashboards, and analytics. Modern AI-powered BI integrates machine learning for predictive analytics, natural language queries, and automated insights. From a **QA perspective**, testing BI systems requires validating data accuracy, visualization correctness, query performance, user access controls, and AI-generated recommendations.

**Target Audience**: Senior QA engineers (7+ years) testing BI platforms, dashboards, analytics applications, and AI-powered insights.

---

## Why This Matters in Enterprise

### Business Impact
- **BI market size**: $27.1B in 2025, projected $54.3B by 2030 (Gartner)
- **Data-driven decisions**: 65% of organizations cite BI as critical to strategy
- **ROI**: $13.01 return for every $1 invested in BI (Nucleus Research)
- **AI-powered BI**: 80% of BI platforms will embed AI by 2026 (Gartner)

### Technical Imperative
- **Trust in data**: Executives make million-dollar decisions based on dashboards (accuracy critical)
- **Performance at scale**: Dashboards must load <5 sec with billion-row datasets
- **Self-service analytics**: Non-technical users create reports (validation essential)
- **AI transparency**: Automated insights must be explainable (no black-box recommendations)

### Career Value
- **BI/Analytics QA demand**: 68% growth in BI testing roles (Dice 2025)
- **Salary premium**: 30-45% higher for BI + QA expertise
- **Cross-functional**: Bridges data engineering, analytics, business stakeholders

---

## Scope and Boundaries

### In Scope
- BI fundamentals (reports, dashboards, KPIs, metrics)
- BI architecture (semantic layer, OLAP, data marts)
- Visualization testing (chart accuracy, responsiveness)
- Query performance testing (optimization, caching)
- AI-powered BI (NLQ, automated insights, forecasting)
- Self-service analytics validation
- Embedded analytics and APIs

### Out of Scope
- DWH design (covered in [01_DWH_Concepts_QA_Perspective.md](./01_DWH_Concepts_QA_Perspective.md))
- ETL testing (covered in [04_ETL_Concepts.md](./04_ETL_Concepts.md))
- Platform-specific BI tools (Tableau, Power BI, Looker covered in stack files)

---

## BI Architecture

### Layered Architecture

    ```mermaid
    graph TD
        A[Data Sources] --> B[Data Warehouse]
        B --> C[Semantic Layer]
        C --> D[BI Tools]
        D --> E[Reports]
        D --> F[Dashboards]
        D --> G[Ad-hoc Analysis]
        
        H[AI Engine] --> D
        
        style C fill:#e1f5ff
        style D fill:#ffe1f5
        style H fill:#fff4e1
    ```

**Key Components**:

1. **Semantic Layer**: Business-friendly metadata (Sales Revenue, not sum(order_amount))
2. **OLAP Cube**: Pre-aggregated data for fast queries
3. **Data Mart**: Subject-specific subset (Sales Mart, Finance Mart)
4. **BI Tool**: User interface for analysis (Tableau, Power BI, Looker)
5. **AI Engine**: ML models for predictions, anomaly detection, NLQ

---

## BI Testing Fundamentals

### 1. Data Accuracy Testing

**Report Reconciliation**:
    ```python
    def test_report_accuracy():
        """Validate BI report matches source data"""
        
        # Source query (ground truth)
        source_query = """
            SELECT 
                DATE(order_date) as date,
                SUM(order_amount) as total_revenue
            FROM orders
            WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31'
            GROUP BY DATE(order_date)
        """
        source_data = execute_query(source_query)
        source_total = sum([row['total_revenue'] for row in source_data])
        
        # BI report query
        report_data = get_report_data("Monthly Sales Report", month="2024-01")
        report_total = sum([row['Revenue'] for row in report_data])
        
        # Validate totals match (allow 0.01% tolerance for rounding)
        difference_pct = abs(source_total - report_total) / source_total * 100
        
        assert difference_pct < 0.01, \
            f"Revenue mismatch: Source=${source_total:,.2f}, " \
            f"Report=${report_total:,.2f} (diff: {difference_pct:.4f}%)"
    ```

**Aggregation Validation**:
    ```python
    def test_aggregation_accuracy():
        """Validate SUM, AVG, COUNT in dashboard"""
        
        # Dashboard shows: Total Orders = 1,000, Avg Order Value = $150
        dashboard_metrics = get_dashboard_metrics("Sales Overview")
        
        # Direct database query
        db_metrics = execute_query("""
            SELECT 
                COUNT(*) as total_orders,
                AVG(order_amount) as avg_order_value,
                SUM(order_amount) as total_revenue
            FROM orders
            WHERE order_date >= CURRENT_DATE - INTERVAL 30 DAY
        """)[0]
        
        # Validate each metric
        assert dashboard_metrics['Total Orders'] == db_metrics['total_orders'], \
            f"Order count mismatch: {dashboard_metrics['Total Orders']} vs {db_metrics['total_orders']}"
        
        assert abs(dashboard_metrics['Avg Order Value'] - db_metrics['avg_order_value']) < 0.01, \
            f"Avg order value mismatch: {dashboard_metrics['Avg Order Value']:.2f} vs {db_metrics['avg_order_value']:.2f}"
    ```

### 2. Visualization Testing

**Chart Type Validation**:
    ```python
    def test_chart_rendering():
        """Validate charts render correctly"""
        
        # Load dashboard
        dashboard = load_dashboard("Sales Analysis")
        
        # Validate chart exists
        revenue_chart = dashboard.get_chart("Revenue Trend")
        assert revenue_chart is not None, "Revenue Trend chart not found"
        
        # Validate chart type
        assert revenue_chart.type == "line", \
            f"Wrong chart type: {revenue_chart.type} (expected: line)"
        
        # Validate data points
        data_points = revenue_chart.get_data_points()
        assert len(data_points) == 12, \
            f"Expected 12 months, got {len(data_points)}"
        
        # Validate axes
        assert revenue_chart.x_axis.label == "Month", "Wrong X-axis label"
        assert revenue_chart.y_axis.label == "Revenue ($)", "Wrong Y-axis label"
    ```

**Visual Regression Testing**:
    ```python
    from PIL import Image
    import imagehash
    
    def test_visual_regression():
        """Detect unexpected visual changes in dashboard"""
        
        # Capture current screenshot
        current_screenshot = capture_dashboard_screenshot("Sales Dashboard")
        current_hash = imagehash.average_hash(Image.open(current_screenshot))
        
        # Load baseline screenshot
        baseline_screenshot = "baselines/sales_dashboard.png"
        baseline_hash = imagehash.average_hash(Image.open(baseline_screenshot))
        
        # Calculate difference (0 = identical, higher = more different)
        hash_diff = current_hash - baseline_hash
        
        # Allow small differences (anti-aliasing, date changes)
        assert hash_diff < 5, \
            f"Visual regression detected: hash diff = {hash_diff}"
    ```

### 3. Filter and Drill-Down Testing

    ```python
    def test_interactive_filters():
        """Validate filters update charts correctly"""
        
        dashboard = load_dashboard("Regional Sales")
        
        # Initial state (all regions)
        initial_data = dashboard.get_chart_data("Sales by Region")
        initial_total = sum([d['sales'] for d in initial_data])
        
        # Apply filter (only US)
        dashboard.apply_filter("Region", value="US")
        
        filtered_data = dashboard.get_chart_data("Sales by Region")
        
        # Validate only US data shown
        assert len(filtered_data) == 1, \
            f"Expected 1 region after filter, got {len(filtered_data)}"
        assert filtered_data[0]['region'] == "US"
        
        # Validate total decreased (US < all regions)
        filtered_total = filtered_data[0]['sales']
        assert filtered_total < initial_total, \
            "Filtered total should be less than unfiltered"
        
        # Validate against database
        db_total = execute_query(
            "SELECT SUM(sales) FROM orders WHERE region = 'US'"
        )[0][0]
        
        assert abs(filtered_total - db_total) < 0.01, \
            f"Filter data mismatch: Dashboard=${filtered_total:,.2f}, DB=${db_total:,.2f}"
    ```

**Drill-Down Testing**:
    ```python
    def test_drill_down():
        """Validate drill-down from summary to detail"""
        
        dashboard = load_dashboard("Sales Hierarchy")
        
        # Top level: Total Sales by Region
        region_chart = dashboard.get_chart("Sales by Region")
        us_sales = [d for d in region_chart.get_data_points() if d['region'] == 'US'][0]
        
        # Drill down: Click on US to see states
        dashboard.drill_down("Sales by Region", "US")
        
        state_chart = dashboard.get_chart("Sales by State")
        state_data = state_chart.get_data_points()
        
        # Validate states sum to US total
        states_total = sum([d['sales'] for d in state_data])
        
        assert abs(states_total - us_sales['sales']) < 0.01, \
            f"Drill-down total mismatch: States=${states_total:,.2f}, US=${us_sales['sales']:,.2f}"
    ```

---

## Performance Testing

### Dashboard Load Time

    ```python
    import time
    
    def test_dashboard_load_time():
        """Validate dashboard loads within SLA"""
        
        dashboards = [
            {"name": "Executive Summary", "max_load_sec": 3},
            {"name": "Sales Analysis", "max_load_sec": 5},
            {"name": "Inventory Detail", "max_load_sec": 10}
        ]
        
        for dashboard_config in dashboards:
            start = time.time()
            dashboard = load_dashboard(dashboard_config["name"])
            load_time = time.time() - start
            
            assert load_time < dashboard_config["max_load_sec"], \
                f"Dashboard '{dashboard_config['name']}' load time {load_time:.2f}s " \
                f"exceeds SLA {dashboard_config['max_load_sec']}s"
    ```

### Query Performance Testing

    ```python
    def test_query_performance():
        """Validate report queries execute within SLA"""
        
        report = "Top 100 Customers by Revenue"
        
        # Execute query multiple times
        execution_times = []
        for _ in range(10):
            start = time.time()
            data = get_report_data(report)
            execution_times.append(time.time() - start)
        
        # Calculate percentiles
        p50 = sorted(execution_times)[4]  # Median
        p95 = sorted(execution_times)[9]  # 95th percentile
        
        # Validate SLA
        assert p50 < 2.0, f"p50 query time {p50:.2f}s exceeds 2s SLA"
        assert p95 < 5.0, f"p95 query time {p95:.2f}s exceeds 5s SLA"
    ```

### Concurrent User Load Testing

    ```python
    from concurrent.futures import ThreadPoolExecutor
    
    def test_concurrent_users():
        """Validate BI system handles 100 concurrent users"""
        
        def load_dashboard_as_user(user_id):
            try:
                start = time.time()
                dashboard = load_dashboard("Sales Dashboard", user=f"user_{user_id}")
                latency = time.time() - start
                return {"success": True, "latency": latency}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # Simulate 100 concurrent users
        num_users = 100
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            results = list(executor.map(load_dashboard_as_user, range(num_users)))
        
        # Validate success rate
        successes = [r for r in results if r["success"]]
        success_rate = len(successes) / num_users * 100
        
        assert success_rate >= 95, \
            f"Success rate {success_rate:.1f}% below 95% threshold"
        
        # Validate p95 latency
        latencies = sorted([r["latency"] for r in successes])
        p95_latency = latencies[int(len(latencies) * 0.95)]
        
        assert p95_latency < 10, \
            f"p95 latency {p95_latency:.2f}s exceeds 10s under load"
    ```

---

## AI-Powered BI Testing

### Natural Language Query (NLQ)

    ```python
    def test_natural_language_query():
        """Validate NLQ translates to correct SQL"""
        
        nlq_engine = NaturalLanguageQueryEngine()
        
        # Test cases: (natural language, expected SQL pattern)
        test_cases = [
            (
                "What was total revenue last month?",
                "SELECT SUM(revenue) FROM sales WHERE month = LAST_MONTH"
            ),
            (
                "Show me top 10 customers by revenue",
                "SELECT customer, SUM(revenue) FROM sales GROUP BY customer ORDER BY revenue DESC LIMIT 10"
            ),
            (
                "Compare sales this year vs last year by region",
                "SELECT region, SUM(CASE WHEN year=THIS_YEAR), SUM(CASE WHEN year=LAST_YEAR)"
            )
        ]
        
        for nlq, expected_pattern in test_cases:
            # Generate SQL from natural language
            generated_sql = nlq_engine.translate(nlq)
            
            # Validate SQL contains expected keywords (simplified check)
            for keyword in expected_pattern.split():
                if keyword.isupper():  # SQL keywords
                    assert keyword in generated_sql.upper(), \
                        f"NLQ '{nlq}' missing keyword '{keyword}' in SQL: {generated_sql}"
            
            # Execute and validate returns data
            result = execute_query(generated_sql)
            assert len(result) > 0, f"NLQ '{nlq}' returned no data"
    ```

### Automated Insights

    ```python
    def test_automated_insights():
        """Validate AI-generated insights are accurate"""
        
        insights_engine = InsightsEngine()
        
        # Generate insights from sales data
        insights = insights_engine.analyze("sales_dashboard")
        
        # Validate insights generated
        assert len(insights) > 0, "No insights generated"
        
        # Validate insight types
        insight_types = {i['type'] for i in insights}
        expected_types = {'anomaly', 'trend', 'correlation'}
        
        assert insight_types & expected_types, \
            f"Missing expected insight types. Got: {insight_types}"
        
        # Validate anomaly detection
        anomaly_insights = [i for i in insights if i['type'] == 'anomaly']
        
        for anomaly in anomaly_insights:
            # Verify anomaly is real (statistical test)
            data = get_time_series_data(anomaly['metric'], anomaly['time_range'])
            
            mean = data.mean()
            std = data.std()
            anomaly_value = data.loc[anomaly['date']]
            
            z_score = abs((anomaly_value - mean) / std)
            
            # Anomaly should be at least 2 standard deviations
            assert z_score >= 2.0, \
                f"False anomaly detected: z-score={z_score:.2f} (threshold: 2.0)"
    ```

### Forecasting Validation

    ```python
    def test_forecasting_accuracy():
        """Validate ML forecasting models"""
        
        forecast_engine = ForecastEngine()
        
        # Use historical data to test forecast accuracy
        # Train on Jan-Oct, forecast Nov-Dec, compare to actual
        train_data = get_sales_data("2024-01-01", "2024-10-31")
        actual_data = get_sales_data("2024-11-01", "2024-12-31")
        
        # Generate forecast
        forecast = forecast_engine.predict(
            data=train_data,
            forecast_periods=60  # 60 days (Nov-Dec)
        )
        
        # Calculate forecast accuracy (MAPE: Mean Absolute Percentage Error)
        errors = []
        for i, actual_row in enumerate(actual_data):
            forecast_value = forecast[i]['value']
            actual_value = actual_row['sales']
            
            pct_error = abs(forecast_value - actual_value) / actual_value * 100
            errors.append(pct_error)
        
        mape = sum(errors) / len(errors)
        
        # Validate MAPE < 10% (industry standard for good forecast)
        assert mape < 10, \
            f"Forecast accuracy poor: MAPE={mape:.2f}% (threshold: 10%)"
    ```

---

## Self-Service Analytics Testing

### Report Builder Validation

    ```python
    def test_report_builder():
        """Validate non-technical users can create reports"""
        
        builder = ReportBuilder()
        
        # User creates report: Sales by Region
        report = builder.create_report(
            name="My Sales Report",
            data_source="sales_data",
            dimensions=["region"],
            metrics=["SUM(revenue)", "COUNT(orders)"],
            filters=[{"field": "order_date", "operator": ">=", "value": "2024-01-01"}]
        )
        
        # Validate report created
        assert report.id is not None, "Report not created"
        
        # Validate report executes
        data = report.run()
        assert len(data) > 0, "Report returned no data"
        
        # Validate data accuracy (compare to SQL)
        expected = execute_query("""
            SELECT region, SUM(revenue), COUNT(orders)
            FROM sales_data
            WHERE order_date >= '2024-01-01'
            GROUP BY region
        """)
        
        assert len(data) == len(expected), \
            f"Row count mismatch: Report={len(data)}, SQL={len(expected)}"
    ```

### Data Security in Self-Service

    ```python
    def test_row_level_security():
        """Validate users only see data they're authorized for"""
        
        # Create report as Sales Manager (sees all data)
        manager_report = create_report_as_user(
            user="sales_manager@example.com",
            report="Regional Sales"
        )
        manager_data = manager_report.run()
        
        # Create same report as Regional Manager (sees only their region)
        regional_report = create_report_as_user(
            user="us_manager@example.com",
            report="Regional Sales"
        )
        regional_data = regional_report.run()
        
        # Validate regional manager sees subset
        assert len(regional_data) < len(manager_data), \
            "Regional manager seeing more data than sales manager"
        
        # Validate regional manager only sees US
        regions = {row['region'] for row in regional_data}
        assert regions == {'US'}, \
            f"Regional manager seeing unauthorized regions: {regions}"
    ```

---

## Embedded Analytics Testing

### Dashboard Embedding

    ```python
    def test_embedded_dashboard():
        """Validate dashboard embeds correctly in external app"""
        
        from selenium import webdriver
        
        # Load external app with embedded dashboard
        driver = webdriver.Chrome()
        driver.get("https://app.example.com/sales-page")
        
        # Wait for dashboard to load
        dashboard_iframe = driver.find_element_by_id("embedded-dashboard")
        driver.switch_to.frame(dashboard_iframe)
        
        # Validate dashboard rendered
        revenue_metric = driver.find_element_by_id("total-revenue")
        assert revenue_metric.is_displayed(), "Revenue metric not visible"
        
        # Validate data matches standalone dashboard
        embedded_value = float(revenue_metric.text.replace('$', '').replace(',', ''))
        
        standalone_dashboard = load_dashboard("Sales Dashboard")
        standalone_value = standalone_dashboard.get_metric("Total Revenue")
        
        assert abs(embedded_value - standalone_value) < 0.01, \
            f"Embedded value ${embedded_value:,.2f} != standalone ${standalone_value:,.2f}"
    ```

### API Testing

    ```python
    def test_bi_api():
        """Validate BI data accessible via REST API"""
        
        import requests
        
        # Request sales data via API
        response = requests.get(
            "https://bi.example.com/api/v1/reports/sales",
            params={"start_date": "2024-01-01", "end_date": "2024-01-31"},
            headers={"Authorization": f"Bearer {api_token}"}
        )
        
        # Validate response
        assert response.status_code == 200, \
            f"API error: {response.status_code} - {response.text}"
        
        data = response.json()
        
        # Validate data structure
        assert "data" in data, "Missing 'data' field in API response"
        assert "metadata" in data, "Missing 'metadata' field"
        
        # Validate data accuracy (compare to direct query)
        api_total = sum([row['revenue'] for row in data['data']])
        
        db_total = execute_query("""
            SELECT SUM(revenue) FROM sales
            WHERE sale_date BETWEEN '2024-01-01' AND '2024-01-31'
        """)[0][0]
        
        assert abs(api_total - db_total) < 0.01, \
            f"API total ${api_total:,.2f} != DB total ${db_total:,.2f}"
    ```

---

## Interview Questions

### Basic (0-3 years)
**Q1**: What is the difference between a report and a dashboard?  
**A1**: **Report**: Static, detailed data (e.g., monthly sales PDF). **Dashboard**: Interactive, real-time, multiple visualizations (charts, KPIs). Reports for distribution, dashboards for exploration.

**Q2**: What is a KPI?  
**A2**: Key Performance Indicator = metric that measures success toward goal. Examples: Revenue (financial KPI), Customer Satisfaction Score (service KPI), Conversion Rate (marketing KPI). KPIs are actionable, measurable, time-bound.

### Advanced (4-8 years)
**Q3**: How do you test dashboard accuracy?  
**A3**: (1) **Reconciliation**: Compare dashboard totals to source database queries, (2) **Drill-down validation**: Ensure details sum to summary, (3) **Filter testing**: Verify filters update data correctly, (4) **Edge cases**: Test with zero data, missing dates, null values, (5) **Cross-dashboard**: Validate same metric shows same value across dashboards.

**Q4**: What is a semantic layer and why is it important?  
**A4**: **Semantic layer**: Business-friendly metadata layer (maps "Revenue" to `SUM(order_amount)`). **Importance**: (1) Consistency (everyone uses same definition), (2) Simplicity (users don't write SQL), (3) Governance (centralized business logic), (4) Reusability (metric defined once, used everywhere).

### Scenario (8-12 years)
**Q5**: Dashboard shows revenue dropping 50% overnight. Troubleshoot?  
**A5**: (1) **Data refresh**: Check if ETL ran (data stale?), (2) **Query logic**: Review query for recent changes (bug introduced?), (3) **Filter defaults**: Check if default filter changed (now filtering out data), (4) **Source data**: Validate source system has data (outage?), (5) **Timezone**: Check if timezone issue (yesterday's data not loaded yet), (6) **User error**: Confirm user didn't apply restrictive filter.

### Architect (12+ years)
**Q6**: Design BI testing strategy for enterprise (500 dashboards, 10K users)?  
**A6**: (1) **Golden dataset**: 100 critical dashboards tested daily (automated), (2) **Tiered testing**: Critical (daily), standard (weekly), low-priority (monthly), (3) **Automated reconciliation**: Compare all metrics to source hourly, alert on >1% variance, (4) **Visual regression**: Screenshot comparison weekly (detect UI breaks), (5) **Performance monitoring**: Track dashboard load times, alert if p95 >5 sec, (6) **User acceptance**: Sample 5% users monthly, survey satisfaction, (7) **A/B testing**: New features rolled out to 10% users first, (8) **Governance**: All dashboards cataloged (owner, refresh schedule, SLA), (9) **Compliance**: Row-level security tested quarterly, audit logs reviewed, (10) **Disaster recovery**: Backup dashboards weekly, test restore monthly.

---

## Frequently Asked Questions

**Q1**: What is OLAP and how does it relate to BI?  
**A1**: **OLAP** (Online Analytical Processing) = multidimensional analysis (slice/dice data by dimensions). OLAP cubes pre-aggregate data for fast queries. BI tools query OLAP cubes. **Test**: Validate cube aggregations match source data.

**Q2**: How to test calculated metrics?  
**A2**: (1) **Unit test formula**: Test calculation logic independently (e.g., profit = revenue - cost), (2) **Sample validation**: Pick 10 records, manually calculate, compare to dashboard, (3) **Edge cases**: Test with zero revenue, negative cost, null values, (4) **Cross-check**: Validate against external source (Excel, accounting system).

**Q3**: What is data latency in BI and how to test?  
**A3**: **Data latency** = time from event to dashboard. Example: Sale at 10:00 AM, shows in dashboard at 10:05 AM (5 min latency). **Test**: (1) Insert record in source, (2) Wait for ETL, (3) Refresh dashboard, (4) Validate record appears, (5) Measure time. Target: <15 min for near-real-time.

**Q4**: How to test drill-down functionality?  
**A4**: (1) **Hierarchy validation**: Verify drill path exists (Region → State → City), (2) **Aggregation**: Ensure child levels sum to parent, (3) **Filters**: Validate drilling applies filters correctly (drilling US shows only US states), (4) **Navigation**: Test back button returns to parent level.

**Q5**: What is a data mart and how does it differ from a data warehouse?  
**A5**: **Data Warehouse** = enterprise-wide, all subjects (sales, HR, finance). **Data Mart** = subject-specific subset (Sales Mart for sales team). Marts are smaller, faster, tailored to department needs. **Test**: Validate mart data matches corresponding DWH subject area.

**Q6**: How to test BI caching?  
**A6**: (1) **First load**: Measure query time (no cache, slow), (2) **Second load**: Measure query time (cached, fast), validate <1 sec, (3) **Cache invalidation**: Update source data, verify cache refreshes, (4) **Expiration**: Wait for cache TTL, validate refresh occurs.

**Q7**: What is a star schema and why is it used in BI?  
**A7**: **Star schema** = fact table (center) + dimension tables (points). Optimized for BI queries (denormalized, fast joins, simple). **Test**: Validate fact-dimension joins, check grain (one row per transaction), verify measures additive.

**Q8**: How to test parameterized reports?  
**A8**: (1) **Valid params**: Test with expected values (date range, region), (2) **Invalid params**: Test with wrong types (text for date), validate error handling, (3) **Edge cases**: Empty range, future dates, (4) **Default values**: Verify defaults applied when params omitted.

**Q9**: What is data storytelling in BI?  
**A9**: Using visualizations + narrative to communicate insights. Example: Dashboard shows sales dropping → annotation explains "COVID-19 impact, Mar 2020". **Test**: Validate annotations appear, narrative matches data, insights actionable.

**Q10**: How to validate forecast confidence intervals?  
**A10**: (1) **Historical accuracy**: Backtest (forecast past, compare to actual), (2) **Interval width**: Wider interval = less confident (validate width reasonable, e.g., ±10%), (3) **Coverage**: 95% CI should contain actual 95% of time (test on historical data).

**Q11**: What is a metric tree?  
**A11**: Hierarchical breakdown of metric. Example: Revenue = (Traffic × Conversion Rate) × Average Order Value. **Test**: Validate components multiply/add correctly, leaf metrics reconcile to source data.

**Q12**: How to test real-time dashboards?  
**A12**: (1) **Latency**: Insert event, measure time to appear (target: <5 sec), (2) **Correctness**: Validate event data accurate, (3) **Load**: Simulate 1000 events/sec, ensure dashboard updates, (4) **Consistency**: Refresh multiple times, validate no duplicates/missing events.

**Q13**: What is a BI governance model?  
**A13**: Policies for dashboard creation, ownership, access. **Components**: (1) Approval process (new dashboards reviewed), (2) Naming conventions, (3) Data source certification (trusted vs. unverified), (4) Access controls (RBAC), (5) Sunset policy (unused dashboards archived). **Test**: Validate policies enforced (unapproved dashboard blocked, naming validated).

**Q14**: How to test mobile BI apps?  
**A14**: (1) **Responsive design**: Test on multiple screen sizes (phone, tablet), (2) **Touch interactions**: Validate swipe, pinch-to-zoom work, (3) **Offline mode**: Test dashboard caching (works without network), (4) **Performance**: Validate load time <3 sec on 4G.

**Q15**: What is a KPI card and how to test it?  
**A15**: **KPI card** = single metric display (Total Revenue: $1.2M). **Test**: (1) **Value accuracy**: Compare to database, (2) **Trend indicator**: Validate up/down arrow correct (compare to previous period), (3) **Formatting**: Check $ sign, thousands separator, decimals, (4) **Sparkline**: If included, validate mini-chart accurate.

**Q16**: How to test BI alerts?  
**A16**: (1) **Trigger condition**: Set threshold (revenue <$10K), validate alert fires when breached, (2) **Delivery**: Confirm email/SMS received, (3) **Frequency**: Test only one alert per hour (not spam), (4) **False positives**: Validate doesn't fire when condition not met.

**Q17**: What is a BI data refresh schedule and how to test?  
**A17**: **Refresh schedule** = how often dashboard data updates (hourly, daily). **Test**: (1) **Execution**: Verify refresh job runs on schedule (cron job logs), (2) **Completion**: Check refresh completes within SLA (2-hour window), (3) **Data freshness**: Query dashboard, validate latest data present.

**Q18**: How to test cross-filtering in dashboards?  
**A18**: **Cross-filtering** = selecting one chart filters others. **Test**: (1) Click bar in chart A (e.g., "US" region), (2) Validate chart B updates (shows only US data), (3) Validate chart C updates, (4) Validate clearing filter restores original state, (5) Test multiple filters (US + Q1).

**Q19**: What is a BI data lineage and why test it?  
**A19**: **Data lineage** = trace metric from dashboard to source table. Example: "Revenue" metric → SQL query → fact_sales table → orders source system. **Test**: (1) Document lineage, (2) Validate each transformation, (3) Compare final metric to source, (4) Update lineage when logic changes.

**Q20**: How to test BI performance with large datasets (1B rows)?  
**A20**: (1) **Indexing**: Validate indexes on date, region (fast filters), (2) **Aggregation**: Pre-aggregate to daily/monthly (not query all rows), (3) **Partitioning**: Partition by date (query only relevant partitions), (4) **Caching**: Cache frequent queries (30-min TTL), (5) **Load test**: 100 concurrent users, validate p95 <5 sec.

---

## Actionable Checklists

### BI Dashboard Testing Checklist
- [ ] Data accuracy validated (reconcile to source)
- [ ] Aggregations correct (SUM, AVG, COUNT)
- [ ] Filters work correctly (update charts)
- [ ] Drill-down validated (details sum to summary)
- [ ] Visualizations render correctly (chart types, axes)
- [ ] Load time <5 sec (p95)
- [ ] Mobile responsive (test on phone/tablet)
- [ ] Cross-filtering works (selecting one chart filters others)
- [ ] Row-level security (users see only authorized data)
- [ ] Visual regression (no unexpected UI changes)

### BI Performance Testing Checklist
- [ ] Dashboard load time measured (p50, p95)
- [ ] Query performance tested (<5 sec)
- [ ] Concurrent users tested (100+ users)
- [ ] Caching validated (second load faster)
- [ ] Large dataset performance (1B rows, <5 sec)
- [ ] Real-time latency (<5 sec event to dashboard)
- [ ] API performance (<1 sec response)
- [ ] Database indexes validated (query plans optimized)

### AI-Powered BI Testing Checklist
- [ ] Natural language queries translate correctly
- [ ] Automated insights are accurate (anomalies real)
- [ ] Forecasting accuracy validated (MAPE <10%)
- [ ] Recommendations relevant (A/B tested)
- [ ] Explanations provided (why insight generated)
- [ ] Confidence scores calibrated (90% confident = 90% correct)
- [ ] Bias tested (insights fair across demographics)

---

## References

### Books
- **The Data Warehouse Toolkit** (Kimball, Ross): Star schema for BI
- **Storytelling with Data** (Cole Nussbaumer Knaflic): Visualization best practices
- **Information Dashboard Design** (Stephen Few): Dashboard design principles

### Standards
- **ISO/IEC 25012**: Data Quality Model (applies to BI)
- **TDWI**: BI best practices and benchmarks

### Tools
- **Tableau**: Leading BI platform
- **Power BI**: Microsoft BI platform
- **Looker**: Google Cloud BI platform
- **Qlik**: Associative analytics platform
- **Sisense**: Embedded analytics platform

### Courses
- **Tableau Desktop Specialist**: Official Tableau certification
- **Microsoft Power BI Data Analyst**: Official Power BI certification

---

**Core References**: Platform-agnostic BI/Analytics concepts  
**Stack Deltas**: Platform-specific BI tools (Tableau, Power BI, Looker) in stack files

**Previous**: [13_Data_Governance_QA_Perspective.md](./13_Data_Governance_QA_Perspective.md)  
**Next**: [15_Data_Security_QA_Perspective.md](./15_Data_Security_QA_Perspective.md)  
**Up**: [Master Index](../00_MASTER_INDEX.md)