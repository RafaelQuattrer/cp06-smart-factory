// Asserções avaliadas na compilação, usando o mesmo cabeçalho do firmware.
// Uma regressão no limite impede a compilação, sem depender de hardware.
#include "../firmware/smart_factory/edge_logic.h"
static_assert(!isAlert(30.0f), "30 C precisa ser NORMAL");
static_assert(!isAlert(35.0f), "35 C precisa ser NORMAL");
static_assert(isAlert(35.01f), "Acima de 35 C precisa ser ALERTA");
static_assert(isAlert(36.0f), "36 C precisa ser ALERTA");
static_assert(!isAlert(-40.0f), "Limite inferior do DHT22");
static_assert(isAlert(80.0f), "Limite superior do DHT22");
int main() { return 0; }
