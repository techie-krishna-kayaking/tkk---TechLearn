# ML Release Gate

Validate training/inference schema, point-in-time features, label quality, baseline metric, calibration/threshold, critical slices, robustness and latency. Compare a challenger against current champion on frozen data. Promotion requires all mandatory gates to pass; a global metric increase cannot waive a critical slice/safety regression.
