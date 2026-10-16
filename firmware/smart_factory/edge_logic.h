#pragma once
// Ponto único da regra local: exatamente 35 °C continua NORMAL.
inline constexpr bool isAlert(float temperature) { return temperature > 35.0f; }
